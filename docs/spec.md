# Civic Engine — Technical Specification

*Implements `prd.md` in full. Every PRD epic has a named section below. Every architectural component has its own heading so `/checklist` can reference it precisely.*

---

## Stack

| Layer | Technology | Version | Docs |
|---|---|---|---|
| Backend language | Python | 3.10+ | https://docs.python.org/3/ |
| Backend framework | FastAPI | 0.136.1 | https://fastapi.tiangolo.com/ |
| Data validation | Pydantic | v2 | https://docs.pydantic.dev/latest/ |
| Real-time | python-socketio | latest | https://python-socketio.readthedocs.io/ |
| AI SDK | Anthropic Python SDK | 0.80.0 | https://github.com/anthropics/anthropic-sdk-python |
| Graph algorithms | NetworkX | latest | https://networkx.org/documentation/stable/ |
| Frontend language | TypeScript | 5.x | https://www.typescriptlang.org/docs/ |
| Frontend framework | React | 18.x | https://react.dev/ |
| Frontend build | Vite | 7.x (stable) | https://vite.dev/guide/ |
| Graph rendering | React Flow | @xyflow/react latest | https://reactflow.dev/learn |
| Real-time client | socket.io-client | latest | https://socket.io/docs/v4/client-api/ |
| Type generation | openapi-typescript | latest | https://openapi-ts.dev/ |

**Install commands:**
```bash
# Backend
pip install "fastapi[standard]" python-socketio anthropic networkx pydantic

# Frontend
npm create vite@latest civic-engine-frontend -- --template react-ts
cd civic-engine-frontend
npm install @xyflow/react socket.io-client
npm install -D openapi-typescript
```

---

## Runtime & Deployment

### Development (primary target)
- Runs entirely on localhost — no cloud services required during build or demo
- Backend: `uvicorn main:app --reload` on port 8000
- Frontend: `npm run dev` on port 5173
- Central screen: open `http://localhost:5173/central` in a browser window
- Player phones: open `http://localhost:5173/phone` in Chrome on each phone (same WiFi network)
- Voice commands require Chrome or Edge on player phones

### Environment requirements
- Python 3.10+
- Node.js 20.19+ (required by Vite 7.x)
- API key: `ANTHROPIC_API_KEY` in `backend/.env`
- Admin token: `ADMIN_TOKEN` in `backend/.env` (protects dev/admin endpoints)

### Cloud deployment (future — not required for hackathon)
- Target platform: Railway.app (supports FastAPI + WebSocket persistent connections)
- Docs: https://docs.railway.com/
- Note: No permanent free tier as of 2026. 30-day trial then $5/month minimum.
- Architecture is deployment-ready: no hardcoded localhost, all secrets in env vars, proper CORS config

### TypeScript type generation
Types in `frontend/src/types.ts` are auto-generated from the live backend schema. Add to `frontend/package.json`:
```json
"scripts": {
    "generate-types": "openapi-typescript http://localhost:8000/openapi.json -o src/types.ts",
    "dev": "npm run generate-types && vite"
}
```
Run backend first, then start frontend. Types regenerate on every dev start — no manual sync needed.

**Backup type generation (if openapi-typescript causes issues):**
```bash
pip install datamodel-code-generator
python -c "from game.state import GameState; import json; print(json.dumps(GameState.model_json_schema()))" > schema.json
datamodel-codegen --input schema.json --input-file-type jsonschema --output-model-type typescript --output frontend/src/types.ts
```

---

## Architecture Overview

### Component diagram

```
┌──────────────────────────────────┐
│   Central Screen (Browser)       │
│   React/TypeScript               │
│   /central route                 │
│   City map, metrics, events,     │
│   votes, influence meter         │
└─────────────┬────────────────────┘
              │ WebSocket (socket.io)
              ▼
┌──────────────────────────────────┐     ┌─────────────────────┐
│   Game Server (Python)           │────▶│   Anthropic API      │
│   FastAPI + python-socketio      │     │   claude-sonnet-4-6  │
│   Single source of truth         │◀────│   Voice, citizens,   │
│   All game logic lives here      │     │   events, map gen,   │
│   NetworkX for canal graph       │     │   AI players         │
└─────────────┬────────────────────┘     └─────────────────────┘
              │ WebSocket (socket.io)
              ▼
┌──────────────────────────────────┐
│   Player Phones (Browser)        │
│   React/TypeScript               │
│   /phone route                   │
│   Reports, agents, voice,        │
│   turn timer, vote casting       │
└──────────────────────────────────┘
```

### Core principle
The server holds one `GameState` object in memory. On every change it serialises to JSON and broadcasts to all connected clients. Clients are pure display and input — they render what they receive and forward user actions. Claude is only ever called from the server, never from the browser.

### Turn lifecycle

```
Server starts turn N
    ↓
Generate reports per player (scheduled + threshold + Claude events)
Distribute to phones via WebSocket
40-second server-side timer starts
    ↓
Players act simultaneously:
  Human player → button press or voice → WebSocket → server
  AI players (Finance, Infrastructure) → claude/ai_player.py → server
    ↓
Timer expires → unresolved reports auto-delegated or first option selected
    ↓
Conflict detection → council vote if needed
    ↓
All resolved → apply immediate effects
asyncio.gather() → concurrent Claude calls:
  • Faction reactions (all affected factions in parallel)
  • Next turn reports (3 domains in parallel)
    ↓
Recompute: canal connectivity, freight split, economy, citizen happiness, polling
Check: railway crisis trigger, canal milestones, Canal Mania, election
Log: GameEvents to event_log
Record: Claude usage to UsageTracker
    ↓
Broadcast full game_state to all clients
Next turn begins
```

---

## Game State Data Model

*Implements `prd.md` — all epics. The single source of truth held in server memory.*

### GameState (root model)

```python
# backend/game/state.py

from pydantic import BaseModel
from enum import Enum
from typing import Literal

class GameStatus(str, Enum):
    LOBBY = "lobby"
    SETUP = "setup"
    IN_GAME = "in_game"
    GAME_OVER = "game_over"

class GameState(BaseModel):
    session_id: str                                    # UUID, new each game
    status: GameStatus
    cycle: int = 1                                     # election cycle (1–6)
    turn: int = 1                                      # turn within cycle (1–20)
    game_length: int = 5                               # 4 / 5 / 6 cycles, chosen at setup

    city_map: CityMap
    players: dict[str, Player]                         # player_id → Player
    metrics: Metrics
    factions: list[Faction]
    railway_party: RailwayParty
    canal_party: CanalParty

    pending_reports: dict[str, list[Report]]           # player_id → reports
    pending_vote: Vote | None = None

    pending_effects: list[tuple[int, Effect]] = []     # (apply_at_turn, Effect)
    event_log: list[GameEvent] = []

    council_extensions_remaining: int = 3
    turn_time_limit: int = 40                          # seconds
    current_turn_extended: bool = False

    win_state: WinState | None = None
```

### PlayerType and Player

