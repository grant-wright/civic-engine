"""
claude/citizens.py — Faction reaction generation via Claude tool use.
Fires at turn end for factions whose sensitivities overlap with turn events.
"""
import game.store as store
from game.state import Faction, FactionReaction, GameState
from claude.client import MODEL, safe_claude_call, record_usage

_FACTION_GM_CONTEXT = """You are the game master for Civic Engine, a cooperative Victorian city council game set in the late 1780s. Generate a brief faction reaction to this turn's events from the faction's unique perspective. Be vivid and period-appropriate. Happiness delta: -10 (furious) to +10 (delighted), 0 if nothing material affected them."""

_FACTION_REACTION_TOOL = {
    "name": "faction_reaction",
    "description": "Express the faction's reaction to this turn's events.",
    "input_schema": {
        "type": "object",
        "properties": {
            "reaction_text": {
                "type": "string",
                "description": "1-2 sentences in the faction's distinctive voice. Period-appropriate Victorian tone.",
            },
            "happiness_delta": {
                "type": "number",
                "description": "Change in faction happiness: -10 to +10. Use 0 if nothing material happened.",
            },
            "severity": {
                "type": "string",
                "enum": ["minor", "moderate", "major"],
                "description": "minor = delta ≤3, moderate = 4-6, major = 7+",
            },
        },
        "required": ["reaction_text", "happiness_delta", "severity"],
    },
}


async def generate_faction_reaction(
    faction: Faction,
    turn_summary: str,
    gs: GameState,
) -> FactionReaction | None:
    kwargs = {
        "model": MODEL,
        "system": [
            {
                "type": "text",
                "text": _FACTION_GM_CONTEXT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": faction.profile,
            },
        ],
        "messages": [
            {
                "role": "user",
                "content": (
                    f"This turn's events:\n{turn_summary}\n\n"
                    f"Game state: {gs.to_context_summary()}"
                ),
            }
        ],
        "tools": [_FACTION_REACTION_TOOL],
        "tool_choice": {"type": "any"},
        "max_tokens": 400,
    }

    try:
        response = await safe_claude_call(kwargs, fallback_tokens=600, call_type="faction_reaction")
        record_usage("faction_reaction", response, turn=gs.turn, cycle=gs.cycle)
    except Exception as exc:
        store.log_dev(
            "faction_reaction_error",
            f"Claude call failed for faction '{faction.faction_id}': {exc}",
            turn=gs.turn,
            cycle=gs.cycle,
            faction_id=faction.faction_id,
        )
        return None

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use is None:
        store.log_dev(
            "faction_reaction_error",
            f"No tool_use block in response for faction '{faction.faction_id}'",
            turn=gs.turn,
            cycle=gs.cycle,
            faction_id=faction.faction_id,
        )
        return None

    d = tool_use.input
    return FactionReaction(
        faction_id=faction.faction_id,
        reaction_text=str(d["reaction_text"]),
        happiness_delta=float(d["happiness_delta"]),
        triggered_by=turn_summary[:200],
        severity=d["severity"],
        display_on=["p_transport", "p_finance", "p_infrastructure"],
    )
