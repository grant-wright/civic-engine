import asyncio
import uuid
from pathlib import Path

import socketio
from fastapi import FastAPI
import game.store as store
from game.scenarios import scenario_fresh_game
from game.state import GameEvent, GameEventType, GameStatus, PlayerType, ReportStatus
from game.rules import Turn, Election
from api.admin import router as admin_router
from api.health import router as health_router

# ─── Socket.IO + FastAPI setup ────────────────────────────────────────────────

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
store._sio = sio  # expose to broadcast_game_state() in store.py

fastapi_app = FastAPI(title="Civic Engine", version="0.1.0")
fastapi_app.include_router(admin_router)
fastapi_app.include_router(health_router)

# Mount FastAPI under socket.io so both share one ASGI server on port 8000.
# uvicorn command stays identical: `uvicorn main:app --reload`
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)


# ─── Game state init ──────────────────────────────────────────────────────────

store.game_state = scenario_fresh_game()

_default_map_path = Path(__file__).parent / "saves" / "map_default.json"
if _default_map_path.exists():
    from game.state import CityMap
    _city_map = CityMap.model_validate_json(_default_map_path.read_text())
    store.game_state.city_map = _city_map
    if _city_map.factions:
        store.game_state.factions = _city_map.factions
    for _player in store.game_state.players.values():
        _match = next((c for c in _city_map.councillors if c.role == _player.role), None)
        if _match:
            _player.councillor = _match


# ─── Turn content helper ──────────────────────────────────────────────────────

async def _start_new_turn(gs) -> None:
    """Generate Claude reports for the new turn and queue AI player decisions."""
    if gs.status != GameStatus.IN_GAME:
        return
    from game.reports import schedule_reports
    await schedule_reports(gs)
    await store.broadcast_game_state()
    from claude.ai_player import make_ai_decision
    for player in gs.players.values():
        if player.player_type != PlayerType.AI:
            continue
        for report in gs.pending_reports.get(player.player_id, []):
            if report.status == ReportStatus.PENDING:
                store.fire_task(make_ai_decision(player, report, gs, store.broadcast_game_state))


# ─── Socket.IO event handlers ─────────────────────────────────────────────────

@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None):
    pass  # actual registration happens on the 'register' event


@sio.event
async def register(sid: str, data: dict):
    """
    Payload: {client_type, player_id, role, session_id}
    On reconnect (known session_id): restore session to new sid.
    Always emits full game state to just this client.
    """
    if store.game_state is None:
        return

    session_id = data.get("session_id", "")

    # Check if this is a reconnect from a known session
    existing_sid = next(
        (s for s, info in store.connected_clients.items()
         if info.get("session_id") == session_id and session_id),
        None,
    )
    if existing_sid and existing_sid != sid:
        # Port the client record to the new sid, drop the stale one
        store.connected_clients[sid] = store.connected_clients.pop(existing_sid)
    else:
        store.connected_clients[sid] = {
            "client_type": data.get("client_type", "unknown"),
            "player_id": data.get("player_id"),
            "role": data.get("role"),
            "session_id": session_id,
        }

    # Emit full state to just this client — everyone else already has it
    payload = store.game_state.model_dump(mode="json")
    await sio.emit("game_state_update", payload, to=sid)


@sio.event
async def player_action(sid: str, data: dict):
    """
    Payload: {player_id, action_type, target_type, target_id, option_id}
    Schedules the chosen option's effects and marks the report decided.
    """
    if store.game_state is None:
        return

    gs = store.game_state
    player_id = data.get("player_id", "")
    target_id = data.get("target_id", "")
    option_id = data.get("option_id", "")

    # Apply chosen option's effects; graceful no-op if report/option not found
    chosen_label = option_id  # fallback to raw id if not resolved
    report_title = target_id
    for report in gs.pending_reports.get(player_id, []):
        if report.report_id == target_id:
            report_title = report.title
            for opt in report.options:
                if opt.option_id == option_id:
                    chosen_label = opt.label
                    for e in opt.effects:
                        gs.pending_effects.append((gs.turn + e.delay_turns, e))
                    report.status = ReportStatus.DECIDED
                    report.decision = option_id
            break

    player = gs.players.get(player_id)
    actor_name = player.councillor.name if player else (player_id or "unknown")

    event = GameEvent(
        event_id=str(uuid.uuid4()),
        event_type=GameEventType.MAJOR_DECISION,
        turn=gs.turn,
        cycle=gs.cycle,
        description=f"{actor_name} chose '{chosen_label}' on '{report_title}'",
        player_id=player_id,
        data=data,
    )
    gs.event_log.append(event)

    await store.broadcast_game_state()