```python
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

class Player(BaseModel):
    player_id: str
    name: str
    role: CouncilRole
    player_type: PlayerType = PlayerType.HUMAN
    councillor: Councillor
    agents: list[Agent] = []
    ai_difficulty: AIDifficulty | None = None          # AI players only
```

---

## City Map & Canal Network

*Implements `prd.md > Canal Network & City Map`, `prd.md > Game Setup`*

### CityMap

```python
class CityMap(BaseModel):
    nodes: dict[str, MapNode]
    canal_segments: dict[str, CanalSegment]
    railway_segments: list[RailwaySegment] = []       # populated after railway activation

    def get_major_nodes(self) -> list[str]:
        return [n.node_id for n in self.nodes.values()
                if n.node_type in (NodeType.PORT, NodeType.INDUSTRIAL)]
```

### MapNode

```python
class NodeType(str, Enum):
    PORT = "port"
    INDUSTRIAL = "industrial"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MARKET = "market"

class MapNode(BaseModel):
    node_id: str
    name: str                                          # "Ironbridge Wharf", "Millbrook Basin"
    node_type: NodeType
    position: tuple[float, float]                      # normalised 0.0–1.0 for React rendering
    has_railway_station: bool = False
    has_canal_wharf: bool = False
```

### Waypoint

```python
class WaypointType(str, Enum):
    CUTTING = "cutting"           # dug through earth
    EMBANKMENT = "embankment"     # built up above ground
    LOCK = "lock"                 # changes water level
    AQUEDUCT = "aqueduct"         # crosses road or river → engineering feat trigger
    TUNNEL = "tunnel"             # underground, high cost/risk
    JUNCTION = "junction"         # branches to another canal
    AMENITY = "amenity"           # fishing platform, mooring, towpath garden

class WaypointStatus(str, Enum):
    UNSTARTED = "unstarted"
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    CONTESTED = "contested"

class Waypoint(BaseModel):
    waypoint_id: str
    name: str                                          # "Brindley's Cutting", "Chadwick Locks"
    waypoint_type: WaypointType
    position: tuple[float, float]                      # on the path between districts
    status: WaypointStatus = WaypointStatus.UNSTARTED
    blocked_by: str | None = None                      # "railway_claim" | "flood_event" | "strike"
    construction_turns_required: int                   # varies by type (aqueduct > cutting)
    turns_spent: int = 0
```

### CanalSegment

```python
class SegmentStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETE = "complete"

class CanalSegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    waypoints: list[Waypoint]                          # ordered from→to
    railway_claimed: bool = False                      # corridor contested by railway party
    construction_cost: int = 0

    @property
    def status(self) -> SegmentStatus:
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
    # Future upgrade: waypoints list becomes sub-nodes in full graph (Option B discriminated union)
```

### Canal connectivity check (game/map.py)

```python
import networkx as nx

def check_canal_connectivity(city_map: CityMap) -> CanalTier:
    G = nx.Graph()
    for seg in city_map.canal_segments.values():
        if seg.status == SegmentStatus.COMPLETE:
            G.add_edge(seg.from_node, seg.to_node)

    major = city_map.get_major_nodes()
    if not all(G.has_node(n) for n in major):
        return CanalTier.NONE
    if not nx.is_connected(G.subgraph(major)):
        return CanalTier.NONE

    # Check Silver: all major nodes + all nodes of one type
    # Check Gold: every district connected, 80%+ coverage
    # Returns: NONE | BRONZE | SILVER | GOLD
```

Docs: https://networkx.org/documentation/stable/reference/algorithms/connected.html

### AI map generation (claude/map_gen.py)

Claude generates the complete city map at startup via tool use. The Pydantic schema is passed as the tool's input schema. Returns validated `CityMap` JSON including node positions (normalised 0.0–1.0), canal segment routes, and named/typed waypoints.

Starting state: city begins with 1–2 short disconnected canal stubs from a previous failed commission. Complete but unconnected — no network effect yet. Gives players something to build toward.

This module is the **MCP server candidate** for afternoon experimentation. Wrap `generate_city_map()` as an MCP tool called `generate_victorian_city_map`.

---

## Railway Party

*Implements `prd.md > Railway Party & Time Pressure`*

### RailwayPhase

```python
class RailwayPhase(str, Enum):
    LOBBY = "lobby"     # passive pressure, lobbying events only, no map presence
    ACTIVE = "active"   # AI councillors operational, segments appearing on map
```

### RailwayParty

```python
class RailwayParty(BaseModel):
    influence: float = 20.0
    phase: RailwayPhase = RailwayPhase.LOBBY
    activation_threshold: float = 40.0               # tunable per difficulty
    lobbying_events: list[str] = []

    # Phase 2 — mirrors canal party structure
    councillors: list[RailwayCouncillor] = []
    railway_segments: list[RailwaySegment] = []
    budget: int = 0
```

### CanalParty

```python
class CanalParty(BaseModel):
    influence: float = 50.0                           # starts at parity
    milestones_achieved: list[str] = []
```

### Railway influence growth
- Grows each turn based on canal progress (slow canal = faster railway rise)
- Generates competing lobbying event reports on councillor phones
- Railway crisis trigger: `railway_party.influence >= canal_party.influence`
- Coal and steel scarcity constrains early influence growth (PRD-specified)

### Railway activation event
When `influence >= activation_threshold`:
1. `GameEvent.RAILWAY_ACTIVATED` fires
2. Central screen: dramatic event card ("The Steam Engine Act has passed. The Railway Syndicate is now organised.")
3. Railway councillors introduced via dossier reveal
4. `railway_party.budget` initialised
5. `railway_party.phase → ACTIVE`
6. From next turn: railway AI councillors decide, railway segments appear on map

**Activation timing by game length:**

| Game length | Railway activates |
|---|---|
| 4 cycles (beginner) | Cycle 3, turn 1 |
| 5 cycles (standard) | Cycle 2, turn 10 |
| 6 cycles (experienced) | Cycle 2, turn 1 |

### RailwaySegment

```python
class RailwaySegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    waypoints: list[Waypoint]                         # reuses same Waypoint model
    status: SegmentStatus
```

Railway segments claim corridors on the same node graph as canal segments. When a railway waypoint overlaps a canal waypoint: `canal_waypoint.blocked_by = "railway_claim"`, `canal_waypoint.status = BLOCKED`. No new blocking logic needed — it already exists.

### Railway corridor strategy (game/railway.py)

AI corridor selection priority:
1. Corridors where canal has active construction (contest them)
2. Corridors connecting major industrial nodes (high freight value)
3. Corridors that would split canal network connectivity if claimed

### Railway AI players

Use `claude/ai_player.py` with adversarial goal:
```
system: "You are [name], [role] of the Railway Syndicate. Your goal is to complete
the railway network before the canal party finishes theirs. Claim strategically
valuable corridors. Contest canal waypoints where railway routes would be more
efficient. Lobby the council to slow canal approvals."
```

Same `make_ai_decision()` function as canal AI players. Same code, opposite system prompt and goal.

