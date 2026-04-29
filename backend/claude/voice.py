"""
claude/voice.py — Voice command parsing via Claude tool use.
Maps a free-text transcript to a structured game action (choose/defer/escalate/delegate).
"""
import game.store as store
from game.state import GameState, ParsedCommand, TargetType
from claude.client import MODEL, safe_claude_call, record_usage

_VOICE_SYSTEM = """You are a voice command parser for a Victorian city council game. Map the player's spoken words to one of the available actions listed. Be generous in interpretation — "first option", "number one", "the bold one" should all resolve to the appropriate option. If the intent is genuinely ambiguous, use action_type "unclear" and write a short clarification_prompt."""

_DISPATCH_TOOL = {
    "name": "dispatch_command",
    "description": "Parse the voice transcript into a specific game action.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action_type": {
                "type": "string",
                "enum": ["choose_option", "delegate", "defer", "escalate", "unclear"],
            },
            "option_id": {
                "type": "string",
                "description": "The option_id to select (only when action_type is choose_option).",
            },
            "agent_id": {
                "type": "string",
                "description": "The agent_id to delegate to (only when action_type is delegate).",
            },
            "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "How confident you are in this mapping.",
            },
            "clarification_prompt": {
                "type": "string",
                "description": "Short question to ask the player (only when action_type is unclear).",
            },
        },
        "required": ["action_type", "confidence"],
    },
}


async def parse_voice_command(
    transcript: str,
    player_id: str,
    report_id: str | None,
    gs: GameState,
) -> ParsedCommand | None:
    player = gs.players.get(player_id)
    if player is None:
        return None

    # Find the currently open report
    report = None
    if report_id:
        for r in gs.pending_reports.get(player_id, []):
            if r.report_id == report_id:
                report = r
                break

    # Build available-actions context
    action_lines: list[str] = []
    if report:
        for i, opt in enumerate(report.options, 1):
            action_lines.append(
                f"  choose_option #{i}: option_id={opt.option_id!r}  label={opt.label!r}"
            )
        action_lines.append("  defer: defer this report to a later turn")
        action_lines.append("  escalate: flag for full council vote")
    for agent in player.agents:
        action_lines.append(
            f"  delegate: to {agent.name!r}  agent_id={agent.agent_id!r}"
        )

    if not action_lines:
        return None

    report_context = (
        f"Current report: {report.title}\n{report.description}\n\n"
        if report else "No report currently selected.\n\n"
    )

    kwargs = {
        "model": MODEL,
        "system": [
            {
                "type": "text",
                "text": _VOICE_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": (
                    f"{report_context}"
                    f"Available actions:\n" + "\n".join(action_lines) +
                    f"\n\nPlayer said: \"{transcript}\""
                ),
            }
        ],
        "tools": [_DISPATCH_TOOL],
        "tool_choice": {"type": "any"},
        "max_tokens": 200,
    }

    try:
        response = await safe_claude_call(kwargs, fallback_tokens=400, call_type="voice_parse")
        record_usage("voice_parse", response, turn=gs.turn, cycle=gs.cycle)
    except Exception as exc:
        store.log_dev(
            "voice_parse_error",
            f"Claude call failed: {exc}",
            turn=gs.turn,
            cycle=gs.cycle,
            player_id=player_id,
            transcript=transcript,
        )
        return None

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use is None:
        store.log_dev(
            "voice_parse_error",
            "No tool_use block in voice parse response",
            turn=gs.turn,
            cycle=gs.cycle,
            player_id=player_id,
            transcript=transcript,
        )
        return None

    d = tool_use.input
    action_type = d.get("action_type", "unclear")

    parameters: dict = {}
    if d.get("option_id"):
        parameters["option_id"] = d["option_id"]
    if d.get("agent_id"):
        parameters["agent_id"] = d["agent_id"]

    return ParsedCommand(
        action_type=action_type,
        target_type=TargetType.REPORT if report_id else None,
        target_id=report_id,
        parameters=parameters,
        confidence=float(d.get("confidence", 0.5)),
        clarification_needed=(action_type == "unclear"),
        clarification_prompt=d.get("clarification_prompt"),
    )
