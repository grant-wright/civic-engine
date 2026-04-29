from __future__ import annotations
from pydantic import BaseModel, Field, computed_field
from enum import Enum
from typing import Literal
from game.rules import StartingBudget, Turn


# ─── Enums ───────────────────────────────────────────────────────────────────

class GameStatus(str, Enum):
    LOBBY = "lobby"
    SETUP = "setup"
    IN_GAME = "in_game"
    GAME_OVER = "game_over"

class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"

class AIDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class CouncilRole(str, Enum):
    FINANCE = "finance"
    INFRASTRUCTURE = "infrastructure"
    TRANSPORT = "transport"

class NodeType(str, Enum):
    PORT = "port"
    INDUSTRIAL = "industrial"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MARKET = "market"

class WaypointType(str, Enum):
    CUTTING = "cutting"
    EMBANKMENT = "embankment"
    LOCK = "lock"
    AQUEDUCT = "aqueduct"
    TUNNEL = "tunnel"
    JUNCTION = "junction"
    AMENITY = "amenity"

class WaypointStatus(str, Enum):
    UNSTARTED = "unstarted"
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    CONTESTED = "contested"

class SegmentStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETE = "complete"

class RailwayPhase(str, Enum):
    LOBBY = "lobby"
    ACTIVE = "active"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EffectType(str, Enum):
    METRIC_DELTA = "metric_delta"
    BUDGET_DELTA = "budget_delta"
    CONSTRUCTION_START = "construction_start"
    CONSTRUCTION_ADVANCE = "construction_advance"
    FACTION_MOOD = "faction_mood"
    REPORT_GENERATE = "report_generate"
    RAILWAY_INFLUENCE = "railway_influence"
    CANALPARTY_INFLUENCE = "canalparty_influence"
    AESTHETIC_DELTA = "aesthetic_delta"
    ECONOMY_DELTA = "economy_delta"
    INCOME_DELTA = "income_delta"
    COUNCIL_EXTENSION = "council_extension"

class TargetType(str, Enum):
    METRIC = "metric"
    FACTION = "faction"
    SEGMENT = "segment"
    WAYPOINT = "waypoint"
    RAILWAY_PARTY = "railway_party"
    CANAL_PARTY = "canal_party"
    PLAYER = "player"
    AGENT = "agent"
    ECONOMY = "economy"
    FREIGHT_ROAD = "freight_road"
    FREIGHT_CANAL = "freight_canal"
    FREIGHT_RAIL = "freight_rail"
    CYCLE_INCOME = "cycle_income"

class ReportType(str, Enum):
    SCHEDULED = "scheduled"
    THRESHOLD = "threshold"
    CLAUDE_EVENT = "claude_event"
    AGENT_OUTCOME = "agent_outcome"

class ReportStatus(str, Enum):
    PENDING = "pending"
    DECIDED = "decided"
    DELEGATED = "delegated"
    DEFERRED = "deferred"
    ESCALATED = "escalated"
    AUTO_RESOLVED = "auto_resolved"

class GameEventType(str, Enum):
    WAYPOINT_COMPLETE = "waypoint_complete"
    WAYPOINT_BLOCKED = "waypoint_blocked"
    SEGMENT_COMPLETE = "segment_complete"
    NETWORK_EFFECT = "network_effect"
    MILESTONE_BRONZE = "milestone_bronze"
    MILESTONE_SILVER = "milestone_silver"
    MILESTONE_GOLD = "milestone_gold"
    ENGINEERING_FEAT = "engineering_feat"
    CANAL_MANIA = "canal_mania"
    CANAL_MANIA_BURST = "canal_mania_burst"
    RAILWAY_ACTIVATED = "railway_activated"
    RAILWAY_CRISIS = "railway_crisis"
    ELECTION_SURVIVED = "election_survived"
    GAME_OVER = "game_over"
    MAJOR_DECISION = "major_decision"
    AGENT_SUCCESS = "agent_success"
    AGENT_FAILURE = "agent_failure"
    FACTION_SWING = "faction_swing"
    COUNCIL_EXTENSION = "council_extension"
    CONNECTION_LOST = "connection_lost"
    CLAUDE_TIMEOUT = "claude_timeout"
    VOICE_FALLBACK = "voice_fallback"
    AUTO_RESOLVED = "auto_resolved"

class CanalTier(str, Enum):
    NONE = "none"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


# ─── Councillor & Agent ───────────────────────────────────────────────────────

class CouncillorSkill(BaseModel):
    skill_name: str
    description: str
    level: float = 1.0
    experience_points: int = 0


class Agent(BaseModel):
    agent_id: str
    name: str
    domain: CouncilRole
    specialisations: list[str]
    risk_profile: float = 0.5
    track_record: int = 0
    hiring_cost: int
    active: bool = True


