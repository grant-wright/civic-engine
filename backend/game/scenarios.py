import uuid
from game.state import (
    GameState, GameStatus, CityMap, MapNode, NodeType, CanalSegment, Waypoint,
    WaypointType, WaypointStatus, Faction, Councillor, CouncillorSkill, CouncilRole,
    Player, PlayerType, AIDifficulty, Agent, Metrics, RailwayParty, CanalParty,
    Report, ReportOption, ReportType, ReportStatus, RiskLevel,
)
from game.rules import FactionSensitivity


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _skill(name: str, desc: str) -> CouncillorSkill:
    return CouncillorSkill(skill_name=name, description=desc)


# ─── Councillors ──────────────────────────────────────────────────────────────

def _make_councillors() -> list[Councillor]:
    return [
        # Finance
        Councillor(
            councillor_id="c_fin_01",
            name="Sir Edmund Blackwell",
            role=CouncilRole.FINANCE,
            political_alignment="Conservative Whig — stability above all",
            core_values=["fiscal_prudence", "institutional_trust", "long_term_yield"],
            professional_background="Merchant banker, formerly of the East India Company. Fluent in bond markets and risk assessment.",
            value_tension="Believes canal investment is sound but distrusts the speculative fervour it may unleash.",
            skills=[
                _skill("Bond Structuring", "Reduces borrowing cost on large infrastructure loans."),
                _skill("Risk Assessment", "Identifies financial traps in agent proposals before they bite."),
            ],
            profile=(
                "You are Sir Edmund Blackwell, Finance Councillor. A conservative Whig merchant banker, "
                "you managed bond portfolios for the East India Company before entering civic life. "
                "You believe canals are a sound long-term investment — freight costs fall, trade expands, "
                "and property values along the waterway rise. But you are deeply wary of speculative mania. "
                "You will back canal proposals that show clear returns, reject ones driven by enthusiasm alone, "
                "and sound the alarm the moment bubble risk appears. Your core values: fiscal prudence, "
                "institutional trust, long-term yield. When in doubt, you ask: what is the yield at maturity?"
            ),
        ),
        Councillor(
            councillor_id="c_fin_02",
            name="Lady Catherine Morrow",
            role=CouncilRole.FINANCE,
            political_alignment="Progressive Whig — commerce enables reform",
            core_values=["workers_rights", "canal_progress", "economic_equity"],
            professional_background="Widow of a mill owner. Manages family assets. Understands the link between cheap freight and affordable goods.",
            value_tension="Wants canal prosperity to benefit workers, not just shareholders.",
            skills=[
                _skill("Wage Impact Analysis", "Predicts employment effects of construction decisions."),
                _skill("Merchant Liaison", "Negotiates favourable freight terms for the canal party."),
            ],
            profile=(
                "You are Lady Catherine Morrow, Finance Councillor. A progressive Whig, you inherited a mill "
                "and chose to run it with an eye to worker welfare rather than pure profit. You know that "
                "cheaper freight through canals directly lowers the cost of bread and coal for ordinary people. "
                "You will vote for canal investments, especially those that employ local navvies at fair wages. "
                "You are suspicious of agents who cut corners — you have seen what a collapsed cutting does to "
                "the men digging it. Core values: workers' rights, canal progress, economic equity."
            ),
        ),
        Councillor(
            councillor_id="c_fin_03",
            name="Mr. Josiah Threadneedle",
            role=CouncilRole.FINANCE,
            political_alignment="Pragmatic — follows the numbers, not the party",
            core_values=["fiscal_prudence", "accuracy", "efficiency"],
            professional_background="Certified public accountant. Former Treasury examiner. Obsessive record-keeper.",
            value_tension="Supports the canal project as long as the books balance; will switch sides if they don't.",
            skills=[
                _skill("Ledger Audit", "Detects budget overruns and agent corruption in financial reports."),
                _skill("Cost Modelling", "Produces accurate cost estimates for proposed canal sections."),
            ],
            profile=(
                "You are Mr. Josiah Threadneedle, Finance Councillor. A former Treasury examiner turned civic "
                "accountant. You have no political allegiance — only the ledger. You support the canal project "
                "because the numbers make sense: freight cost reductions compound over decades. But if the "
                "budget goes off-plan, you will say so loudly and vote for austerity measures. You despise "
                "vague cost estimates. Core values: fiscal prudence, accuracy, efficiency."
            ),
        ),
        Councillor(
            councillor_id="c_fin_04",
            name="Dr. Augustus Grieves",
            role=CouncilRole.FINANCE,
            political_alignment="Classical economist — free markets tempered by civic duty",
            core_values=["long_term_yield", "heritage", "institutional_trust"],
            professional_background="Political economist. Lectures at the Mechanics Institute. Published on canal network effects.",
            value_tension="Intellectually certain canals outperform roads; emotionally attached to the city's character.",
            skills=[
                _skill("Economic Forecasting", "Models freight split changes and their downstream effects."),
                _skill("Heritage Valuation", "Quantifies the economic value of aesthetic preservation."),
            ],
            profile=(
                "You are Dr. Augustus Grieves, Finance Councillor. A political economist who has written "
                "extensively on the network effects of connected canal systems. You know — with mathematical "
                "certainty — that a complete canal network will outcompete any road system for bulk freight. "
                "You also believe the canal's aesthetic character is an economic asset: canal-side amenity "
                "raises property values and draws visitors. Core values: long-term yield, heritage, "
                "institutional trust."
            ),
        ),

        # Infrastructure
        Councillor(
            councillor_id="c_inf_01",
            name="Mr. Thomas Brunel Jr.",
            role=CouncilRole.INFRASTRUCTURE,
            political_alignment="Engineering meritocrat — solve the problem, politics follows",
            core_values=["canal_progress", "engineering_excellence", "worker_safety"],
            professional_background="Civil engineer. Trained under his father. Specialises in aqueducts and tunnel boring.",
            value_tension="Wants to build fast and bold; knows haste kills navvies and collapses cuttings.",
            skills=[
                _skill("Structural Engineering", "Reduces construction risk on aqueducts, tunnels, and locks."),
                _skill("Survey Accuracy", "Spots alignment errors before they become expensive corrections."),
            ],
            profile=(
                "You are Mr. Thomas Brunel Jr., Infrastructure Councillor. A civil engineer trained under "
                "your father, specialising in the bold structures — aqueducts, tunnels, deep cuttings. "
                "You believe infrastructure is the city's backbone. Every completed canal segment is a "
                "permanent victory over geography. But you know construction kills when rushed. You push "
                "for quality over speed, and you will challenge any agent report that sacrifices structural "
                "integrity for a budget saving. Core values: canal progress, engineering excellence, "
                "worker safety."
            ),
        ),
        Councillor(
            councillor_id="c_inf_02",
            name="Miss Eleanor Fairweather",
            role=CouncilRole.INFRASTRUCTURE,
            political_alignment="Reform Whig — infrastructure as public good",
            core_values=["heritage", "worker_safety", "canal_progress"],
            professional_background="Self-taught surveyor. First woman to present before the Town Improvement Committee. Expert in flood risk.",
            value_tension="Fights for heritage preservation in canal routing; sometimes delays projects she ultimately supports.",
            skills=[
                _skill("Flood Risk Assessment", "Prevents costly reroutes by identifying drainage issues early."),
                _skill("Heritage Survey", "Identifies historically significant sites before construction begins."),
            ],
            profile=(
                "You are Miss Eleanor Fairweather, Infrastructure Councillor. A self-taught surveyor who "
                "forced her way into civic planning through sheer competence. You have mapped every flood "
                "plain and ancient common in this district. You support the canal wholeheartedly — but "
                "only if the route respects the land. You will block any alignment that runs through a "
                "heritage site without mitigation, and you will demand proper drainage surveys before "
                "any cutting begins. Core values: heritage, worker safety, canal progress."
            ),
        ),
        Councillor(
            councillor_id="c_inf_03",
            name="Captain Robert Ashby",
            role=CouncilRole.INFRASTRUCTURE,
            political_alignment="Tory pragmatist — order, efficiency, results",
            core_values=["efficiency", "fiscal_prudence", "institutional_trust"],
            professional_background="Royal Engineers, retired. Oversaw military canal works in Flanders. Values discipline and clear command.",
            value_tension="Believes the civilian construction industry is disorganised and corrupt; would prefer military oversight.",
            skills=[
                _skill("Logistics Planning", "Optimises supply chains for large construction sites."),
                _skill("Contractor Evaluation", "Identifies unreliable contractors before they default mid-project."),
            ],
            profile=(
                "You are Captain Robert Ashby, Infrastructure Councillor. A Royal Engineers veteran who "
                "built military canals in Flanders under budget and on schedule — because late meant men "
                "died. You find civilian contractors appalling: slow, dishonest, and prone to scope creep. "
                "You support the canal but insist on military-grade project discipline. You will push for "
                "tight contracts, penalty clauses, and regular inspection. Core values: efficiency, "
                "fiscal prudence, institutional trust."
            ),
        ),
        Councillor(
            councillor_id="c_inf_04",
            name="Mr. Patrick O'Brien",
            role=CouncilRole.INFRASTRUCTURE,
            political_alignment="Labour reformist — the men who dig deserve dignity",
            core_values=["workers_rights", "canal_progress", "worker_safety"],
            professional_background="Former navvy foreman, now a contractor. Knows every canal construction technique from the inside.",
            value_tension="Advocates for navvy welfare; sometimes seen as obstructive by those who want to move faster.",
            skills=[
                _skill("Navvy Management", "Maintains crew morale and reduces strikes on active construction."),
                _skill("Ground Knowledge", "Identifies subsurface hazards that surveyors miss."),
            ],
            profile=(
                "You are Mr. Patrick O'Brien, Infrastructure Councillor. You dug your first cutting at "
                "fourteen. You have spent thirty years in the earth, and you know every trick of the trade — "
                "and every way a poorly run site kills men. You are now a contractor and a councillor, and "
                "you use both roles to fight for the navvies who still do the digging. You will support "
                "canal progress enthusiastically, but you will stop any project that skips safety measures "
                "to save money. The men in the trench are not a line item. Core values: workers' rights, "
                "canal progress, worker safety."
            ),
        ),

        # Transport
        Councillor(
            councillor_id="c_trn_01",
            name="Lord William Trentham",
            role=CouncilRole.TRANSPORT,
            political_alignment="Canal Whig — waterways are civilisation",
            core_values=["canal_progress", "heritage", "economic_equity"],
            professional_background="Landowner. President of the Canal Society. Has funded three private canal ventures.",
            value_tension="Deeply invested in the canal's success; sometimes too optimistic about timelines and costs.",
            skills=[
                _skill("Route Advocacy", "Builds political support for approved canal routes in council."),
                _skill("Freight Negotiation", "Secures early freight commitments from merchants before a segment opens."),
            ],
            profile=(
                "You are Lord William Trentham, Transport Councillor. You have devoted your political "
                "life to the canal cause. Your grandfather funded the first lock in this district; your "
                "father sat on the original Canal Commission; you carry that legacy forward. You believe "
                "that connected waterways are the mark of a civilised city: cheap freight, clean water "
                "transport, amenity for all. You sometimes let enthusiasm outrun your judgement — you have "
                "been known to promise timelines the engineers cannot meet. But you will fight for the "
                "canal with everything you have. Core values: canal progress, heritage, economic equity."
            ),
        ),
        Councillor(
            councillor_id="c_trn_02",
            name="Mrs. Sarah Doyle",
            role=CouncilRole.TRANSPORT,
            political_alignment="Liberal reformist — transport connects communities",
            core_values=["economic_equity", "workers_rights", "efficiency"],
            professional_background="Runs a freight logistics firm. Manages 40 canal boats and 120 carters. Knows the transport system from the ground up.",
            value_tension="Wants canals to succeed but also relies on road haulage; genuinely weighs both sides.",
            skills=[
                _skill("Freight Analysis", "Calculates exact freight shift from road to canal for proposed segments."),
                _skill("Operator Network", "Knows every boat operator and carter in the district; spots supply chain issues early."),
            ],
            profile=(
                "You are Mrs. Sarah Doyle, Transport Councillor. You run the largest freight logistics firm "
                "in the district — forty canal boats, a hundred and twenty carters, and contracts with "
                "every major merchant in town. You are the canal party's most practical voice: you know "
                "what freight moves, on what route, at what cost. When a canal segment opens, you know "
                "immediately whether it shifts freight or just adds infrastructure. You will support "
                "canal investments that move goods; you will question those that look good on a map but "
                "serve no freight need. Core values: economic equity, workers' rights, efficiency."
            ),
        ),
        Councillor(
            councillor_id="c_trn_03",
            name="Mr. Charles Whitmore",
            role=CouncilRole.TRANSPORT,
            political_alignment="Tory landowner — order on the roads, order in the council",
            core_values=["institutional_trust", "fiscal_prudence", "efficiency"],
            professional_background="Turnpike Trust chairman. Manages toll revenue from six roads. Conflicted about canals cutting into road traffic.",
            value_tension="Publicly supports the canal party; privately worried about toll revenue losses.",
            skills=[
                _skill("Road Network Analysis", "Identifies which road routes will lose freight to new canal segments."),
                _skill("Toll Revenue Forecasting", "Estimates budget impacts of freight shift away from turnpikes."),
            ],
            profile=(
                "You are Mr. Charles Whitmore, Transport Councillor. You sit on the council as a canal "
                "party member, but you are also chairman of the Thornbury Turnpike Trust — you collect "
                "tolls from six roads, and canal freight eats directly into that income. You are not a "
                "traitor to the canal cause; you genuinely believe a connected waterway improves the "
                "whole city. But you pay close attention to which road routes each new canal segment "
                "threatens, and you will sometimes advocate for routing decisions that protect toll "
                "revenue. Core values: institutional trust, fiscal prudence, efficiency."
            ),
        ),
        Councillor(
            councillor_id="c_trn_04",
            name="Inspector James Holroyd",
            role=CouncilRole.TRANSPORT,
            political_alignment="Reform bureaucrat — systems over personalities",
            core_values=["efficiency", "accuracy", "worker_safety"],
            professional_background="Canal and river navigation inspector. Has surveyed 200 miles of working canals. Writes the most detailed reports on council.",
            value_tension="Believes in the canal system but has seen enough failures to be permanently sceptical of optimistic projections.",
            skills=[
                _skill("Navigation Survey", "Produces highly accurate depth, flow, and obstruction reports for proposed routes."),
                _skill("Maintenance Forecasting", "Predicts long-term maintenance costs that optimistic plans omit."),
            ],
            profile=(
                "You are Inspector James Holroyd, Transport Councillor. You have surveyed two hundred miles "
                "of working canals and written the inspection reports that determined whether they lived "
                "or were abandoned. You have seen canals that were engineering triumphs and ones that were "
                "expensive ditches that never moved a tonne of freight. You support this project, but you "
                "will not pretend problems do not exist. When an agent report claims construction is on "
                "track, you will ask for the survey data. When a timeline looks optimistic, you will say "
                "so on the record. Core values: efficiency, accuracy, worker safety."
            ),
        ),
    ]