### Map rendering for railway
Second React Flow edge type: `RailwayEdge` — dark iron-red lines vs canal's blue. Contested waypoint: amber warning marker. `InfluenceMeter` component shows both influence bars racing each other.

---

## Metrics & Economy

*Implements `prd.md > Metrics`*

### Metrics model

```python
class DepartmentBudget(BaseModel):
    finance: int = 10_000
    infrastructure: int = 5_000
    transport: int = 5_000

class Metrics(BaseModel):
    # Headline pair — prominent on central screen
    road_rage_index: float = 50.0
    canal_efficiency_index: float = 10.0             # starts low — partial canal
    aesthetic_index: float = 40.0                    # starts moderate — natural waterways exist

    # Quarterly panel
    citizen_happiness: float = 65.0                  # computed — see below
    horse_pollution: float = 30.0
    accidents_this_cycle: int = 0
    projects_delayed: int = 0
    tradies_nonbilling: int = 0

    # Freight split — must sum to 100
    road_freight_pct: float = 100.0
    canal_freight_pct: float = 0.0
    rail_freight_pct: float = 0.0

    # Economy
    economy_index: float = 50.0
    cycle_income: int = 0

    budget: DepartmentBudget = DepartmentBudget()

    # Election tracking
    election_polling: float = 65.0                   # lags citizen_happiness (inertia)
    cycles_survived: int = 0
```

### Metric recomputation sequence (each turn end)

```python
# game/map.py
def recompute_canal_efficiency(city_map, metrics):
    tier = check_canal_connectivity(city_map)
    base = metrics.canal_freight_pct * 0.8
    network_bonus = {CanalTier.BRONZE: 15, CanalTier.SILVER: 25, CanalTier.GOLD: 40}
    metrics.canal_efficiency_index = min(100.0, base + network_bonus.get(tier, 0))

# game/factions.py
def recompute_citizen_happiness(factions, metrics) -> float:
    faction_component = sum(f.happiness * f.population_weight for f in factions) \
                        / sum(f.population_weight for f in factions)
    aesthetic_component = metrics.aesthetic_index
    return (faction_component * 0.8) + (aesthetic_component * 0.2)

# game/engine.py
def recompute_economy(metrics) -> float:
    target = (metrics.canal_freight_pct * 1.2 +     # canal: goods-per-load advantage
              metrics.rail_freight_pct  * 0.9 +      # rail: efficient but rival
              metrics.road_freight_pct  * 0.4)       # road: slow, congested, costly
    new_economy = metrics.economy_index + (target - metrics.economy_index) * 0.25
    return max(0.0, min(100.0, new_economy))

def nudge_polling(metrics):
    metrics.election_polling += (metrics.citizen_happiness - metrics.election_polling) * 0.2
```

### Road Rage drivers and relievers (applied via METRIC_DELTA effects)

**Rises with:** congestion, delays, diversions, excessive tolls, accidents, horse volume, horse pollution events, restrictive road rules.  
**Falls with:** faster journeys, more route options, canal segments absorbing freight, road works completed.

### Horse pollution rule
Rises by a fixed amount each turn when `canal_efficiency_index < 30`. Falls as canal segments complete. Crosses 70 → public health report fires (Road Rage driver + election liability).

### Cycle-end income

```python
def apply_cycle_income(metrics: Metrics) -> None:
    income = int(BASE_INCOME * (metrics.economy_index / 100))
    metrics.budget.finance        += income // 2
    metrics.budget.infrastructure += income // 3
    metrics.budget.transport      += income // 6
    metrics.cycle_income = income
```

### Canal Mania

```python
class CanalMania(BaseModel):
    triggered: bool = False
    windfall_received: int = 0
    bubble_risk: float = 0.0
    bubble_burst: bool = False
```

Fires when `canal_freight_pct > 60%`. Finance receives large one-time windfall. `bubble_risk` rises each subsequent turn. If `bubble_risk > threshold` before stabilisation: crash report fires, `economy_index` drops sharply, merchant faction collapses.

---

## Factions & Aesthetic Index

*Implements `prd.md > Citizen Agents & Faction Reactions`*

### Faction model

```python
class Faction(BaseModel):
    faction_id: str
    name: str
    profile: str                                      # plain text — Claude's system prompt
    happiness: float = 60.0
    population_weight: float = 1.0                   # relative size for happiness weighting
    transport_priorities: list[str]
    political_sensitivities: list[str]
    reaction_threshold: float = 10.0
    canal_alignment: float = 0.0                     # -1.0 (oppose) to +1.0 (support)
    railway_alignment: float = 0.0
```

### Period-correct faction examples

| Faction | Canal alignment | Aesthetic sensitivity |
|---|---|---|
| Canal Workers' Guild | +0.9 | Very high — they live on the water |
| Angling Society | +0.7 | Very high — water quality is their activity |
| Canal Boat Families | +0.8 | Very high — the canal is their home |
| Natural Historians | +0.5 | High — documenting Victorian species |
| Carter's Association | -0.6 | Low — losing freight contracts to canal |
| Coach-travelling Gentry | -0.3 | Moderate — prefer road speed |
| Turnpike Trust Shareholders | -0.5 | Low — toll road revenue threatened |
| Railway Investors | -0.8 | Negative — see aesthetic as obstruction |
| Waterside Tavern Keepers | +0.4 | Moderate — canal foot traffic is trade |
| Merchants & Street Traders | +0.5 | Moderate — cheaper goods movement |

### Faction reaction generation (claude/citizens.py)

```python
async def generate_faction_reaction(faction, turn_summary, game_state) -> FactionReaction:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=350,
        system=faction.profile,                       # faction IS the system prompt
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": GAME_CONTEXT_BLOCK,
                 "cache_control": {"type": "ephemeral"}},  # cached
                {"type": "text", "text": f"Turn {game_state.turn}. {turn_summary}. React in character."}
            ]
        }],
        tools=[faction_reaction_tool]
    )
```

Only factions whose `political_sensitivities` overlap with this turn's effects receive a Claude call. Checked before calling — no wasted API calls.

```python
class FactionReaction(BaseModel):
    faction_id: str
    reaction_text: str
    happiness_delta: float
    triggered_by: str
    severity: Literal["minor", "moderate", "major"]
    display_on: list[str]                             # ["central_screen", "player_phone_P1"]
```

### Aesthetic Index

Starts at 40.0 — natural waterways pre-exist the canal. Building well enhances what's there; building carelessly destroys it.

**Raises aesthetic:** canal segment complete at standard pace (+5), amenity waypoint complete (+8), pleasure boat licence approved (+4), engineering feat (aqueduct) completed (+6), construction paced for habitat (+3), waterfowl nesting protected (+5).

**Lowers aesthetic:** rushed construction (+6), horse pollution into canal (-4), Canal Mania overbuilding (-5), railway segment built adjacent to canal (-3), industrial effluent ignored (-8), agent cuts corners (-4).

**Aesthetic faction economic effects (when canal freight rises):**