class Councillor(BaseModel):
    councillor_id: str
    name: str
    role: CouncilRole
    political_alignment: str
    core_values: list[str]
    professional_background: str
    value_tension: str
    skills: list[CouncillorSkill]
    decisions_made: int = 0
    value_aligned_decisions: int = 0
    milestones_achieved: list[str] = []
    profile: str


# ─── Map Models (Waypoint → Segment → Node → Map) ────────────────────────────

class Waypoint(BaseModel):
    waypoint_id: str
    name: str
    waypoint_type: WaypointType
    position: tuple[float, float]
    status: WaypointStatus = WaypointStatus.UNSTARTED
    blocked_by: str | None = None
    construction_turns_required: int
    turns_spent: int = 0


class CanalSegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    waypoints: list[Waypoint]
    railway_claimed: bool = False
    construction_cost: int = 0

    @computed_field
    @property
    def status(self) -> SegmentStatus:
        if not self.waypoints:
            return SegmentStatus.PROPOSED
        if all(w.status == WaypointStatus.COMPLETE for w in self.waypoints):
            return SegmentStatus.COMPLETE
        if any(w.status in (WaypointStatus.UNDER_CONSTRUCTION, WaypointStatus.COMPLETE)
               for w in self.waypoints):
            return SegmentStatus.UNDER_CONSTRUCTION
        return SegmentStatus.PROPOSED

    @property
    def active_waypoint(self) -> Waypoint | None:
        return next(
            (w for w in self.waypoints
             if w.status not in (WaypointStatus.COMPLETE, WaypointStatus.BLOCKED)),
            None
        )


class RailwaySegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    waypoints: list[Waypoint]
    status: SegmentStatus


class MapNode(BaseModel):
    node_id: str
    name: str
    node_type: NodeType
    position: tuple[float, float]
    has_railway_station: bool = False
    has_canal_wharf: bool = False


# ─── Factions (before CityMap — CityMap embeds them) ─────────────────────────

class Faction(BaseModel):
    faction_id: str
    name: str
    profile: str
    happiness: float = 60.0
    population_weight: float = 1.0
    transport_priorities: list[str]
    political_sensitivities: list[str]
    reaction_threshold: float = 10.0
    canal_alignment: float = 0.0
    railway_alignment: float = 0.0


class FactionReaction(BaseModel):
    faction_id: str
    reaction_text: str
    happiness_delta: float
    triggered_by: str
    severity: Literal["minor", "moderate", "major"]
    display_on: list[str]


# ─── City Map (embeds councillors and factions — all generated together) ──────

class CityMap(BaseModel):
    nodes: dict[str, MapNode]
    canal_segments: dict[str, CanalSegment]
    railway_segments: list[RailwaySegment] = []
    councillors: list[Councillor] = []
    factions: list[Faction] = []

    def get_major_nodes(self) -> list[str]:
        return [n.node_id for n in self.nodes.values()
                if n.node_type in (NodeType.PORT, NodeType.INDUSTRIAL)]


# ─── Metrics & Economy ────────────────────────────────────────────────────────

class DepartmentBudget(BaseModel):
    finance: int = StartingBudget.finance
    infrastructure: int = StartingBudget.infrastructure
    transport: int = StartingBudget.transport


class Metrics(BaseModel):
    road_rage_index: float = 50.0
    canal_efficiency_index: float = 10.0
    aesthetic_index: float = 40.0

    citizen_happiness: float = 65.0
    horse_pollution: float = 30.0
    accidents_this_cycle: int = 0
    projects_delayed: int = 0
    tradies_nonbilling: int = 0

    road_freight_pct: float = 100.0
    canal_freight_pct: float = 0.0
    rail_freight_pct: float = 0.0

    economy_index: float = 50.0
    cycle_income: int = 0

    budget: DepartmentBudget = Field(default_factory=DepartmentBudget)

    election_polling: float = 65.0
    cycles_survived: int = 0


# ─── Railway & Canal Parties ──────────────────────────────────────────────────

class RailwayParty(BaseModel):
    influence: float = 20.0
    phase: RailwayPhase = RailwayPhase.LOBBY
    activation_threshold: float = 40.0
    lobbying_events: list[str] = []
    councillors: list[Councillor] = []
    railway_segments: list[RailwaySegment] = []
    budget: int = 0


class CanalParty(BaseModel):
    influence: float = 50.0
    milestones_achieved: list[str] = []


class CanalMania(BaseModel):
    triggered: bool = False
    windfall_received: int = 0
    bubble_risk: float = 0.0
    bubble_burst: bool = False


