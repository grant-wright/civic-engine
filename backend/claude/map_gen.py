from claude.client import MODEL, record_usage, safe_claude_call
from game.state import CityMap

_MAP_GEN_INSTRUCTIONS = """You are a Victorian city map designer for Civic Engine, a cooperative city management game set in the 1780s–1820s.

Generate a complete city setup. The city is at the dawn of the canal age: horse-drawn freight dominates, a canal party has partially built a waterway network, and the early railway lobby is beginning to stir.

DISTRICTS (8–10 nodes):
- Exactly 2 PORT nodes (river docks, wharfs — place near edges, x < 0.25 or x > 0.75)
- Exactly 2–3 INDUSTRIAL nodes (iron foundries, cloth mills — mid-city, varied positions)
- Exactly 2–3 RESIDENTIAL nodes (workers' terraces, merchant streets)
- Exactly 1 COMMERCIAL node (trading halls, counting houses)
- Exactly 1 MARKET node (central market square — position near 0.45–0.55, 0.45–0.55)
- Names must be period-accurate late Georgian / early Regency (e.g. "Ironbridge Wharf", "Millbrook Basin", "Coppergate Market")
- Positions: (x, y) floats 0.0–1.0. Spread across the grid — no two nodes closer than 0.15 apart.
- node_id: snake_case of the name (e.g. "ironbridge_wharf")
- has_canal_wharf: true for PORT nodes, false for others
- has_railway_station: false for all (railways not yet active)

CANAL SEGMENTS (4–6 total):
- Connect district nodes in geographic paths
- Each segment has 2–4 ordered waypoints
- Waypoint construction_turns_required by type: AQUEDUCT=7, TUNNEL=9, LOCK=5, CUTTING=4, EMBANKMENT=4, JUNCTION=3, AMENITY=2
- Waypoint positions: interpolate between from_node and to_node positions along the path
- waypoint_id format: "wp_{segment_number}_{waypoint_index}" where both are zero-padded two-digit integers
  Example: segment 1 has waypoints wp_01_01, wp_01_02, wp_01_03. Segment 2 has wp_02_01, wp_02_02.
- EXACTLY 1–2 segments must have ALL waypoints with status="complete" and turns_spent equal to construction_turns_required — these are short 2-waypoint stubs from a previous failed commission. They must be disconnected from each other (do not share any nodes that would connect them).
- All other segments: all waypoints status="unstarted", turns_spent=0
- segment_id format: "seg_01", "seg_02" etc.
- construction_cost: 2000–8000 depending on waypoint complexity

FACTIONS (4–6, included in factions list):
- Mix: 2–3 pro-canal, 1–2 anti-canal, 1 pragmatic neutral
- profile: 5–7 sentences written in the faction's voice (first person plural "we") — this text is used directly as Claude's system prompt when generating faction reactions. Include: who they are, what they need, what they fear, how they feel about the canal, how they feel about the railway.
- faction_id: snake_case (e.g. "canal_workers_guild", "carters_association")
- canal_alignment: float -1.0 to +1.0
- railway_alignment: float -1.0 to +1.0
- population_weight: float 0.6–1.4 (relative faction size)
- political_sensitivities: 2–4 strings from: worker_safety, canal_progress, workers_rights, fiscal_prudence, heritage, aesthetic_index, horse_pollution, freight_road, economic_equity, election_polling, engineering_excellence
- reaction_threshold: float 8.0–15.0

COUNCILLORS (exactly 12, included in councillors list):
- Roles: finance (4), infrastructure (4), transport (4)
- councillor_id format: "c_fin_01" through "c_fin_04", "c_inf_01" through "c_inf_04", "c_trn_01" through "c_trn_04"
- political_alignment: 1 sentence (e.g. "Conservative Whig — stability above all")
- core_values: 3–5 strings from: fiscal_prudence, institutional_trust, long_term_yield, workers_rights, canal_progress, economic_equity, accuracy, efficiency, engineering_excellence, worker_safety, heritage
- professional_background: 1–2 sentences about their career and expertise
- value_tension: 1 sentence — the competing good within them (a genuine dilemma, not a simple character flaw)
- skills: 2–3 skills. Each skill has skill_name (title-case 2–3 words) and description (one sentence starting with a verb, describing what the skill enables)
- profile: 5–7 sentences. Start with "You are [name], [role] Councillor." This text is used directly as Claude's system prompt for AI player decisions. Include their name, values, professional identity, how they make decisions, what they will and won't support.
- decisions_made: 0, value_aligned_decisions: 0, milestones_achieved: []

Generate historically grounded late Georgian characters with distinct voices and real internal tensions."""


async def generate_city_map() -> CityMap:
    schema = CityMap.model_json_schema()

    response = await safe_claude_call(
        call_type="map_gen",
        kwargs={
            "model": MODEL,
            "max_tokens": 3000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": _MAP_GEN_INSTRUCTIONS,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": "Generate the Victorian city now using the generate_city_map tool.",
                        },
                    ],
                }
            ],
            "tools": [
                {
                    "name": "generate_city_map",
                    "description": "Generate a complete late Georgian city map with districts, canal segments, factions, and councillors.",
                    "input_schema": schema,
                }
            ],
            "tool_choice": {"type": "tool", "name": "generate_city_map"},
        },
        fallback_tokens=5000,
    )

    record_usage("map_gen", response)

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    return CityMap.model_validate(tool_use_block.input)