| Faction | Effect |
|---|---|
| Canal Workers' Guild | happiness +, wages implied rising |
| Carter's Association | happiness -, freight contracts lost |
| Merchants | happiness +, cheaper goods movement |
| Railway Investors | canal_alignment drops |

### Heritage Commendation win state

Awarded if `aesthetic_index >= 70` at game end, regardless of canal tier:
*"The people's canal — a working waterway and a living landscape, remembered for generations."*

Stacks with canal completion tiers. Gold + Heritage = highest possible achievement.

### Faction and councillor generation (claude/map_gen.py)

Factions and councillors generated at startup alongside the city map — same Claude call. `profile` text becomes the Claude system prompt for faction reactions and AI player decisions. Profiles include historical context (era, cultural background, economic stakes) so Claude generates period-appropriate dialogue automatically.

---

## Reports & Turn Loop

*Implements `prd.md > Turn Structure & Decision-Making`*

### Report model

```python
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

class Report(BaseModel):
    report_id: str
    title: str
    description: str                                  # Claude-generated narrative
    report_type: ReportType
    addressed_to: str                                 # player_id
    domain: CouncilRole
    options: list[ReportOption]                       # 1–4 options
    status: ReportStatus = ReportStatus.PENDING
    is_private: bool = True
    delegation_candidates: list[str] = []             # agent_ids eligible for this report
    delegated_to: str | None = None
    decision: str | None = None                       # option_id chosen
    conflict_with: str | None = None                  # conflicting report_id
    defer_count: int = 0
    deferred_until_turn: int | None = None
    deferral_consequences: list[str] = []
    escalated_to_council: bool = False
    urgent: bool = False                              # if True, cannot be deferred
    turn_received: int
    turn_deadline: int
```

### ReportOption

```python
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ReportOption(BaseModel):
    option_id: str
    label: str
    description: str
    effects: list[Effect]
    risk_level: RiskLevel
    agent_only: bool = False                          # only visible when delegating
    is_forced: bool = False                           # single-option forced acknowledgment
    value_signals: list[str] = []                     # ["workers_rights", "heritage", "fiscal_prudence"]
    min_skill_level: float = 0.0                      # skill gate — higher skill sees more options
    required_skill: str | None = None
```

### Option count rules

| Count | Meaning |
|---|---|
| 1 | Forced acknowledgment — something is happening to the council |
| 2–3 | Standard decision |
| 4 | Agent-researched or complex council matter |

### Player action set (40-second window)

| Action | Available when |
|---|---|
| Choose option | Always |
| Delegate → pick agent | Agent available in domain |
| Research alternatives | Agent available + fewer than 3 options |
| Defer | Not urgent, `defer_count < 2` |
| Flag for council | Any report |
| Council extension | `council_extensions_remaining > 0`, not during vote |

### Deferral rules

- Active political choice, not passive timeout
- Small `election_polling` penalty (-2) — public sees indecision
- Cannot defer `urgent: True` reports
- Deferred twice → auto-escalates to council on third turn
- Problem persists and may worsen while deferred

### Research alternatives

```python
ReportOption(
    option_id="research_alternatives",
    label="Ask [Agent Name] to find more options",
    description="Costs one turn. Agent may surface 1–2 additional options.",
    effects=[Effect(effect_type=EffectType.REPORT_GENERATE, target_type=TargetType.METRIC,
                    target_id="self", value=1, delay_turns=1)],
    risk_level=RiskLevel.LOW
)
```

### Report generation (claude/events.py)

```python
async def generate_report(domain, trigger, game_state) -> Report:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=700,
        system=GAME_MASTER_PROMPT,                    # cached
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": STATIC_DOMAIN_CONTEXT[domain],
                 "cache_control": {"type": "ephemeral"}},   # cached per domain
                {"type": "text", "text": f"Trigger: {trigger}. State: {game_state.to_context_summary()}"}
            ]
        }],
        tools=[report_generation_tool]
    )
```

Docs for tool use: https://docs.anthropic.com/en/docs/build-with-claude/tool-use

### Conflict detection (game/engine.py)

After each decision submitted, server checks all pending decisions from other players for resource conflicts (same canal segment, same budget line, same agent). On conflict: both reports paused, `Vote` created, `pending_vote` set, `vote_called` event broadcast.

### Council vote

```python
class Vote(BaseModel):
    vote_id: str
    report_ids: list[str]                             # conflicting reports
    initiated_by: str                                 # player_id or "system"
    options: list[ReportOption]
    votes: dict[str, str] = {}                        # player_id → option_id
    status: Literal["pending", "resolved"] = "pending"
    result: str | None = None
    mayor_tiebreaker: bool = False
```

Mayor NPC breaks 1–1 ties. Vote result displayed on central screen's `VotePanel`.

### Council extensions

```python
# Any player can spend an extension via button or voice
# server: council_extensions_remaining -= 1
# server: add 30 seconds to active timer
# broadcast: updated timer to all clients
# effect: election_polling -= 2
# event_log: COUNCIL_EXTENSION logged
```

---

## Effects System

*Applied by game/engine.py at turn end. Supports immediate and delayed effects.*

### TargetType

```python
class TargetType(str, Enum):
    METRIC = "metric"              # target_id: metric name ("road_rage_index", etc.)
    FACTION = "faction"            # target_id: faction_id
    SEGMENT = "segment"            # target_id: segment_id
    WAYPOINT = "waypoint"          # target_id: waypoint_id
    RAILWAY_PARTY = "railway_party"  # target_id: "singleton"
    CANAL_PARTY = "canal_party"      # target_id: "singleton"
    PLAYER = "player"              # target_id: player_id
    AGENT = "agent"                # target_id: agent_id
    ECONOMY = "economy"            # target_id: "singleton"
    FREIGHT_ROAD = "freight_road"  # target_id: "singleton"
    FREIGHT_CANAL = "freight_canal"
    FREIGHT_RAIL = "freight_rail"
    CYCLE_INCOME = "cycle_income"
# Future upgrade: replace target_type + target_id with Pydantic discriminated union
# (see spec-session-log.md section 7 for full upgrade path)
```

### EffectType

```python
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
```

### Effect

```python
class Effect(BaseModel):
    effect_type: EffectType
    target_type: TargetType
    target_id: str
    value: float | str
    delay_turns: int = 0
    description: str
```

### Effect routing (game/engine.py)

```python
def apply_effect(effect: Effect, game_state: GameState) -> None:
    match effect.target_type:
        case TargetType.FACTION:
            faction = game_state.get_faction(effect.target_id)   # KeyError = loud failure
            faction.happiness += effect.value
        case TargetType.SEGMENT:
            segment = game_state.city_map.canal_segments[effect.target_id]
            ...
        case TargetType.CANAL_PARTY:
            game_state.canal_party.influence += effect.value
        case TargetType.RAILWAY_PARTY:
            game_state.railway_party.influence += effect.value
        case TargetType.METRIC:
            setattr(game_state.metrics, effect.target_id,
                    getattr(game_state.metrics, effect.target_id) + effect.value)
```

### Pending effects queue