# ─── Effects ──────────────────────────────────────────────────────────────────

class Effect(BaseModel):
    effect_type: EffectType
    target_type: TargetType
    target_id: str
    value: float | str
    delay_turns: int = 0
    description: str


# ─── Reports ──────────────────────────────────────────────────────────────────

class ReportOption(BaseModel):
    option_id: str
    label: str
    description: str
    effects: list[Effect]
    risk_level: RiskLevel
    agent_only: bool = False
    is_forced: bool = False
    value_signals: list[str] = []
    min_skill_level: float = 0.0
    required_skill: str | None = None


class Report(BaseModel):
    report_id: str
    title: str
    description: str
    report_type: ReportType
    addressed_to: str
    domain: CouncilRole
    options: list[ReportOption]
    status: ReportStatus = ReportStatus.PENDING
    is_private: bool = True
    delegation_candidates: list[str] = []
    delegated_to: str | None = None
    decision: str | None = None
    conflict_with: str | None = None
    defer_count: int = 0
    deferred_until_turn: int | None = None
    deferral_consequences: list[str] = []
    escalated_to_council: bool = False
    urgent: bool = False
    turn_received: int
    turn_deadline: int


# ─── Council Vote ─────────────────────────────────────────────────────────────

class Vote(BaseModel):
    vote_id: str
    report_ids: list[str]
    initiated_by: str
    options: list[ReportOption]
    votes: dict[str, str] = {}
    status: Literal["pending", "resolved"] = "pending"
    result: str | None = None
    mayor_tiebreaker: bool = False


# ─── Win State ────────────────────────────────────────────────────────────────

class WinState(BaseModel):
    outcome: Literal["game_over", "survived", "modest_win", "strong_win",
                     "celebration", "heritage_commendation"]
    canal_tier: CanalTier
    heritage_commendation: bool = False
    cycles_survived: int
    epitaph: str


# ─── Events ───────────────────────────────────────────────────────────────────

class GameEvent(BaseModel):
    event_id: str
    event_type: GameEventType
    turn: int
    cycle: int
    description: str
    player_id: str | None = None
    data: dict = Field(default_factory=dict)


# ─── Voice Command Parsing ────────────────────────────────────────────────────

class ParsedCommand(BaseModel):
    action_type: str
    target_type: TargetType | None = None
    target_id: str | None = None
    parameters: dict = Field(default_factory=dict)
    confidence: float
    clarification_needed: bool = False
    clarification_prompt: str | None = None


# ─── Player ───────────────────────────────────────────────────────────────────

class Player(BaseModel):
    player_id: str
    name: str
    role: CouncilRole
    player_type: PlayerType = PlayerType.HUMAN
    councillor: Councillor
    agents: list[Agent] = []
    ai_difficulty: AIDifficulty | None = None


# ─── Root Game State ──────────────────────────────────────────────────────────

class GameState(BaseModel):
    session_id: str
    status: GameStatus
    cycle: int = 1
    turn: int = 1
    game_length: int = 5

    city_map: CityMap
    players: dict[str, Player]
    metrics: Metrics
    factions: list[Faction]
    railway_party: RailwayParty
    canal_party: CanalParty
    canal_mania: CanalMania = Field(default_factory=CanalMania)

    pending_reports: dict[str, list[Report]] = Field(default_factory=dict)
    pending_vote: Vote | None = None

    pending_effects: list[tuple[int, Effect]] = []
    event_log: list[GameEvent] = []

    council_extensions_remaining: int = Turn.extensions_per_game
    turn_time_limit: int = Turn.default_seconds
    current_turn_extended: bool = False

    win_state: WinState | None = None

    def to_context_summary(self) -> str:
        m = self.metrics
        faction_lines = ", ".join(
            f"{f.name} (id={f.faction_id}, happiness={f.happiness:.0f})"
            for f in self.factions
        )
        return (
            f"Turn {self.turn}/20, Cycle {self.cycle}/{self.game_length}. "
            f"Road Rage: {m.road_rage_index:.0f}, Canal Efficiency: {m.canal_efficiency_index:.0f}, "
            f"Aesthetic: {m.aesthetic_index:.0f}. "
            f"Citizen Happiness: {m.citizen_happiness:.0f}, Election Polling: {m.election_polling:.0f}. "
            f"Canal freight: {m.canal_freight_pct:.0f}%, Railway influence: {self.railway_party.influence:.0f}. "
            f"Canal party influence: {self.canal_party.influence:.0f}. "
            f"Factions: {faction_lines}."
        )

    def get_faction(self, faction_id: str) -> Faction:
        for f in self.factions:
            if f.faction_id == faction_id:
                return f
        raise KeyError(f"Faction {faction_id!r} not found")