@sio.event
async def voice_command(sid: str, data: dict):
    """Stub — logs and ignores. Full implementation in step 11."""
    pass


@sio.event
async def end_turn(sid: str, data: dict | None = None):
    """
    Payload: {player_id}  — sent by the frontend when the turn timer fires.
    Advances the engine: applies pending effects, ticks construction, updates metrics,
    checks cycle end, then increments turn.
    """
    if store.game_state is None:
        return

    from game.engine import advance_turn

    advance_turn(store.game_state)
    await store.broadcast_game_state()
    store.fire_task(_start_new_turn(store.game_state))


@sio.event
async def council_extension(sid: str, data: dict | None = None):
    """
    Payload: {player_id}
    Spends one extension: decrement counter, add 30s to turn limit, nudge polling down.
    """
    if store.game_state is None:
        return

    gs = store.game_state
    if gs.council_extensions_remaining <= 0:
        return

    gs.council_extensions_remaining -= 1
    gs.turn_time_limit += Turn.extension_seconds
    gs.metrics.election_polling = max(0.0, gs.metrics.election_polling - Election.extension_polling_cost)
    gs.current_turn_extended = True

    payload = data or {}
    event = GameEvent(
        event_id=str(uuid.uuid4()),
        event_type=GameEventType.COUNCIL_EXTENSION,
        turn=gs.turn,
        cycle=gs.cycle,
        description=(
            f"{payload.get('player_id', 'a councillor')} called a council extension. "
            f"{gs.council_extensions_remaining} remaining."
        ),
        player_id=payload.get("player_id"),
        data={"remaining": gs.council_extensions_remaining},
    )
    gs.event_log.append(event)

    await store.broadcast_game_state()


@sio.event
async def vote_cast(sid: str, data: dict):
    """
    Payload: {player_id, vote_id, option_id}
    Records the player's vote. Resolves and applies effects when all players have voted.
    """
    if store.game_state is None:
        return

    gs = store.game_state
    vote = gs.pending_vote
    if vote is None or vote.vote_id != data.get("vote_id"):
        return

    player_id = data.get("player_id", "")
    option_id = data.get("option_id", "")
    if player_id and option_id:
        vote.votes[player_id] = option_id

    # Resolve once all players have submitted
    if len(vote.votes) >= len(gs.players):
        counts: dict[str, int] = {}
        for oid in vote.votes.values():
            counts[oid] = counts.get(oid, 0) + 1
        winning_id = max(counts, key=lambda k: counts[k])

        top = counts[winning_id]
        vote.mayor_tiebreaker = sum(1 for v in counts.values() if v == top) > 1

        for opt in vote.options:
            if opt.option_id == winning_id:
                for e in opt.effects:
                    gs.pending_effects.append((gs.turn + e.delay_turns, e))
                break

        vote.status = "resolved"
        vote.result = winning_id
        gs.pending_vote = None

    await store.broadcast_game_state()


@sio.event
async def new_game(sid: str, data: dict):
    """
    Payload: {game_length}
    Resets to a fresh game state, preserving the generated city map and councillors.
    Connected clients stay registered — they are the same people starting a new game.
    """
    gs = scenario_fresh_game()

    # Carry forward the generated city map so we don't lose it on reset
    if store.game_state is not None:
        gs.city_map = store.game_state.city_map
        gs.factions = store.game_state.factions
        for player in gs.players.values():
            match = next(
                (c for c in gs.city_map.councillors if c.role == player.role), None
            )
            if match:
                player.councillor = match

    game_length = data.get("game_length")
    if isinstance(game_length, int) and game_length in (4, 5, 6):
        gs.game_length = game_length

    gs.status = GameStatus.IN_GAME
    store.game_state = gs

    await store.broadcast_game_state()
    store.fire_task(_start_new_turn(gs))


@sio.event
async def disconnect(sid: str):
    """Log connection loss and remove client from registry."""
    client = store.connected_clients.pop(sid, None)
    if store.game_state is None or client is None:
        return

    event = GameEvent(
        event_id=str(uuid.uuid4()),
        event_type=GameEventType.CONNECTION_LOST,
        turn=store.game_state.turn,
        cycle=store.game_state.cycle,
        description=f"{client.get('player_id', 'a client')} disconnected.",
        player_id=client.get("player_id"),
        data={"sid": sid},
    )
    store.game_state.event_log.append(event)


# ─── HTTP root ────────────────────────────────────────────────────────────────

@fastapi_app.get("/")
async def root():
    return {"message": "Civic Engine API is running"}