Effects with `delay_turns > 0` are stored in `game_state.pending_effects` as `(apply_at_turn, effect)`. Each turn, engine applies all effects where `apply_at_turn == game_state.turn`.

---

## Agent & Delegation System

*Implements `prd.md > Agent Hiring & Delegation`*

### Agent model

```python
class Agent(BaseModel):
    agent_id: str
    name: str
    domain: CouncilRole
    specialisations: list[str]
    risk_profile: float = 0.5                        # 0.0 (cautious) → 1.0 (aggressive)
    track_record: int = 0                            # successful delegations; improves outcomes
    hiring_cost: int
    active: bool = True
```

### Agent domains

- **Finance:** analysts, assessors, loan brokers
- **Infrastructure:** engineers, surveyors, construction crews
- **Transport:** route planners, canal inspectors, freight coordinators

### Delegation outcome resolution (game/agents.py)

```python
def resolve_delegation(report: Report, agent: Agent) -> ReportOption:
    # Higher risk_profile → wider spread of outcomes
    # Better track_record → skews toward better outcomes
    # May select agent_only options unavailable to the player directly
    # Poor outcomes generate new AGENT_OUTCOME reports next turn
```

Outcome arrives as a new `AGENT_OUTCOME` report next turn. Agent reports back on what they did and what happened. Poor decisions create new problem reports downstream.

### Hire / retire agents (game/agents.py)

Hiring costs departmental budget. Retiring frees budget. Agent profile shows abilities, specialisations, risk profile. Player chooses which agent to delegate to — not automatic.

---

## Councillor System

*Implements `prd.md > Game Setup` (councillor selection)*

### Councillor model

```python
class CouncillorSkill(BaseModel):
    skill_name: str
    description: str                                  # Claude-generated
    level: float = 1.0                               # grows from 1.0 upward
    experience_points: int = 0

class Councillor(BaseModel):
    councillor_id: str
    name: str
    role: CouncilRole

    # Three defining axes — semi-randomly generated by Claude at startup
    political_alignment: str
    core_values: list[str]
    professional_background: str
    value_tension: str                               # the competing-goods tension within

    skills: list[CouncillorSkill]
    decisions_made: int = 0
    value_aligned_decisions: int = 0
    milestones_achieved: list[str] = []

    profile: str                                     # full text — Claude system prompt for AI players
```

### Councillor generation

12 councillors generated at startup alongside city map and factions (same Claude call, same tool-use pipeline). 4 per role (Finance / Infrastructure / Transport). Semi-random — different every game. Profiles become Claude system prompts for AI players.

### Skill growth

```python
def award_councillor_experience(councillor, action_type, was_value_aligned, milestone_achieved=False):
    xp = 10
    if was_value_aligned: xp += 5    # consistency with values accelerates growth
    if milestone_achieved: xp += 25
    relevant_skill = find_relevant_skill(councillor, action_type)
    if relevant_skill:
        relevant_skill.experience_points += xp
        relevant_skill.level = 1.0 + (relevant_skill.experience_points / 100)
    councillor.decisions_made += 1
    if was_value_aligned:
        councillor.value_aligned_decisions += 1
```

### Value alignment check

Report options tagged with `value_signals: list[str]`. Engine checks overlap with `councillor.core_values` — simple string matching, no Claude call needed. Aligned decision → XP bonus applied automatically.

### Skill effects

Higher skill level gates additional report options via `min_skill_level` on `ReportOption`. Novice sees 2 options; skilled councillor sees a third creative approach only experience reveals.

---

## Elections & Win States

*Implements `prd.md > Elections`, `prd.md > Game End`*

### Election resolution (game/elections.py)

```python
LOSS_THRESHOLD = 40.0    # election_polling below this = game over

def check_cycle_end(game_state: GameState) -> None:
    if game_state.turn < 20:
        return
    if game_state.metrics.election_polling < LOSS_THRESHOLD:
        trigger_game_over(game_state, reason="election_loss")
    else:
        game_state.metrics.cycles_survived += 1
        if game_state.cycle >= game_state.game_length:
            trigger_win(game_state)
        else:
            game_state.cycle += 1
            game_state.turn = 1
            apply_cycle_income(game_state.metrics)
```

### Win state matrix

| Canal completion | Elections survived | Outcome |
|---|---|---|
| None | All cycles | Survived (no canal legacy) |
| Bronze+ | All cycles | Modest win |
| Silver | All cycles | Strong win |
| Gold | All cycles | Celebration — canal era complete |
| Gold + Aesthetic ≥ 70 | All cycles | Gold + Heritage Commendation |
| Any | Lost election | Hard game over |

```python
class WinState(BaseModel):
    outcome: Literal["game_over", "survived", "modest_win", "strong_win",
                     "celebration", "heritage_commendation"]
    canal_tier: CanalTier
    heritage_commendation: bool = False
    cycles_survived: int
    epitaph: str                                     # Claude-generated end screen text
```

### Game end replay data

`event_log` filtered by type for replay:
- Canal time-lapse: `WAYPOINT_COMPLETE`, `SEGMENT_COMPLETE`, `WAYPOINT_BLOCKED`, `NETWORK_EFFECT`, milestones
- Election history: `ELECTION_SURVIVED`, `GAME_OVER`
- Personal scorecards: filter by `player_id` — `MAJOR_DECISION`, `AGENT_SUCCESS`, `AGENT_FAILURE`
- Shared moments: `FACTION_SWING`, `COUNCIL_EXTENSION`, `RAILWAY_ACTIVATED`

```python
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

class GameEvent(BaseModel):
    event_id: str
    event_type: GameEventType
    turn: int
    cycle: int
    description: str
    player_id: str | None = None
    data: dict = {}
```

---

## Voice Commands

*Implements `prd.md > Voice Commands`*

### Web Speech API (frontend — useVoiceInput.ts)

```typescript
export function useVoiceInput(onTranscript: (text: string) => void) {
    const startListening = () => {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-NZ';
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            if (confidence < 0.6) {
                showConfirmation(`Did you mean: "${transcript}"?`);
            } else {
                onTranscript(transcript);
            }
        };
        recognition.onerror = () => showTextInput("Voice unavailable — type your command:");
        recognition.start();
    };
    return { startListening };
}
```

Requires Chrome or Edge. Works without any API key or cost.

### Voice command flow

```
Player taps mic → Web Speech API → transcript string
    ↓
socket.emit('voice_command', { player_id, text: transcript })
    ↓
Server: claude/voice.py → parse_voice_command()
    ↓
ParsedCommand returned → same path as button action
```

### ParsedCommand model

```python
class ParsedCommand(BaseModel):
    action_type: str
    target_type: TargetType | None = None             # same disambiguation as Effect
    target_id: str | None = None
    parameters: dict = {}
    confidence: float
    clarification_needed: bool = False
    clarification_prompt: str | None = None
```

### Voice parsing (claude/voice.py)

