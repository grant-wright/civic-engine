"""
claude/events.py — Report generation via Claude tool use.
System and domain context are prompt-cached; only the per-turn trigger changes.
"""
import uuid
from game.state import (
    GameState, Report, ReportOption, ReportType, ReportStatus, RiskLevel,
    Effect, EffectType, TargetType, CouncilRole,
)
from claude.client import MODEL, safe_claude_call, record_usage

GAME_MASTER_PROMPT = """You are the game master for Civic Engine, a cooperative steampunk council game set in a Victorian-era British city in the late 1780s. Three councillors — Finance, Infrastructure, and Transport — must complete the canal network before the Railway Party gains dominance.

City metrics to know:
- Road Rage Index (0–100): street chaos from horse traffic and freight. Crisis above 70.
- Canal Efficiency Index (0–100): rises as canal segments connect. Tiers: Bronze/Silver/Gold.
- Aesthetic Index (0–100): civic pride, heritage architecture, public amenity spaces.
- Election Polling (0–100): council survival — dissolution if it falls below 40.
- Horse Pollution (0–100): rises when canal freight is low. Public health crisis above 70.

Generate vivid, historically-grounded reports with 2–3 options offering genuine trade-offs. Use period-appropriate 1780s British tone. Reference the current conditions you are given. Make each option consequential."""

STATIC_DOMAIN_CONTEXT = {
    "finance": """You are generating a report for the Finance Councillor.

Finance concerns: department budgets and tax revenue, economy_index scaling cycle income, Merchant Consortium relations, canal bond investment risk, heritage property values.

Typical Finance reports: budget crises, merchant petitions, canal bond issuance, construction cost overruns, trade route negotiations, railway speculation warnings, insurance disputes.""",

    "infrastructure": """You are generating a report for the Infrastructure Councillor.

Infrastructure concerns: waypoint construction (aqueducts 7 turns, tunnels 9, locks 5, cuttings/embankments 4), Road Rage from construction disruption, worker safety and Canal Workers' Guild relations, material procurement (stone, timber, iron), heritage buildings threatened by construction routes.

Typical Infrastructure reports: construction setbacks, material shortages, worker petitions, road collapse from heavy freight, heritage building threats, engineering dilemmas (speed vs quality vs cost).""",

    "transport": """You are generating a report for the Transport Councillor.

Transport concerns: canal freight percentage (grow this — more canal freight = better efficiency), horse pollution (rises when canal freight is low, crisis above 70), Railway Party lobbying, Carter's Association relations (road hauliers who resist canal dominance), towpath and wharf access.

Typical Transport reports: carter strikes, horse disposal crises, railway party lobbying events, towpath enclosures, freight incentive schemes, wharf congestion, canal timetable disputes.""",
}

_EFFECT_TARGET_TYPES: dict[str, TargetType] = {
    "metric_delta":         TargetType.METRIC,
    "budget_delta":         TargetType.METRIC,
    "faction_mood":         TargetType.FACTION,
    "railway_influence":    TargetType.RAILWAY_PARTY,
    "canalparty_influence": TargetType.CANAL_PARTY,
    "aesthetic_delta":      TargetType.METRIC,
    "economy_delta":        TargetType.ECONOMY,
    "income_delta":         TargetType.CYCLE_INCOME,
}

_REPORT_TOOL = {
    "name": "generate_report",
    "description": "Generate a civic council report with decision options.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short dramatic title (max 60 chars)",
            },
            "description": {
                "type": "string",
                "description": "2-3 sentences, period-appropriate Victorian tone",
            },
            "urgency": {
                "type": "boolean",
                "description": "True if this requires immediate attention this turn",
            },
            "options": {
                "type": "array",
                "minItems": 2,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "label":       {"type": "string"},
                        "description": {"type": "string"},
                        "risk_level":  {"type": "string", "enum": ["low", "medium", "high"]},
                        "min_skill_level": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 5,
                            "description": "Councillor skill required to unlock this option",
                        },
                        "effects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "effect_type": {
                                        "type": "string",
                                        "enum": [
                                            "metric_delta", "budget_delta", "faction_mood",
                                            "aesthetic_delta", "economy_delta", "income_delta",
                                            "railway_influence", "canalparty_influence",
                                        ],
                                    },
                                    "target_id": {
                                        "type": "string",
                                        "description": (
                                            "metric_delta: field on Metrics e.g. road_rage_index, "
                                            "horse_pollution, canal_freight_pct, election_polling. "
                                            "budget_delta: finance | infrastructure | transport. "
                                            "faction_mood: faction_id string. "
                                            "aesthetic_delta: 'aesthetic_index'. "
                                            "economy_delta: 'economy_index'. "
                                            "income_delta: 'cycle_income'. "
                                            "railway_influence or canalparty_influence: 'influence'."
                                        ),
                                    },
                                    "value": {
                                        "type": "number",
                                        "description": "Positive = increase, negative = decrease",
                                    },
                                    "delay_turns": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 5,
                                        "description": "Turns before this effect applies (0 = immediate)",
                                    },
                                    "description": {"type": "string"},
                                },
                                "required": [
                                    "effect_type", "target_id", "value",
                                    "delay_turns", "description",
                                ],
                            },
                        },
                    },
                    "required": ["label", "description", "risk_level", "min_skill_level", "effects"],
                },
            },
        },
        "required": ["title", "description", "urgency", "options"],
    },
}


async def generate_report(
    domain: str,
    gs: GameState,
    trigger: str,
    player_id: str,
) -> Report | None:
    kwargs = {
        "model": MODEL,
        "system": [
            {
                "type": "text",
                "text": GAME_MASTER_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": STATIC_DOMAIN_CONTEXT[domain],
                "cache_control": {"type": "ephemeral"},
            },
        ],
        "messages": [
            {
                "role": "user",
                "content": f"Game state: {gs.to_context_summary()}\n\nTrigger: {trigger}",
            },
        ],
        "tools": [_REPORT_TOOL],
        "tool_choice": {"type": "any"},
        "max_tokens": 3000,
    }

    try:
        response = await safe_claude_call(kwargs, fallback_tokens=4000, call_type="report_gen")
        record_usage("report_gen", response, turn=gs.turn, cycle=gs.cycle)
    except Exception:
        return None

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use is None:
        return None

    d = tool_use.input
    options = []
    for o in d.get("options", []):
        effects = []
        for e in o.get("effects", []):
            et = e["effect_type"]
            effects.append(Effect(
                effect_type=EffectType(et),
                target_type=_EFFECT_TARGET_TYPES.get(et, TargetType.METRIC),
                target_id=str(e["target_id"]),
                value=float(e["value"]),
                delay_turns=int(e.get("delay_turns", 0)),
                description=str(e.get("description", "")),
            ))
        options.append(ReportOption(
            option_id=str(uuid.uuid4()),
            label=o["label"],
            description=o["description"],
            risk_level=RiskLevel(o["risk_level"]),
            min_skill_level=float(o.get("min_skill_level", 0)),
            effects=effects,
        ))

    if not options:
        return None

    return Report(
        report_id=str(uuid.uuid4()),
        title=d["title"],
        description=d["description"],
        report_type=ReportType.CLAUDE_EVENT,
        addressed_to=player_id,
        domain=CouncilRole(domain),
        options=options,
        urgent=bool(d.get("urgency", False)),
        status=ReportStatus.PENDING,
        turn_received=gs.turn,
        turn_deadline=gs.turn + 2,
    )