# ─── Factions ─────────────────────────────────────────────────────────────────

def _make_factions() -> list[Faction]:
    return [
        Faction(
            faction_id="f_canal_workers",
            name="Canal Workers' Guild",
            profile=(
                "You are the Canal Workers' Guild — navvies, lock-keepers, and boat families who live by "
                "the waterway. The canal is not just your livelihood; it is your home. You react with "
                "fierce pride when a new section opens, and with anger when construction is slowed by "
                "bureaucracy or penny-pinching. You care deeply about worker safety — you have buried "
                "friends in collapsed cuttings. You distrust the Railway Syndicate absolutely."
            ),
            happiness=65.0,
            population_weight=1.2,
            transport_priorities=["canal_freight", "canal_employment"],
            political_sensitivities=["worker_safety", "canal_progress", "workers_rights"],
            reaction_threshold=FactionSensitivity.canal_workers,
            canal_alignment=0.9,
            railway_alignment=-0.7,
        ),
        Faction(
            faction_id="f_carters",
            name="Carter's Association",
            profile=(
                "You are the Carter's Association — road hauliers, draught-horse owners, and turnpike "
                "investors whose livelihoods depend on road freight. Every canal tonne is a lost contract. "
                "You are not evil; you are afraid. You will lobby against canal approvals, support road "
                "improvements, and argue loudly that canals are slow, seasonal, and prone to drought. "
                "The Railway Syndicate makes you nervous too — at least canals are slow to build."
            ),
            happiness=45.0,
            population_weight=0.9,
            transport_priorities=["road_freight", "turnpike_revenue"],
            political_sensitivities=["canal_progress", "freight_road", "fiscal_prudence"],
            reaction_threshold=FactionSensitivity.carters,
            canal_alignment=-0.6,
            railway_alignment=-0.3,
        ),
        Faction(
            faction_id="f_anglers",
            name="Angling Society",
            profile=(
                "You are the Angling Society — gentlemen and tradespeople who fish the rivers and streams. "
                "You are enthusiastic canal supporters when waterways are clean and well-maintained; "
                "you become fierce critics when canal works disturb fish habitat, cloud the water, or "
                "introduce effluent. You care passionately about the aesthetic quality of the waterside "
                "environment. An aqueduct over a trout stream delights you. Industrial effluent sickens you."
            ),
            happiness=60.0,
            population_weight=0.7,
            transport_priorities=["canal_amenity", "water_quality"],
            political_sensitivities=["heritage", "aesthetic_index", "horse_pollution"],
            reaction_threshold=FactionSensitivity.anglers,
            canal_alignment=0.7,
            railway_alignment=-0.4,
        ),
        Faction(
            faction_id="f_merchants",
            name="Merchants & Street Traders",
            profile=(
                "You are the Merchants and Street Traders — shopkeepers, market stallholders, and wholesale "
                "buyers who live and die by the cost of goods. Cheaper freight means cheaper stock means "
                "more customers. You are enthusiastic canal supporters when new segments reduce the cost "
                "of coal, timber, and grain. You are pragmatic: if the railway delivers cheaper goods, "
                "you will say so. You care about election stability — civil unrest is bad for trade."
            ),
            happiness=62.0,
            population_weight=1.1,
            transport_priorities=["freight_cost", "canal_freight", "road_freight"],
            political_sensitivities=["canal_progress", "economic_equity", "election_polling"],
            reaction_threshold=FactionSensitivity.merchants,
            canal_alignment=0.5,
            railway_alignment=0.1,
        ),
    ]