```python
async def parse_voice_command(transcript, player, game_state) -> ParsedCommand:
    available_actions = get_domain_actions(player.role, game_state)
    response = await client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=[{"name": "dispatch_command",
                "input_schema": ParsedCommand.model_json_schema()}],
        messages=[{"role": "user", "content":
            f'Player: {player.name}, Role: {player.role.value} councillor\n'
            f'They said: "{transcript}"\n'
            f'Available actions for this domain:\n{available_actions}\n'
            f'Parse into a game action. Domain scoped — cannot issue commands outside their role.'}]
    )
    return ParsedCommand.model_validate(response.content[0].input)
```

---

## Claude Integration

*All Claude calls live in backend/claude/ — game engine never touches the SDK directly.*

### Shared client (claude/client.py)

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()                             # reads ANTHROPIC_API_KEY from env
MODEL = "claude-sonnet-4-6"
```

### Prompt caching

Static content (faction profiles, game rules, domain descriptions) marked `cache_control: {"type": "ephemeral"}`. Cache TTL: 5 minutes — correct window for a live game session. Saves ~80% of those tokens after first call.

Docs: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

### Concurrent calls (asyncio.gather)

```python
async def resolve_turn_end(game_state, turn_summary):
    affected = [f for f in game_state.factions if faction_affected(f, turn_summary)]
    reactions = await asyncio.gather(*[
        generate_faction_reaction(f, turn_summary, game_state) for f in affected
    ])
    next_reports = await asyncio.gather(
        generate_report(CouncilRole.FINANCE, ..., game_state),
        generate_report(CouncilRole.INFRASTRUCTURE, ..., game_state),
        generate_report(CouncilRole.TRANSPORT, ..., game_state)
    )
```

Target: full turn-end processing under 5 seconds. Central screen shows "Council deliberating..." during this window.

### Token limits per call type

| Call type | Safe limit | Fallback |
|---|---|---|
| Voice command | 300 | 500 |
| Faction reaction | 350 | 600 |
| Report generation | 700 | 1200 |
| Map / councillor generation | 3000 | 5000 |

### Truncation handling

```python
async def safe_claude_call(kwargs, fallback_tokens) -> Message:
    response = await client.messages.create(**kwargs)
    if response.stop_reason == "max_tokens":
        kwargs['max_tokens'] = fallback_tokens
        response = await client.messages.create(**kwargs)
    return response
```

Catch `ValidationError` on tool use parsing — incomplete JSON = truncation signal → retry.

### Admin cost monitoring (claude/client.py)

```python
@dataclass
class UsageRecord:
    call_type: str   # "voice" | "faction" | "report" | "map_gen" | "ai_player"
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    turn: int
    cycle: int

    @property
    def cost_usd(self) -> float:
        return (self.input_tokens * 0.000003 + self.output_tokens * 0.000015 +
                self.cache_write_tokens * 0.00000375 + self.cache_read_tokens * 0.0000003)
```

Endpoint: `GET /admin/usage?token=ADMIN_TOKEN`  
Returns: total cost, by call type, cache hit rate, estimated full-game cost.  
Target cache hit rate: >60%. Below 40% = prompt structure needs fixing.  
Estimated cost per full game session: $1.50–$3.00.

Anthropic pricing docs: https://www.anthropic.com/pricing

---

## AI Players

*Implements solo testing and playable demo without additional human players.*

### Setup

Grant plays Transport. Finance and Infrastructure are AI-controlled.

```python
# Game setup: human_player_role = TRANSPORT
# AI players assigned to FINANCE and INFRASTRUCTURE automatically
```

### AI decision making (claude/ai_player.py)

```python
async def make_ai_decision(player, report, game_state) -> PlayerAction:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=f"""You are {player.councillor.name}, {player.role.value} councillor.
        {player.councillor.profile}
        This is a cooperative game. Your shared goal: complete the canal network
        before the railway party gains dominance. Survive every election together.""",
        messages=[{"role": "user", "content": build_ai_context(player, report, game_state)}],
        tools=[ai_decision_tool]
    )
```

2-second delay before applying AI decisions — feels like genuine simultaneous deliberation.

### AI difficulty

- **Easy:** effects visible in prompt, safe choices apparent
- **Medium:** effects shown, no guidance
- **Hard:** raw options only, Claude must reason from game state

### Visibility

AI decisions appear in central screen event feed with AI badge (`🤖`). Grant needs to see them to understand and test game flow.

### Railway AI players

Same `make_ai_decision()` function. Different system prompt — adversarial goal. Corridor strategy from `game/railway.py` drives which segments they build; Claude handles individual turn decisions.

---

## Frontend — Central Screen

*Route: `/central`*

### CityMap.tsx

React Flow graph rendering. Docs: https://reactflow.dev/learn

```typescript
const nodes = Object.values(gameState.cityMap.nodes).map(n => ({
    id: n.node_id,
    position: { x: n.position[0] * WIDTH, y: n.position[1] * HEIGHT },
    type: 'districtNode',
    data: n
}));

