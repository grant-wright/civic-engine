"""
claude/ai_player.py — Cooperative AI councillor decision-making.
Finance and Infrastructure players decide during the turn window (fire-and-forget).
"""
import asyncio
import uuid

from game.state import GameState, Player, Report, ReportStatus, GameEvent, GameEventType
from claude.client import MODEL, safe_claude_call, record_usage

_AI_SYSTEM = """You are a cooperative AI councillor in a Victorian city council game. You work WITH the human Transport Councillor — you are on the same team.

Priorities (in order):
1. Keep election_polling above 40 — game over if it falls below
2. Advance canal construction (higher canal efficiency = closer to victory)
3. Preserve budget reserves
4. Prefer low or medium risk unless metrics are in crisis

Choose the option that best serves the council. One sentence of reasoning only."""

_AI_DECISION_TOOL = {
    "name": "choose_option",
    "description": "Choose one option from the report.",
    "input_schema": {
        "type": "object",
        "properties": {
            "option_id": {"type": "string"},
            "reasoning": {"type": "string", "description": "One sentence rationale."},
        },
        "required": ["option_id", "reasoning"],
    },
}


async def make_ai_decision(
    player: Player,
    report: Report,
    gs: GameState,
    broadcast_fn,
) -> None:
    try:
        await asyncio.sleep(2)  # simulate deliberation before deciding

        options_text = "\n".join(
            f"  [{o.risk_level.value}] option_id={o.option_id}: {o.label} — {o.description}"
            for o in report.options
        )
        kwargs = {
            "model": MODEL,
            "system": [
                {
                    "type": "text",
                    "text": _AI_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Report: {report.title}\n{report.description}\n\n"
                        f"Options:\n{options_text}\n\n"
                        f"Current state: {gs.to_context_summary()}"
                    ),
                }
            ],
            "tools": [_AI_DECISION_TOOL],
            "tool_choice": {"type": "any"},
            "max_tokens": 300,
        }

        chosen_opt = report.options[0]
        reasoning = "default choice"
        try:
            response = await safe_claude_call(kwargs, fallback_tokens=500, call_type="ai_decision")
            record_usage("ai_decision", response, turn=gs.turn, cycle=gs.cycle)
            tool_use = next((b for b in response.content if b.type == "tool_use"), None)
            if tool_use:
                chosen_id = tool_use.input.get("option_id", "")
                reasoning = tool_use.input.get("reasoning", "")
                match = next((o for o in report.options if o.option_id == chosen_id), None)
                if match:
                    chosen_opt = match
        except Exception:
            pass

        for e in chosen_opt.effects:
            gs.pending_effects.append((gs.turn + e.delay_turns, e))
        report.status = ReportStatus.DECIDED
        report.decision = chosen_opt.option_id

        gs.event_log.append(GameEvent(
            event_id=str(uuid.uuid4()),
            event_type=GameEventType.MAJOR_DECISION,
            turn=gs.turn,
            cycle=gs.cycle,
            description=(
                f"🤖 {player.role.value.capitalize()} chose "
                f"'{chosen_opt.label}': {reasoning}"
            ),
            player_id=player.player_id,
        ))
        await broadcast_fn()

    except Exception as exc:
        gs.event_log.append(GameEvent(
            event_id=str(uuid.uuid4()),
            event_type=GameEventType.CLAUDE_TIMEOUT,
            turn=gs.turn,
            cycle=gs.cycle,
            description=f"🤖 {player.role.value.capitalize()} AI decision failed: {exc}",
            player_id=player.player_id,
        ))
        try:
            await broadcast_fn()
        except Exception:
            pass