# ─── scenario_fresh_game ──────────────────────────────────────────────────────

def scenario_fresh_game() -> GameState:
    councillors = _make_councillors()
    factions = _make_factions()

    city_map = CityMap(
        nodes={
            "ironbridge_wharf": MapNode(
                node_id="ironbridge_wharf",
                name="Ironbridge Wharf",
                node_type=NodeType.PORT,
                position=(0.15, 0.25),
                has_canal_wharf=True,
            ),
            "millbrook_basin": MapNode(
                node_id="millbrook_basin",
                name="Millbrook Basin",
                node_type=NodeType.INDUSTRIAL,
                position=(0.20, 0.55),
            ),
            "thornbury_heights": MapNode(
                node_id="thornbury_heights",
                name="Thornbury Heights",
                node_type=NodeType.RESIDENTIAL,
                position=(0.65, 0.15),
            ),
            "coppergate_market": MapNode(
                node_id="coppergate_market",
                name="Coppergate Market",
                node_type=NodeType.MARKET,
                position=(0.50, 0.45),
            ),
            "ferndale_junction": MapNode(
                node_id="ferndale_junction",
                name="Ferndale Junction",
                node_type=NodeType.COMMERCIAL,
                position=(0.75, 0.55),
            ),
            "ashton_forge": MapNode(
                node_id="ashton_forge",
                name="Ashton Forge",
                node_type=NodeType.INDUSTRIAL,
                position=(0.40, 0.80),
            ),
        },
        canal_segments={
            "seg_01": CanalSegment(
                segment_id="seg_01",
                from_node="ironbridge_wharf",
                to_node="millbrook_basin",
                waypoints=[
                    Waypoint(
                        waypoint_id="wp_01_01",
                        name="Brindley's Lock",
                        waypoint_type=WaypointType.LOCK,
                        position=(0.16, 0.36),
                        status=WaypointStatus.COMPLETE,
                        construction_turns_required=4,
                        turns_spent=4,
                    ),
                    Waypoint(
                        waypoint_id="wp_01_02",
                        name="Old Wharf Cutting",
                        waypoint_type=WaypointType.CUTTING,
                        position=(0.17, 0.47),
                        status=WaypointStatus.COMPLETE,
                        construction_turns_required=3,
                        turns_spent=3,
                    ),
                ],
                construction_cost=3_200,
            ),
            "seg_02": CanalSegment(
                segment_id="seg_02",
                from_node="millbrook_basin",
                to_node="coppergate_market",
                waypoints=[
                    Waypoint(
                        waypoint_id="wp_02_01",
                        name="Market Embankment",
                        waypoint_type=WaypointType.EMBANKMENT,
                        position=(0.32, 0.50),
                        status=WaypointStatus.UNSTARTED,
                        construction_turns_required=4,
                    ),
                    Waypoint(
                        waypoint_id="wp_02_02",
                        name="Mill Basin Junction",
                        waypoint_type=WaypointType.JUNCTION,
                        position=(0.42, 0.47),
                        status=WaypointStatus.UNSTARTED,
                        construction_turns_required=2,
                    ),
                ],
                construction_cost=4_800,
            ),
        },
        councillors=councillors,
        factions=factions,
    )

    # Assign one councillor per player role
    trn_councillor = next(c for c in councillors if c.councillor_id == "c_trn_01")
    fin_councillor = next(c for c in councillors if c.councillor_id == "c_fin_01")
    inf_councillor = next(c for c in councillors if c.councillor_id == "c_inf_01")

    players: dict[str, Player] = {
        "p_transport": Player(
            player_id="p_transport",
            name="Lord William Trentham",
            role=CouncilRole.TRANSPORT,
            player_type=PlayerType.HUMAN,
            councillor=trn_councillor,
            agents=[
                Agent(
                    agent_id="a_trn_01",
                    name="Edwin Moss",
                    domain=CouncilRole.TRANSPORT,
                    specialisations=["route_planning", "freight_negotiation"],
                    risk_profile=0.4,
                    track_record=2,
                    hiring_cost=800,
                ),
            ],
        ),
        "p_finance": Player(
            player_id="p_finance",
            name="Sir Edmund Blackwell",
            role=CouncilRole.FINANCE,
            player_type=PlayerType.AI,
            ai_difficulty=AIDifficulty.MEDIUM,
            councillor=fin_councillor,
            agents=[
                Agent(
                    agent_id="a_fin_01",
                    name="Millicent Shaw",
                    domain=CouncilRole.FINANCE,
                    specialisations=["loan_brokering", "bond_assessment"],
                    risk_profile=0.3,
                    track_record=3,
                    hiring_cost=1_000,
                ),
            ],
        ),
        "p_infrastructure": Player(
            player_id="p_infrastructure",
            name="Mr. Thomas Brunel Jr.",
            role=CouncilRole.INFRASTRUCTURE,
            player_type=PlayerType.AI,
            ai_difficulty=AIDifficulty.MEDIUM,
            councillor=inf_councillor,
            agents=[
                Agent(
                    agent_id="a_inf_01",
                    name="George Holt",
                    domain=CouncilRole.INFRASTRUCTURE,
                    specialisations=["surveying", "tunnel_boring"],
                    risk_profile=0.5,
                    track_record=1,
                    hiring_cost=900,
                ),
            ],
        ),
    }

    seeded_report = Report(
        report_id="r_seed_01",
        title="Market Embankment Survey Request",
        description=(
            "Contractors have submitted preliminary estimates for the Market Embankment section "
            "of the Millbrook–Coppergate canal. Before construction can begin, the council must decide "
            "how thoroughly to survey the ground. A collapsed embankment set the last commission back "
            "by two years. How shall we proceed?"
        ),
        report_type=ReportType.SCHEDULED,
        addressed_to="p_transport",
        domain=CouncilRole.TRANSPORT,
        options=[
            ReportOption(
                option_id="opt_01_standard",
                label="Approve Standard Survey",
                description="Commission the contractor's standard ground survey. Reliable and fast.",
                effects=[],
                risk_level=RiskLevel.LOW,
            ),
            ReportOption(
                option_id="opt_01_enhanced",
                label="Commission Enhanced Survey",
                description="A more thorough survey including subsurface drainage assessment. Costs more time but reduces construction risk.",
                effects=[],
                risk_level=RiskLevel.MEDIUM,
            ),
            ReportOption(
                option_id="opt_01_skip",
                label="Proceed Without Survey",
                description="Skip the survey entirely to save two turns. High risk of embankment failure mid-construction.",
                effects=[],
                risk_level=RiskLevel.HIGH,
            ),
        ],
        status=ReportStatus.PENDING,
        turn_received=1,
        turn_deadline=3,
    )

    pending_reports = {"p_transport": [seeded_report]}

    return GameState(
        session_id=str(uuid.uuid4()),
        status=GameStatus.LOBBY,
        cycle=1,
        turn=1,
        game_length=5,
        city_map=city_map,
        players=players,
        metrics=Metrics(),
        factions=factions,
        railway_party=RailwayParty(),
        canal_party=CanalParty(),
        pending_reports=pending_reports,
    )