const edges = Object.values(gameState.cityMap.canalSegments).flatMap(seg =>
    seg.waypoints.map((wp, i) => ({
        id: `${seg.segment_id}-${i}`,
        source: i === 0 ? seg.from_node : `${seg.segment_id}-wp-${i - 1}`,
        target: wp.waypoint_id,
        type: 'canalEdge',
        data: wp
    }))
);
```

Custom node: `DistrictNode.tsx` — district type, name, construction state, railway station badge.  
Custom edge: `CanalEdge.tsx` — waypoints, progress markers, blockage warning, contested indicator.  
Custom edge: `RailwayEdge.tsx` — dark iron-red, locomotive icon on complete sections.  
Custom marker: `WaypointMarker.tsx` — individual waypoint dot, status colour-coded.

### MetricsDash.tsx

Displays: Road Rage Index, Canal Efficiency Index, Aesthetic Index (three headline metrics), quarterly panel (citizen happiness, horse pollution, accidents, projects delayed, tradies non-billing), department budgets.

### InfluenceMeter.tsx

Two bars racing each other: Canal Party influence vs Railway Party influence. Dramatic visual when they approach crossover. Railway crisis fires if railway overtakes canal.

### EventFeed.tsx

Scrolling feed of faction reactions, milestone toasts, AI player decisions (with badge), council extension announcements, error events.

### VotePanel.tsx

Appears when `pending_vote` is non-null. Shows conflicting reports, options, live vote tally as players cast, result announcement, mayor tiebreaker indicator.

---

## Frontend — Player Phone

*Route: `/phone`*

### ReportQueue.tsx

All pending reports for this player's role. Filtered from full game state by `player_id`. Shows: report title, domain badge, urgency indicator, defer count, time remaining.

### ReportCard.tsx

Single report detail. Shows: title, description, options (filtered by skill level), delegation picker (if agent available), defer/escalate buttons, research alternatives (if fewer than 3 options + agent available).

### AgentRoster.tsx

All agents in player's domain. Shows: name, specialisations, risk profile indicator, track record, hiring cost, active/retired status. Delegation picker opens from here when player taps "Delegate" on a report.

### VoiceButton.tsx

Mic button. Calls `useVoiceInput` hook. On success: sends transcript over WebSocket. On low confidence: shows confirmation prompt. On failure: shows text input fallback automatically.

### TurnTimer.tsx

Countdown display. Timer is server-authoritative — client receives `turn_started` event with duration, counts down locally for display only. Server controls actual turn end.

### ExtensionButton.tsx

Shows `council_extensions_remaining`. Disabled when 0 or during a vote. On press: emits `council_extension` event. Broadcasts +30 seconds to all clients.

---

## Frontend — Shared Components & Hooks

### DevPanel.tsx

Hidden overlay. Activated by `Ctrl+Shift+D`. Only rendered when `import.meta.env.DEV` is true — invisible in production builds and to judges.

Contents: scenario buttons, fast-forward (+1/+5 turns, +1 cycle), metric sliders (railway influence, aesthetic index, election polling), save/restore buttons.

### useVoiceInput.ts

Web Speech API wrapper. Returns `{ startListening }`. Handles: confidence check, text fallback on error, `en-NZ` locale.

### useSocket.ts

socket.io-client connection lifecycle. Registers player identity on connect. Handles reconnection with session_id check.

### useGameState.ts

Consumes game state from React Context. Returns typed slice relevant to current component.

### store.ts (React Context)

Holds: full `GameState` mirror (updated on every `game_state_update` event), player identity (`player_id`, `role`, `session_id` from localStorage).

---

## Real-time Communication

### WebSocket event dictionary

| Direction | Event | Payload | Triggers |
|---|---|---|---|
| Client → Server | `register` | `{client_type, player_id, role, session_id}` | On connect |
| Client → Server | `player_action` | `{player_id, action_type, target_type, target_id, option_id}` | Report decision |
| Client → Server | `voice_command` | `{player_id, text}` | Voice transcript |
| Client → Server | `council_extension` | `{player_id}` | Extension button |
| Client → Server | `new_game` | `{game_length}` | Host on central screen |
| Server → Client | `game_state_update` | Full `GameState` JSON | After any change |
| Server → Client | `council_processing` | `{turn, cycle}` | Turn-end Claude calls started |
| Server → Client | `vote_called` | `Vote` object | Conflict detected |
| Server → Client | `milestone` | `{type, description}` | Canal milestone achieved |
| Server → Client | `game_over` | `{reason, win_state}` | Election lost or canal complete |

### Session reconnection

```
Phone reconnects → sends register with stored session_id
Server checks: session_id matches active game?
    YES → rejoin: emit full game_state to this socket only
    NO  → stale: redirect to setup screen
```

### Connection loss fallback cascade

```
Disconnect detected (socket.io fires event)
Free deferral on all pending reports
30-second reconnection window
    ↓
Reconnects? → session restored, reports still pending
Doesn't? → agent available in domain? → agent resolves
         → no agent? → first option selected
    ↓
