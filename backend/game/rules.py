"""
game/rules.py — all tunable game-mechanics constants, grouped by domain.

Every value corresponds to a named spec section. Changing a value here
changes game balance globally — no magic numbers in game logic elsewhere.

All monetary values are in Pounds Sterling (£).
"""


class Happiness:
    """
    Citizen happiness computation weights.
    Spec: Metrics & Economy > Metric recomputation sequence (game/factions.py)
    """
    faction_weight = 0.8        # faction component's share of citizen happiness
    aesthetic_weight = 0.2      # aesthetic index's share
    default = 65.0              # fallback when no factions are defined


class CanalEfficiency:
    """
    Canal efficiency index formula and network tier bonuses.
    Spec: City Map & Canal Network > Canal connectivity check (game/map.py)
         Metrics & Economy > Metric recomputation sequence
    """
    freight_factor = 0.8            # canal_freight_pct * this = base efficiency value
    gold_coverage_threshold = 0.8   # fraction of all districts required for Gold tier
    bronze_bonus = 15.0             # network bonus added to base when Bronze tier achieved
    silver_bonus = 25.0
    gold_bonus = 40.0


class Economy:
    """
    Economy index inertia model and freight-mode multipliers.
    Spec: Metrics & Economy > Metric recomputation sequence
    """
    inertia = 0.25              # how fast economy_index moves toward target each turn
    canal_freight_mult = 1.2    # goods-per-load advantage over road
    rail_freight_mult = 0.9     # efficient but a rival to the canal party
    road_freight_mult = 0.4     # slow, congested, costly


class Election:
    """
    Election polling mechanics and loss condition.
    Spec: Elections & Win States > Election resolution (game/elections.py)
         Reports & Turn Loop > Deferral rules
         Real-time Communication > council_extension event
    """
    loss_threshold = 40.0           # polling below this triggers game over
    polling_lag = 0.2               # how fast polling tracks citizen_happiness each turn
    deferral_polling_cost = 2.0     # election_polling penalty per deferred report
    extension_polling_cost = 2.0    # election_polling penalty per council extension
    heritage_aesthetic_threshold = 70.0  # aesthetic_index required for heritage_commendation win


class Income:
    """
    Cycle-end income formula and department budget split, in Pounds Sterling (£).
    Spec: Metrics & Economy > Cycle-end income (game/elections.py)
    Note: finance_divisor + infrastructure_divisor + transport_divisor sum to 100%
    (1/2 + 1/3 + 1/6 = 1), but integer division means Finance absorbs any
    rounding remainder.
    """
    base = 5_000                    # (£) base income before economy_index scaling
    finance_divisor = 2             # Finance receives income // 2
    infrastructure_divisor = 3      # Infrastructure receives income // 3
    transport_divisor = 6           # Transport receives income // 6


class StartingBudget:
    """
    Department starting budgets in Pounds Sterling (£).
    Spec: Metrics & Economy > Metrics model (DepartmentBudget defaults in state.py)
    Finance starts higher — it is the revenue-managing role.
    """
    finance = 10_000
    infrastructure = 5_000
    transport = 5_000


class Turn:
    """
    Turn timer and council extension rules.
    Spec: Reports & Turn Loop > Player action set
         Real-time Communication > council_extension event
    """
    turns_per_cycle = 20             # turns before election check fires
    default_seconds = 40            # server-authoritative turn duration
    extension_seconds = 30          # seconds added per council extension
    extensions_per_game = 3         # total extensions available each game
    valid_game_lengths = (4, 5, 6)  # in cycles; chosen at game setup


class Railway:
    """
    Railway party influence growth and activation threshold.
    Spec: Railway Party > Railway influence growth
         Railway Party > Railway activation event

    KNOWN ISSUE: The spec defines different activation *timing* per game length:
        Beginner (4 cycles): Cycle 3, Turn 1
        Standard (5 cycles): Cycle 2, Turn 10
        Experienced (6 cycles): Cycle 2, Turn 1
    Currently only the influence threshold is checked. The cycle/turn timing
    mechanic is unimplemented.
    Recommended fix (for /iterate):
        — At game start, set railway_party.activation_threshold based on
          game_length via a lookup table here.
        — Add check_railway_activation_timing() in engine.py that forces
          activation at the correct cycle/turn regardless of influence level.
    """
    growth_per_turn = 2.5                # influence gained per turn at 0% canal freight
                                         # formula: (1 - canal_freight_pct/100) * growth_per_turn
    default_activation_threshold = 40.0  # overridable on RailwayParty per difficulty


class HorsePollution:
    """
    Horse pollution rise/fall rules.
    Spec: Metrics & Economy > Horse pollution rule
    """
    rise_per_turn = 2.0                 # added each turn when canal efficiency is low
    fall_per_turn = 1.0                 # removed each turn when canal freight is sufficient
    low_efficiency_threshold = 30.0     # canal_efficiency_index below this triggers rise
    freight_threshold = 20.0            # canal_freight_pct above this triggers fall
    crisis_threshold = 70.0             # crosses this → public health report fires (step 10)


class RoadRage:
    """
    Road rage index formula weights and per-turn step cap.
    Spec: Metrics & Economy > Metric recomputation sequence (game/engine.py)
    target = road_freight_pct * freight_weight + horse_pollution * pollution_weight
    """
    freight_weight = 0.6       # road freight load's share of the road rage target
    pollution_weight = 0.4     # horse pollution's share
    max_step_per_turn = 5.0    # road_rage_index moves no more than this per turn


class FactionAlertThreshold:
    """
    Metric levels at which factions begin to notice conditions and react.
    Used in game/factions.py build_turn_summary() to inject sensitivity keywords
    so the faction_affected() filter routes Claude reaction calls correctly.
    Spec: Factions & Aesthetic Index > Faction reaction generation (claude/citizens.py)
    """
    road_freight_high = 60.0        # road_freight_pct above this → freight_road, fiscal_prudence
    horse_pollution_notable = 50.0  # horse_pollution above this → horse_pollution keyword
    aesthetic_notable = 55.0        # aesthetic_index above this → aesthetic_index, heritage
    polling_concerning = 60.0       # election_polling below this → election_polling, economic_equity


class FactionSensitivity:
    """
    Per-faction reaction_threshold — how large a happiness delta triggers a
    Claude reaction call for that faction. Lower = more reactive.
    Spec: Factions & Aesthetic Index > Faction reaction generation (claude/citizens.py)
    Used in step 11 (citizens.py) to filter which factions receive a Claude call.
    """
    canal_workers = 8.0     # canal workers react strongly — the canal is their livelihood
    carters = 12.0          # road hauliers take more to rattle
    anglers = 10.0
    merchants = 10.0


class WaypointConstruction:
    """
    Baseline construction turns required by waypoint type.
    Spec: City Map & Canal Network > Waypoint
    Passed to Claude as guidance during map generation; used to validate/default
    waypoints at creation time.
    FLAG FOR /ITERATE: enforce these at waypoint creation — currently advisory
    only (Claude may vary them slightly in generated maps).
    """
    turns_required = {
        "aqueduct":   7,    # crosses road or river — high engineering complexity
        "tunnel":     9,    # underground — highest cost and risk
        "lock":       5,    # changes water level
        "cutting":    4,    # dug through earth
        "embankment": 4,    # built up above ground
        "junction":   3,    # branches to another canal
        "amenity":    2,    # fishing platform, mooring, towpath garden
    }