# ─── scenario_election_pressure ───────────────────────────────────────────────

def scenario_election_pressure() -> GameState:
    """
    Turn 18 of cycle 1 — two turns from the election with polling dangerously close
    to the loss threshold.  Used to test the engine's election and construction paths
    without playing through 17 turns.
    """
    gs = scenario_fresh_game()
    gs.status = GameStatus.IN_GAME
    gs.turn = 18

    # Polling close to loss threshold; happiness already below polling → polling falls next tick
    gs.metrics.election_polling = 45.0
    gs.metrics.citizen_happiness = 42.0

    # Canal efficiency below HorsePollution.low_efficiency_threshold (30) → pollution rising
    gs.metrics.canal_efficiency_index = 18.0
    gs.metrics.horse_pollution = 55.0

    # seg_02 waypoint 1 mid-construction: turns_spent=3, required=4 → completes on next advance_construction
    seg_02 = gs.city_map.canal_segments["seg_02"]
    wp = seg_02.waypoints[0]
    wp.status = WaypointStatus.UNDER_CONSTRUCTION
    wp.turns_spent = 3

    return gs


# ─── Scenario registry ────────────────────────────────────────────────────────

SCENARIOS = {
    "fresh_game": scenario_fresh_game,
    "election_pressure": scenario_election_pressure,
}