GameEvent.CONNECTION_LOST logged
election_polling -= 1
Event feed: "[Player] acting on first available option"
```

---

## Admin & Dev Mode

*Protected by ADMIN_TOKEN in .env. Not visible to players or judges.*

### Admin endpoints (api/admin.py)

```
GET  /admin/usage?token=X           → Claude usage report (cost, cache rate, by type)
POST /admin/seed/{scenario}?token=X → load named game state scenario
POST /admin/set?token=X             → set metric values by dot-path
POST /admin/advance-turn?turns=N&token=X → skip N turns (AI decides everything)
POST /admin/save?slot=X&token=X     → save state to saves/{slot}.json
POST /admin/load?slot=X&token=X     → restore state from saves/{slot}.json
GET  /admin/state?token=X           → dump full current game state
GET  /health                        → uptime check (no auth)
```

### Named scenarios (game/scenarios.py)

```python
SCENARIOS = {
    "fresh":              scenario_fresh_game,
    "canal_progress":     scenario_canal_progress,        # turn 15, cycle 1, half-built
    "railway_activation": scenario_railway_activation,    # influence at 38
    "canal_mania":        scenario_canal_mania,           # network near critical mass
    "election_pressure":  scenario_election_pressure,     # turn 18, polling at 45
    "heritage":           scenario_heritage,              # aesthetic index 75
    "crisis":             scenario_full_crisis,           # everything going wrong
}
```

Each scenario builds on the AI-generated city map — sets metrics, completes segments, adjusts turn/cycle. Does not replace the map.

### Save/load

JSON files in `backend/saves/` (gitignored). Also serves as crash recovery during the demo — if server restarts, `POST /admin/load?slot=quicksave` restores last saved state and broadcasts to all clients.

### Error resilience fallbacks

**Claude timeout (8-second limit):**
- Faction reactions: generic template, happiness_delta = 0
- Report generation: draw from pre-written pool in scenarios.py
- Voice parsing: `clarification_needed: True`, phone shows "Tap your choice"
- AI player decision: first available option selected

**Web Speech API failure:**
- Low confidence: show transcript, ask confirmation
- Complete failure: auto-switch to text input (same WebSocket path)

All failures logged as `GameEvent` with appropriate type. Admin report shows timeout frequency.

---

## File Structure

```
civic-engine/
├── backend/
│   ├── main.py                       # FastAPI app, socket.io setup, WebSocket handlers
│   ├── config.py                     # env vars, BASE_INCOME, ADMIN_TOKEN, game constants
│   ├── game/
│   │   ├── __init__.py
│   │   ├── state.py                  # ALL Pydantic models (single import for /build)
│   │   ├── engine.py                 # turn resolution, effect application, win checks
│   │   ├── map.py                    # networkx canal connectivity, freight recompute
│   │   ├── factions.py               # faction filtering, happiness weighting
│   │   ├── reports.py                # report scheduling, threshold triggers
│   │   ├── agents.py                 # hire/retire, delegation outcome resolution
│   │   ├── elections.py             # cycle-end logic, polling, hard game over
│   │   ├── railway.py                # railway AI corridor selection strategy
│   │   └── scenarios.py             # named dev/test seed functions + pre-written reports
│   ├── claude/
│   │   ├── __init__.py
│   │   ├── client.py                 # shared AsyncAnthropic client, UsageTracker
│   │   ├── voice.py                  # transcript → ParsedCommand (tool use)
│   │   ├── citizens.py               # faction reaction generation (concurrent)
│   │   ├── events.py                 # report/event generation per domain
│   │   ├── ai_player.py              # canal AI (cooperative) + railway AI (adversarial)
│   │   └── map_gen.py                # city map, factions, councillors at startup ← MCP candidate
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py                  # /admin/* endpoints (usage, seed, set, save, load)
│   │   └── health.py                 # GET /health
│   ├── saves/                        # JSON save slots — gitignored
│   ├── requirements.txt
│   ├── .env                          # ANTHROPIC_API_KEY, ADMIN_TOKEN — never commit
│   └── .env.example                  # safe template for repo
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                  # React entry point
│   │   ├── App.tsx                   # routing: /central → CentralScreen, /phone → PlayerPhone
│   │   ├── socket.ts                 # socket.io-client, single shared connection
│   │   ├── store.ts                  # React Context: game state mirror + player identity
│   │   ├── types.ts                  # AUTO-GENERATED — run npm run generate-types
│   │   ├── views/
│   │   │   ├── CentralScreen/
│   │   │   │   ├── index.tsx         # layout: map left, metrics right, event feed bottom
│   │   │   │   ├── CityMap.tsx       # React Flow: DistrictNode + CanalEdge + RailwayEdge
│   │   │   │   ├── MetricsDash.tsx   # Road Rage, Canal Efficiency, Aesthetic + quarterly panel
│   │   │   │   ├── InfluenceMeter.tsx # canal vs railway influence race bar
│   │   │   │   ├── EventFeed.tsx     # faction reactions, milestones, AI decisions
│   │   │   │   └── VotePanel.tsx     # council vote display + live tally + result
│   │   │   └── PlayerPhone/
│   │   │       ├── index.tsx         # layout, role-filtered councillor view
│   │   │       ├── ReportQueue.tsx   # all pending reports for this player
│   │   │       ├── ReportCard.tsx    # report + options + action buttons
│   │   │       ├── AgentRoster.tsx   # hire/retire + delegation picker
│   │   │       ├── VoiceButton.tsx   # mic + Web Speech API + text fallback
│   │   │       ├── TurnTimer.tsx     # countdown (display only — server is authoritative)
│   │   │       └── ExtensionButton.tsx # council extension + remaining count
│   │   ├── components/
│   │   │   ├── DistrictNode.tsx      # React Flow custom node
│   │   │   ├── CanalEdge.tsx         # React Flow custom canal edge (waypoints)
│   │   │   ├── RailwayEdge.tsx       # React Flow custom railway edge
│   │   │   ├── WaypointMarker.tsx    # individual waypoint status on map edge
│   │   │   ├── FactionCard.tsx       # faction name, happiness bar, reaction text
│   │   │   └── DevPanel.tsx          # hidden dev overlay (Ctrl+Shift+D, DEV only)
│   │   └── hooks/
│   │       ├── useVoiceInput.ts      # Web Speech API: startListening → onTranscript
│   │       ├── useSocket.ts          # connection lifecycle, event registration
│   │       └── useGameState.ts       # consume game state from Context
│   ├── index.html
│   ├── package.json                  # includes generate-types + dev scripts
│   └── vite.config.ts
│
├── docs/
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   ├── spec.md                       # ← this document
│   └── spec-session-log.md           # full design conversation record
├── process-notes.md
└── README.md
```

---

## Key Technical Decisions

### 1. City map as a graph, not a grid
**Decided:** City districts are graph nodes; canal routes are edges with ordered waypoints as sub-nodes.  
**Why:** Canal connectivity (Bronze/Silver/Gold tiers, network effect, spatial competition with railway) are all graph questions. NetworkX handles connectivity in two lines of code.  
**Tradeoff accepted:** More complex data model than a grid; no spatial queries possible (but none needed).

### 2. Waypoints as sub-nodes (Option B)
**Decided:** Canal segments have an ordered list of named, typed waypoints rather than a simple progress percentage.  
**Why:** Multiple simultaneous blockages, named historical locations, railway spatial competition at specific points, AQUEDUCT type triggers engineering feat automatically.  
**Tradeoff accepted:** ~4–5 hours extra build time over the simpler model. Grant accepted this explicitly.  
**Future upgrade:** Waypoints can become full graph nodes when the network grows to full game scale.

### 3. Target type disambiguation on Effect and ParsedCommand
**Decided:** Every `target_id` is accompanied by a `target_type` enum that routes the engine to the correct entity namespace before lookup.  
**Why:** Plain string IDs are a collision risk — a faction "C4" and a segment "C4" would be indistinguishable without the type field. Identified independently by Grant as a real bug risk.  
**Tradeoff accepted:** Option A (two fields) over Option B (discriminated unions) — same safety, lower complexity for a hackathon build. Upgrade path documented in spec-session-log.md section 7.

---

## Dependencies & External Services

| Service | Purpose | Key docs | Auth |
|---|---|---|---|
| Anthropic API | Claude for voice parsing, citizen reactions, event generation, AI players, map generation | https://docs.anthropic.com/en/api | `ANTHROPIC_API_KEY` |
| FastAPI | Backend web framework + OpenAPI schema | https://fastapi.tiangolo.com/ | None |
| python-socketio | Real-time WebSocket communication | https://python-socketio.readthedocs.io/ | None |
| NetworkX | Canal network graph connectivity | https://networkx.org/documentation/stable/ | None |
| React Flow | City map node-edge rendering | https://reactflow.dev/learn | None |
| openapi-typescript | TypeScript type generation from FastAPI schema | https://openapi-ts.dev/ | None |
| Web Speech API | Browser voice input (no cost, no key) | https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API | None — Chrome/Edge only |

**Estimated Claude API cost per full game session:** $1.50–$3.00 with prompt caching. Monitor via `GET /admin/usage`.

**No external database required.** Game state held in server memory. Persistence via JSON save files in `backend/saves/`.

---

## Open Issues

From `prd.md > Open Questions` — deferred to build:

1. **Starting canal state** — How many stubs exist at game start, and which segments? The AI map generator decides, but the prompt needs specific guidance. Resolve during `claude/map_gen.py` implementation.

2. **Faction count for demo** — How many factions in the opening dossier? Suggest 4–6 for demo (canal workers, carter's association, railway investors, angling society, merchants, coach-travelling gentry). Tune during `claude/map_gen.py` implementation.

3. **Agent failure mechanics** — When an agent decision goes wrong, what exactly fires next turn? New problem report, construction delay, or budget overrun? Recommend: all three are possible outcomes, weighted by agent risk_profile. Decide exact weights during `game/agents.py` implementation.

4. **Horse pollution mechanic** — Periodic event, threshold metric, or constant Road Rage modifier? Recommend: constant modifier (rises/falls with `road_freight_pct`) plus a threshold event at 70 that fires a public health report. Resolve during `game/reports.py` implementation.

5. **Canal Mania bubble burst mechanics** — What exactly happens when `bubble_risk` crosses threshold? Recommend: large `BUDGET_DELTA` hit to Finance, `economy_index` sharp drop, merchant faction happiness collapse, `CANAL_MANIA_BURST` event card. Resolve during `game/engine.py` implementation.

6. **Arrow function syntax** — Grant flagged unfamiliarity with TypeScript arrow functions / array methods during the spec session. Walk through the `types.ts` mapping and React Flow node/edge transforms during `/build` before expecting him to write them independently.

7. **Railway party influence growth rate** — Specific formula for how fast influence grows based on canal progress not yet defined. Recommend: `influence += (1 - canal_freight_pct/100) * 2.5` per turn — faster growth when canal is underperforming. Tune during `game/railway.py` implementation.

8. **Election loss threshold** — 40.0 used as placeholder. May need tuning based on how quickly `citizen_happiness` moves in practice. Test during dev mode with `election_pressure` scenario.
