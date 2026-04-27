# Civic Engine — Spec Session Design Log

*A full record of the /spec design conversation for future reference. Organized by topic. Read this alongside docs/spec.md to understand the reasoning behind every architectural decision.*

---

## 1. Stack Decisions

### What was chosen
- **Backend:** Python + FastAPI (v0.136.1)
- **Frontend:** React + Vite + TypeScript
- **Real-time:** python-socketio (FastAPI ASGI compatible)
- **AI:** Anthropic Python SDK (v0.80.0)
- **Map rendering:** React Flow (@xyflow/react)
- **Graph algorithms:** NetworkX (Python)

### Why not C#
Grant asked about C#. Ruled out because Anthropic's official SDKs are Python and TypeScript — C# would mean unofficial Claude tooling and building a web UI in an ecosystem not naturally at home there. Fighting the tooling rather than building the game.

### Why FastAPI over Flask or Django
FastAPI is typed, structured, and async-native — closest to what a C# developer would expect from a web framework. Pydantic models feel like C# data classes. Native async support handles concurrent Claude calls cleanly.

### Why TypeScript over JavaScript
Grant preferred TypeScript specifically. Coming from C#, types and interfaces are natural. TypeScript is significantly closer to C# than JavaScript is.

### Deployment decision
Local development for the hackathon. Architecture designed to be cloud-deployable (no hardcoded localhost, environment variables for secrets, proper CORS config) but deployment not attempted during the build. Railway.app identified as the right target for future deployment — supports FastAPI + WebSocket apps, but no permanent free tier as of 2026 (30-day trial, then $5/month).

---

## 2. Client/Server Architecture

### The fundamental split
The server (Python/FastAPI) is the single source of truth and runs all game logic. The clients (React) are purely display and input — they render what the server sends and forward user inputs to the server. Claude is only ever called from the server side, never from the browser.

Grant independently identified the key analogy: React is like a Unity UI Canvas. Python is the GameManager.

### Two client types
- **Central screen** — `/central` route, shows city map, metrics, events, votes, railway meter
- **Player phone** — `/phone` route, shows that player's reports, agent roster, voice button, turn timer

Both are the same React app on different routes. The server broadcasts full game state to all clients; each client knows its own player identity and filters what to display.

### Session identity
Each phone browser stores in localStorage:
```
player_id: "P2"
role: "Infrastructure"
session_id: "a3f9..."   ← matches server's active session UUID
```

On connection, clients register their identity with the server. The server maps socket connection IDs to player IDs. On reconnection, session_id is checked — if it matches the active game, the player rejoins seamlessly; if not, they go to the setup screen.

Grant independently identified the need for session identity before it was proposed — strong developer instinct.

### Game lifecycle states
```
LOBBY → SETUP → IN_GAME → GAME_OVER
```

New game triggered by host on central screen. Server broadcasts `new_game` event with fresh game state. React replaces its local state mirror. Player identity (player_id, role) persists in localStorage across games; game state is wiped.

---

## 3. Game State Data Model

### The core principle
One `GameState` Pydantic model lives in Python server memory. It serialises to JSON for WebSocket broadcast. Every client receives the same full state and renders the appropriate filtered view.

### Top-level structure
```python
class GameState(BaseModel):
    session_id: str
    status: GameStatus          # LOBBY | SETUP | IN_GAME | GAME_OVER
    cycle: int                  # election cycle (1–6)
    turn: int                   # turn within cycle (1–20)
    game_length: int            # 4 / 5 / 6 cycles

    city_map: CityMap
    players: dict[str, Player]
    metrics: Metrics
    factions: list[Faction]
    railway_party: RailwayParty
    canal_party: CanalParty
    pending_reports: dict[str, list[Report]]
    pending_vote: Vote | None
    event_log: list[GameEvent]
    pending_effects: list[tuple[int, Effect]]  # (apply_at_turn, effect)
    win_state: WinState | None
    council_extensions_remaining: int = 3
    turn_time_limit: int = 40
```

---

## 4. City Map — Graph Model

### Why a graph, not a grid
What matters in Civic Engine isn't which grid squares have canals — it's which districts are connected to which. Canal network effects, Bronze/Silver/Gold win tiers, and spatial competition with the railway are all graph connectivity questions.

Grant immediately understood the percolation connection from a Java course he'd done — the Canal Mania network effect trigger is exactly a percolation phase transition.

### Map nodes (districts)
```python
class MapNode(BaseModel):
    node_id: str
    node_type: NodeType         # PORT | INDUSTRIAL | RESIDENTIAL | COMMERCIAL
    position: tuple[float, float]   # normalised 0.0–1.0 for React rendering
    has_railway_station: bool = False   # Grant's addition
    has_canal_wharf: bool = False
    construction_state: ConstructionState | None = None
```

### Canal network connectivity check
```python
import networkx as nx

def check_canal_connectivity(city_map: CityMap) -> CanalTier:
    G = nx.Graph()
    for seg in city_map.canal_segments.values():
        if seg.status == "complete":
            G.add_edge(seg.from_node, seg.to_node)

    major_nodes = city_map.get_major_nodes()
    if nx.is_connected(G.subgraph(major_nodes)):
        return CanalTier.BRONZE   # all major nodes linked
```

### Starting state at turn 1
The AI-generated city begins with 1–2 short, disconnected canal stubs from a previous failed commission. Complete but isolated — no network effect yet. Gives players something to build toward; makes the first connection feel earned.

### AI map generation
Claude generates the entire city map at startup via tool use. The Pydantic model's JSON schema is passed as the tool's input schema. Claude returns node positions, segment routes, waypoint names and types — all validated directly into the CityMap model. Positions are normalised (0.0–1.0) so React scales them to any canvas size.

This is also the candidate MCP server experiment for Grant's afternoon session — `generate_victorian_city_map` as an MCP tool.

### React Flow for rendering
React Flow (@xyflow/react) handles the node-edge graph rendering. Custom `DistrictNode` and `CanalEdge` components handle the Victorian steampunk visual styling. Game state maps directly to React Flow's node/edge format. Cuts estimated rendering work from ~3 hours to ~1.5 hours.

---

## 5. Canal Segments and Waypoints

### Option B chosen — waypoints as sub-nodes
Grant chose the richer waypoint model over simple progress percentage. Reasons:
- Multiple simultaneous blockages possible
- Named locations add historical character ("Brindley's Cutting", "Chadwick Locks")
- Railway can claim specific waypoints, forcing reroutes — spatial competition made concrete
- Aqueduct waypoints trigger the PRD's "engineering feat" milestone automatically

Extra build cost: approximately 4–5 hours over the simpler approach. Grant accepted this tradeoff explicitly.

### Waypoint types
```python
class WaypointType(str, Enum):
    CUTTING = "cutting"       # dug through earth
    EMBANKMENT = "embankment" # built up above ground
    LOCK = "lock"             # changes water level
    AQUEDUCT = "aqueduct"     # crosses road or river → engineering feat trigger
    TUNNEL = "tunnel"         # underground, high cost/risk
    JUNCTION = "junction"     # branches to another canal
    AMENITY = "amenity"       # fishing platform, mooring, towpath garden → aesthetic boost
```

### Canal segment model
```python
class CanalSegment(BaseModel):
    segment_id: str
    from_node: str
    to_node: str
    waypoints: list[Waypoint]         # ordered from→to
    railway_claimed: bool = False     # corridor contested
    construction_cost: int = 0

    @property
    def active_waypoint(self) -> Waypoint | None:
        return next(
            (w for w in self.waypoints
             if w.status not in ("complete", "blocked")),
            None
        )
    # future: waypoints: list[Waypoint] = []  ← sub-nodes upgrade path
```

### Waypoint model
```python
class Waypoint(BaseModel):
    waypoint_id: str
    name: str
    waypoint_type: WaypointType
    position: tuple[float, float]
    status: WaypointStatus          # UNSTARTED | UNDER_CONSTRUCTION | COMPLETE | BLOCKED | CONTESTED
    blocked_by: str | None = None   # "railway_claim" | "flood_event" | "strike"
    construction_turns_required: int
    turns_spent: int = 0
```

---

## 6. Report Class and Player Decisions

### What a Report is
The atomic unit of gameplay. Every player decision goes through one. Generated from three sources: scheduled (quarterly/annual), threshold-triggered (metric crosses a line), Claude-generated events.

### Report model
```python
class Report(BaseModel):
    report_id: str
    title: str
    description: str                    # Claude-generated narrative
    report_type: ReportType             # SCHEDULED | THRESHOLD | CLAUDE_EVENT | AGENT_OUTCOME
    addressed_to: str                   # player_id
    domain: CouncilRole
    options: list[ReportOption]         # 1–4 options
    status: ReportStatus                # PENDING | DECIDED | DELEGATED | DEFERRED | ESCALATED | AUTO_RESOLVED
    is_private: bool = True
    delegation_candidates: list[str] = []   # agent_ids eligible
    delegated_to: str | None = None         # set when player chooses agent
    decision: str | None = None
    conflict_with: str | None = None
    defer_count: int = 0
    deferred_until_turn: int | None = None
    deferral_consequences: list[str] = []
    escalated_to_council: bool = False
    turn_received: int
    turn_deadline: int
    urgent: bool = False                # if True, cannot be deferred
```

### Key design decisions on reports

**1 option = forced acknowledgment.** Not a real choice — communicates that something is happening to the council, not a decision point. Realistic (sometimes cities have momentum of their own).

**1–4 options range.** 1 = forced. 2–3 = standard. 4 = agent-researched or complex council matter.

**Player chooses which agent to delegate to** — not automatic. Opens the agent roster picker on the phone. Different agents have different risk profiles and specialisations; the choice is strategic.

**DEFER as explicit action.** Active choice, not passive timeout. Deferral costs a small election_polling penalty (public sees indecision). Cannot defer urgent reports. Deferring twice auto-escalates to council on the third turn.

**Research alternatives** — available when fewer than 3 options exist and an agent is available. Costs one turn; agent returns a follow-up report with up to 4 options including agent_only ones.

### Report option model
```python
class ReportOption(BaseModel):
    option_id: str
    label: str
    description: str
    effects: list[Effect]
    risk_level: RiskLevel           # LOW | MEDIUM | HIGH
    agent_only: bool = False        # only visible when delegating
    is_forced: bool = False         # single-option forced acknowledgment
    value_signals: list[str] = []   # ["workers_rights", "fiscal_prudence", "heritage"]
    min_skill_level: float = 0.0    # skill gate — higher-skilled councillors see more options
    required_skill: str | None = None
```

### Player action set per turn (40-second timer)

| Action | Available when |
|---|---|
| Choose option | Always |
| Delegate → pick agent | Agent available in domain |
| Research alternatives | Agent available + fewer than 3 options |
| Defer | Not urgent, defer_count < 2 |
| Flag for council | Any report |

---

## 7. Effects System

### The Effect model
Replaces simple `expected_effects: list[str]` strings. Structured, typed, with delay support.

```python
class Effect(BaseModel):
    effect_type: EffectType
    target_type: TargetType     # prevents cross-namespace ID collision
    target_id: str              # ID within that namespace only
    value: float | str
    delay_turns: int = 0        # 0 = immediate, N = applied N turns later
    description: str
```

### Target type disambiguation
Grant identified a real bug risk: if `target` is just a string, a faction called "C4" and a segment called "C4" could collide. Solution: `target_type` field routes the engine to the right collection before looking up `target_id`.

Option A (target_type + target_id) chosen for the hackathon. Option B (Pydantic discriminated unions) documented as the production upgrade path — same concept, stricter enforcement, mechanical upgrade.

### Effect types
```python
class EffectType(str, Enum):
    METRIC_DELTA = "metric_delta"
    BUDGET_DELTA = "budget_delta"
    CONSTRUCTION_START = "construction_start"
    CONSTRUCTION_ADVANCE = "construction_advance"
    FACTION_MOOD = "faction_mood"
    REPORT_GENERATE = "report_generate"
    RAILWAY_INFLUENCE = "railway_influence"
    CANALPARTY_INFLUENCE = "canalparty_influence"   # Grant's addition
    AESTHETIC_DELTA = "aesthetic_delta"              # Grant's addition
    ECONOMY_DELTA = "economy_delta"
    INCOME_DELTA = "income_delta"
    COUNCIL_EXTENSION = "council_extension"
```

### Target types
```python
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
```

### Pending effects queue
```python
class GameState(BaseModel):
    ...
    pending_effects: list[tuple[int, Effect]]  # (apply_at_turn, effect)
```

Each turn, the engine applies all effects whose `apply_at_turn` matches the current turn. Budget deducted immediately; canal construction starts immediately but advances one waypoint per turn.

---

## 8. Metrics and Factions

### Metrics model
```python
class Metrics(BaseModel):
    road_rage_index: float = 50.0
    canal_efficiency_index: float = 10.0
    aesthetic_index: float = 40.0       # Grant's addition — see section 10

    citizen_happiness: float = 65.0     # computed from faction happiness
    horse_pollution: float = 30.0
    accidents_this_cycle: int = 0
    projects_delayed: int = 0
    tradies_nonbilling: int = 0

    road_freight_pct: float = 100.0
    canal_freight_pct: float = 0.0
    rail_freight_pct: float = 0.0

    economy_index: float = 50.0
    cycle_income: int = 0

    budget: DepartmentBudget = DepartmentBudget()
    election_polling: float = 65.0
    cycles_survived: int = 0
```

### citizen_happiness is computed, not stored directly
```python
def recompute_citizen_happiness(factions, metrics) -> float:
    faction_component = weighted_average(factions)        # 80%
    aesthetic_component = metrics.aesthetic_index / 100   # 20%
    return (faction_component * 0.8) + (aesthetic_component * 100 * 0.2)
```

### election_polling has inertia (same pattern as economy)
```python
polling += (citizen_happiness - polling) * 0.2
```

### Faction model
```python
class Faction(BaseModel):
    faction_id: str
    name: str
    profile: str                        # plain text — Claude's system prompt
    happiness: float = 60.0
    population_weight: float = 1.0
    transport_priorities: list[str]
    political_sensitivities: list[str]
    reaction_threshold: float = 10.0
    canal_alignment: float = 0.0        # -1.0 to +1.0
    railway_alignment: float = 0.0
```

### Historical accuracy on faction names
Grant caught a major anachronism: "Car-dependent commuters" was used in an example. Cars don't exist in 1785. Period-correct replacements:

| Anachronistic | Period-correct |
|---|---|
| Car-dependent commuters | Coach-travelling gentry |
| Road freight operators | Carter's Association |
| Turnpike investors | Turnpike Trust shareholders |

Claude generates period-appropriate dialogue when the faction `profile` is historically grounded. If the profile doesn't mention cars, Claude won't.

### Faction reactions
Not every decision reaches every faction. The engine checks each faction's `political_sensitivities` against the decision's effects before calling Claude. Only affected factions get reaction calls. Keeps cost down, reactions relevant.

```python
class FactionReaction(BaseModel):
    faction_id: str
    reaction_text: str
    happiness_delta: float
    triggered_by: str
    severity: Literal["minor", "moderate", "major"]
    display_on: list[str]
```

---

## 9. Economic Model

### Grant's observation
Grant identified that the PRD implied an economic layer without spelling it out: tradies non-billing, goods-per-load advantage, Canal Mania windfall, coal and steel scarcity. These should feed back into budgets and faction happiness.

### Freight volume split — the engine
```python
class Metrics(BaseModel):
    road_freight_pct: float = 100.0
    canal_freight_pct: float = 0.0
    rail_freight_pct: float = 0.0     # must sum to 100
```

Everything economic flows from where goods are moving.

### Economy index with inertia
Grant noted that `min(100.0, computed)` was wrong — the economy can go backwards under disruption. Fixed with inertia model (same pattern as election_polling):

```python
def recompute_economy(metrics: Metrics) -> float:
    target = (
        metrics.canal_freight_pct * 1.2 +
        metrics.rail_freight_pct * 0.9 +
        metrics.road_freight_pct * 0.4
    )
    new_economy = metrics.economy_index + (target - metrics.economy_index) * 0.25
    return max(0.0, min(100.0, new_economy))
```

Canal gives higher economic return than rail; road is the least efficient. But all three can fall — catastrophic disruption reduces economy_index toward a lower target.

### Cycle-end income
```python
def apply_cycle_income(metrics: Metrics) -> DepartmentBudget:
    income = int(BASE_INCOME * (metrics.economy_index / 100))
    return DepartmentBudget(
        finance=income // 2,
        infrastructure=income // 3,
        transport=income // 6
    )
```

The flywheel: better canal → more freight on canal → higher economy → more cycle income → more budget → build more canal.

### Canal Mania economic event
```python
class CanalMania(BaseModel):
    triggered: bool = False
    windfall_received: int = 0
    bubble_risk: float = 0.0       # rises each turn after Mania fires
    bubble_burst: bool = False     # crash report fires if bubble_risk > threshold
```

Fires when canal_freight_pct crosses ~60%. Finance gets a windfall. Bubble risk rises each turn — if players don't stabilise, the crash hits economy_index hard.

---

## 10. Aesthetic Index

### Grant's design addition
Proposed to add an aesthetic metric grounded in the canal's non-transport value: fishing, living aboard, resident appeal, natural habitat for waterfowl. Explicitly described as a "folk ethic grounded in older world values" — the canal party's alternative value system to the railway's speed and capital.

### Aesthetic index
Starts at 40.0 — natural waterways pre-exist the canal. Building well enhances what's there; building carelessly destroys it.

**Raises:** Canal segments completed at standard pace (+5), amenity waypoints (+8), pleasure boat licences (+4), engineering feats (+6), construction paced for habitat (+3), waterfowl nesting protected (+5).

**Lowers:** Rushed construction (-6), horse pollution spills into canal (-4), Canal Mania overbuilding (-5), railway segments built adjacent (-3), industrial effluent ignored (-8), agent cutting corners (-4).

### New factions the aesthetic unlocks
- Angling Society (very high sensitivity)
- Canal Boat Families (very high — they live on the water)
- Natural Historians (Victorian naturalists — high)
- Waterside Tavern Keepers (moderate — foot traffic is their trade)

### Heritage Commendation win state
Awarded if `aesthetic_index >= 70` at game end, regardless of canal completion tier:
*"The people's canal — a working waterway and a living landscape, remembered for generations."*

Stacks with canal completion tiers. Gold + Heritage = highest possible achievement.

### Railway aesthetic contrast
Each railway segment built near a canal applies a small `AESTHETIC_DELTA` to nearby districts. Steam, coal dust, industrial noise. Railway doesn't just race canal on efficiency — it erodes the world the canal party is trying to preserve.

### AMENITY waypoint type
Deliberate council decision, not required for connectivity. Extra 1–2 construction turns. Returns: AESTHETIC_DELTA +8, faction happiness boost to residential and fishing factions, small CYCLE_INCOME from leisure tolls.

**The competing goods dilemma this creates:** Build efficiently (skip amenities, finish faster) or build beautifully (slower, stronger community support, better election polling). Exactly the design principle from the scope session.

---

## 11. Voice Commands and Claude Integration

### Web Speech API
Browser built-in. No library, no API key, no cost. Works reliably in Chrome and Edge — demo players should use Chrome on their phones.

```typescript
const recognition = new webkitSpeechRecognition();
recognition.lang = 'en-NZ';
recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    socket.emit('voice_command', { player_id, text: transcript });
};
```

React sends the raw text to the server. Claude interprets it — never React.

### Voice command scoping
Claude is told the player's domain and shown only that domain's available actions. A Transport councillor cannot accidentally voice-command a Finance decision. Domain scoping is in the prompt, not a post-processing filter.

### ParsedCommand model
```python
class ParsedCommand(BaseModel):
    action_type: str
    target_type: TargetType | None = None   # same disambiguation as Effect
    target_id: str | None = None
    parameters: dict = {}
    confidence: float
    clarification_needed: bool = False
    clarification_prompt: str | None = None
```

Grant identified the same target_id disambiguation issue here as in the Effect model — same fix applied.

### Three Claude integration points

**Voice parsing** — `claude/voice.py`: transcript → ParsedCommand via tool use. Scoped to player domain.

**Faction reactions** — `claude/citizens.py`: faction.profile IS the system prompt. Claude speaks as that faction. Called concurrently with asyncio.gather for all affected factions.

**Report generation** — `claude/events.py`: game master generates domain reports. Called once per domain per turn.

**Map generation** — `claude/map_gen.py`: city map, factions, councillors generated at startup. MCP server candidate for afternoon experiment.

### Prompt caching
Static content (faction profiles, game rules, domain descriptions) marked with `cache_control: {"type": "ephemeral"}`. Saves ~80% of those tokens on calls after the first. Cache TTL is 5 minutes — exactly right for a fast game session.

### Concurrent Claude calls
`asyncio.gather()` runs all faction reactions and report generations in parallel. Total latency = slowest single call, not sum. Target: under 5 seconds for full turn-end processing.

### Max tokens handling
```python
async def safe_claude_call(kwargs: dict, fallback_tokens: int) -> Message:
    response = await client.messages.create(**kwargs)
    if response.stop_reason == "max_tokens":
        kwargs['max_tokens'] = fallback_tokens
        response = await client.messages.create(**kwargs)
    return response
```

Pydantic ValidationError on tool use truncation = retry signal.

Token limits per call type:

| Call type | Safe limit | Fallback |
|---|---|---|
| Voice command | 300 | 500 |
| Faction reaction | 350 | 600 |
| Report generation | 700 | 1200 |
| Map generation | 3000 | 5000 |

### Admin cost monitoring
```python
@dataclass
class UsageRecord:
    call_type: str
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    turn: int
    cycle: int

    @property
    def cost_usd(self) -> float:
        return (
            self.input_tokens       * 0.000003   +
            self.output_tokens      * 0.000015   +
            self.cache_write_tokens * 0.00000375 +
            self.cache_read_tokens  * 0.0000003
        )
```

Admin endpoint: `GET /admin/usage?token=ADMIN_TOKEN`
Returns: total cost, cost by call type, cache hit rate, estimated full-game cost.
Target cache hit rate: >60%. Below 40% = prompt structure needs fixing.
Estimated cost per full game session: $1.50–$3.00 with good caching.

---

## 12. AI Players

### The constraint
Grant is the sole developer and tester. He needs AI players to fill Finance and Infrastructure roles while he plays Transport. Also needed for any solo demo.

### Architecture
AI players are players whose decisions are made server-side by Claude instead of arriving over WebSocket from a human. The game engine checks `player_type` to know whether to wait for WebSocket input or call Claude directly.

```python
class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"

class AIDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
```

### AI decision making
```python
# claude/ai_player.py
async def make_ai_decision(player, report, game_state) -> PlayerAction:
    # system prompt: councillor profile + cooperative goal
    # AI players are on the same team — their goal is canal completion
    # Difficulty shapes what effects information is visible in the prompt
```

2-second delay before applying AI decisions — feels like genuine simultaneous deliberation, not instant snapping.

AI players also vote in council votes. Same Claude call, vote context instead of report context.

### Visibility on central screen
AI decisions show in the event feed with an AI badge:
```
🤖 Alderman Blackwood (Finance) [AI]
   Approved canal survey budget — £320
```

Grant needs to see AI decisions to test and understand game flow.

---

## 13. Railway Party Phase Transition

### Grant's design decision
The railway party evolves from a passive lobby group to an active rival organization that mirrors the canal party's structure. Same architecture, opposing goal, AI-controlled throughout.

**Phase 1 — LOBBY:** Influence grows, lobbying events appear on councillor phones, no physical map presence. Constrained by coal and steel scarcity.

**Phase 2 — ACTIVE:** AI councillors operational, railway segments appearing on map, influence racing canal party influence directly.

```python
class RailwayPhase(str, Enum):
    LOBBY = "lobby"
    ACTIVE = "active"

class RailwayParty(BaseModel):
    influence: float = 20.0
    phase: RailwayPhase = RailwayPhase.LOBBY
    activation_threshold: float = 40.0    # tunable per difficulty
    councillors: list[RailwayCouncillor] = []
    railway_segments: list[RailwaySegment] = []
    budget: int = 0
```

### Activation event
When influence crosses threshold: dramatic event card on central screen, railway councillors introduced in a dossier reveal, railway budget initialised, phase → ACTIVE. From next turn: railway AI councillors make decisions, segments appear on map.

Activation timing by difficulty:
- 4 cycles (beginner): Cycle 3, turn 1
- 5 cycles (standard): Cycle 2, turn 10
- 6 cycles (experienced): Cycle 2, turn 1

### Railway AI uses same mechanism
`claude/ai_player.py` with an inverted goal:
```
system: "Your goal is to complete the railway network before the canal party finishes theirs.
         Claim the most strategically valuable corridors. Contest canal waypoints."
```

Canal AI: cooperative, same team as Grant. Railway AI: adversarial, opposing goal. Same code, opposite system prompt.

### Railway segments reuse waypoints
`RailwaySegment` uses the same `Waypoint` model as `CanalSegment`. Spatial competition: when a railway segment claims a waypoint that overlaps a canal corridor, it sets `blocked_by: "railway_claim"` on the canal waypoint. No new blocking logic — it already exists.

### Map rendering
Second React Flow edge type: `RailwayEdge`. Dark iron-red lines vs canal's blue. Contested waypoint: amber warning marker. `InfluenceMeter` component shows the two influence bars racing each other.

### New file: game/railway.py
Railway corridor selection strategy — which corridors does the railway AI target?

Priority: (1) corridors where canal has active construction, (2) corridors connecting major industrial nodes, (3) corridors that would split canal network connectivity if claimed.

---

## 14. File Structure

```
civic-engine/
├── backend/
│   ├── main.py                   # FastAPI app, socket.io, WebSocket event handlers
│   ├── config.py                 # env vars, game constants
│   ├── game/
│   │   ├── state.py              # ALL Pydantic models
│   │   ├── engine.py             # turn resolution, effect application, win checks
│   │   ├── map.py                # networkx connectivity, freight split
│   │   ├── factions.py           # faction filtering, happiness weighting
│   │   ├── reports.py            # report scheduling, threshold checks
│   │   ├── agents.py             # hire/retire, delegation outcome
│   │   ├── elections.py          # cycle-end, polling, win/lose
│   │   ├── railway.py            # railway AI corridor strategy
│   │   └── scenarios.py          # named dev/test seed states
│   ├── claude/
│   │   ├── client.py             # shared AsyncAnthropic, UsageTracker
│   │   ├── voice.py              # transcript → ParsedCommand
│   │   ├── citizens.py           # faction reactions (concurrent)
│   │   ├── events.py             # report generation
│   │   ├── ai_player.py          # canal and railway AI decisions
│   │   └── map_gen.py            # city/faction/councillor generation ← MCP candidate
│   ├── api/
│   │   ├── admin.py              # /admin/usage, /admin/seed, /admin/set,
│   │   │                         # /admin/advance-turn, /admin/save, /admin/load
│   │   └── health.py             # /health
│   ├── saves/                    # JSON save slots (gitignored)
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx               # routing: /central, /phone
│   │   ├── socket.ts             # socket.io-client, single connection
│   │   ├── store.ts              # React Context: game state + player identity
│   │   ├── types.ts              # auto-generated TypeScript types (see below)
│   │   ├── views/
│   │   │   ├── CentralScreen/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── CityMap.tsx           # React Flow map
│   │   │   │   ├── MetricsDash.tsx
│   │   │   │   ├── InfluenceMeter.tsx    # canal vs railway race bar
│   │   │   │   ├── EventFeed.tsx
│   │   │   │   └── VotePanel.tsx
│   │   │   └── PlayerPhone/
│   │   │       ├── index.tsx
│   │   │       ├── ReportQueue.tsx
│   │   │       ├── ReportCard.tsx
│   │   │       ├── AgentRoster.tsx
│   │   │       ├── VoiceButton.tsx
│   │   │       ├── TurnTimer.tsx
│   │   │       └── ExtensionButton.tsx
│   │   ├── components/
│   │   │   ├── DistrictNode.tsx      # React Flow custom node
│   │   │   ├── CanalEdge.tsx         # React Flow custom canal edge
│   │   │   ├── RailwayEdge.tsx       # React Flow custom railway edge
│   │   │   ├── WaypointMarker.tsx
│   │   │   ├── FactionCard.tsx
│   │   │   └── DevPanel.tsx          # hidden dev overlay (Ctrl+Shift+D)
│   │   └── hooks/
│   │       ├── useVoiceInput.ts
│   │       ├── useSocket.ts
│   │       └── useGameState.ts
│   ├── package.json              # includes "generate-types" script
│   └── vite.config.ts
│
├── docs/
├── saves/
├── process-notes.md
└── README.md
```

---

## 15. TypeScript Type Generation

### Decision
Option C — FastAPI OpenAPI + openapi-typescript.

FastAPI automatically generates an OpenAPI schema from routes and models. `openapi-typescript` reads it and generates TypeScript.

### Workflow
```python
# backend/api/admin.py — dummy routes to pull key models into schema
@app.get("/schema/game-state", response_model=GameState, include_in_schema=True)
async def _game_state_schema(): pass
```

```json
// frontend/package.json
"scripts": {
    "generate-types": "openapi-typescript http://localhost:8000/openapi.json -o src/types.ts",
    "dev": "npm run generate-types && vite"
}
```

Types regenerate every time the frontend dev server starts. Type drift becomes impossible during active development.

### Backup option
Option B — `datamodel-code-generator`. If openapi-typescript causes unexpected issues:
```bash
pip install datamodel-code-generator
python -c "from backend.game.state import GameState; import json; \
           print(json.dumps(GameState.model_json_schema()))" > schema.json
datamodel-codegen --input schema.json --input-file-type jsonschema \
                  --output-model-type typescript --output frontend/src/types.ts
```

---

## 16. Council Extensions

### Grant's design addition
A limited-use action that extends the 40-second turn timer. Creates genuine strategic tension: when do you spend your extensions?

```python
class GameState(BaseModel):
    ...
    council_extensions_remaining: int = 3
    turn_time_limit: int = 40
    current_turn_extended: bool = False
```

Rules:
- One extension per turn maximum (no stacking)
- Cannot extend during a council vote
- Adds 30 seconds to active server-side timer
- Costs election_polling -2 (public sees indecision)
- All 3 spent → button greyed out on all phones
- Logged to event_log → shows in end-of-game scorecard

---

## 17. Dev Mode and Game State Seeding

### Motivation
Grant is the sole developer and tester. Fresh game turn 1 won't show interesting mechanics — Canal Mania, railway activation, election pressure, aesthetic events all come later. Needed: ability to drop into specific game states.

### Three-layer dev mode

**Layer 1 — Named scenarios (backend/game/scenarios.py):**
```python
SCENARIOS = {
    "fresh": scenario_fresh_game,
    "canal_progress": ...,        # turn 15, cycle 1, half-built
    "railway_activation": ...,    # influence at 38, about to cross threshold
    "canal_mania": ...,           # network near critical mass
    "election_pressure": ...,     # turn 18, low polling
    "heritage": ...,              # high aesthetic, strong community
    "crisis": ...,                # everything going wrong
}
```

**Layer 2 — Admin endpoints (api/admin.py):**
```
POST /admin/seed/{scenario_name}  → load named scenario
POST /admin/set                   → set individual values by path
POST /admin/advance-turn?turns=N  → skip N turns (AI decides everything)
POST /admin/save?slot=quicksave   → save state to saves/quicksave.json
POST /admin/load?slot=quicksave   → restore from save file
```

All protected by ADMIN_TOKEN. Save/load also serves as crash recovery during demo.

**Layer 3 — Dev panel (frontend/src/components/DevPanel.tsx):**
- Hidden overlay, activated by Ctrl+Shift+D
- Only rendered when `import.meta.env.DEV` is true — invisible in production
- Buttons for each named scenario
- Fast-forward: +1 turn, +5 turns, +1 cycle
- Sliders for key metrics (railway influence, aesthetic index, election polling)
- Save/restore buttons

---

## 18. Error Resilience

### The design principle
The game must never freeze waiting for a human or a service. Every failure path has a default action that keeps the turn moving, and every default action is logged.

### Case 1 — Claude timeout (8-second limit)

| Call type | Fallback |
|---|---|
| Faction reactions | Generic template: "[faction] watches developments cautiously." Delta: 0 |
| Report generation | Draw from pre-written pool in game/scenarios.py |
| Voice command | Return clarification_needed: True — phone shows "Tap your choice" |
| AI player decision | First available option selected, logged |

Admin report logs all timeouts with timestamp, call type, and turn number.

### Case 2 — Web Speech API failure

Three sub-cases in useVoiceInput hook:
- **Low confidence (< 0.6):** Show transcript, ask confirmation "Did you mean: X?"
- **Complete failure:** Auto-switch to text input field (same WebSocket event, same server parsing)
- **Empty transcript:** "Voice unavailable — type your command"

Text fallback is automatic and seamless. In a noisy demo room, judges won't notice it happened.

### Case 3 — WebSocket disconnection

Priority cascade:
```
Disconnect detected (socket.io event)
    ↓
Free deferral on all pending reports
30-second reconnection window
    ↓
Reconnects? → session restored, reports still pending
Doesn't reconnect? ↓
Agent available? → default agent resolves all reports
No agent? → first available option selected
    ↓
GameEvent: CONNECTION_LOST logged
Central screen: "[Player] acting on first available option"
election_polling: -1
Personal scorecard: connection event noted
```

"Route to another councillor" kept as a manual option (button on phone) — not automatic, to avoid cross-domain conflicts.

### New GameEvent types for error logging
```python
CONNECTION_LOST = "connection_lost"
CLAUDE_TIMEOUT = "claude_timeout"
VOICE_FALLBACK = "voice_fallback"
AUTO_RESOLVED = "auto_resolved"
```

---

## 19. Councillor Model

### Grant's design decisions
- Skill growth mirrors agents: milestones and actions increase experience
- Acting consistently with values gives a growth bonus
- Initial profile (political alignment, core values, background) generated semi-randomly by Claude at startup
- Skills generated same way as faction personalities — Claude-generated from profile, not hardcoded
- Each game: different councillors (replayability layer)

### Councillor model
```python
class CouncillorSkill(BaseModel):
    skill_name: str
    description: str            # Claude-generated
    level: float = 1.0
    experience_points: int = 0

class Councillor(BaseModel):
    councillor_id: str
    name: str
    role: CouncilRole

    political_alignment: str    # "Progressive reformer with conservative fiscal instincts"
    core_values: list[str]      # ["workers' rights", "civic duty", "fiscal prudence"]
    professional_background: str
    value_tension: str          # the "competing goods" tension within the character

    skills: list[CouncillorSkill]
    decisions_made: int = 0
    value_aligned_decisions: int = 0
    milestones_achieved: list[str] = []

    profile: str                # full text — Claude system prompt for AI players
```

### Value alignment — no extra Claude call
Report options tagged with `value_signals: list[str]`. Engine matches against `councillor.core_values`. Simple string matching, instant, no latency cost.

### Skill growth
```python
def award_councillor_experience(councillor, action_type, was_value_aligned, milestone_achieved=False):
    xp = 10
    if was_value_aligned: xp += 5
    if milestone_achieved: xp += 25
    relevant_skill = find_relevant_skill(councillor, action_type)
    if relevant_skill:
        relevant_skill.experience_points += xp
        relevant_skill.level = 1.0 + (relevant_skill.experience_points / 100)
```

### Mechanical effect of skill
Higher skill unlocks additional report options via `min_skill_level` gate on `ReportOption`. A novice Infrastructure councillor sees 2 options; a skilled one sees a third creative engineering solution. Skill growth feels meaningful because it literally opens new decisions.

### Generation at startup (12 councillors, 4 per role)
Same pipeline as map and factions. Claude generates names, backgrounds, value tensions, initial skills. Semi-random — different every game. Profiles become Claude system prompts for AI players.

---

## 20. WebSocket Event Dictionary

| Direction | Event | Payload | Triggers |
|---|---|---|---|
| Client → Server | `register` | `{client_type, player_id, role, session_id}` | On connect |
| Client → Server | `player_action` | `{player_id, action_type, target_type, target_id, option_id}` | Report decision |
| Client → Server | `voice_command` | `{player_id, text}` | Voice transcript |
| Client → Server | `council_extension` | `{player_id}` | Extension button |
| Client → Server | `new_game` | `{game_length}` | Host on central screen |
| Server → Client | `game_state_update` | Full `GameState` JSON | After any change |
| Server → Client | `council_processing` | `{turn, cycle}` | Turn-end started |
| Server → Client | `vote_called` | `Vote` object | Conflict detected |
| Server → Client | `milestone` | `{type, description}` | Canal milestone |
| Server → Client | `game_over` | `{reason, win_state}` | Election lost or canal complete |

---

## 21. Key Design Contributions by Grant

These are the moments where Grant shaped the architecture, not just followed it:

- **Waypoints over progress percentage** — chose the richer Option B knowing it cost 4–5 extra hours. Added character and made spatial competition concrete.
- **CANALPARTY_INFLUENCE as an effect type** — identified that tracking only railway influence was incomplete; the race needs both sides measured.
- **Target type disambiguation** — independently identified that plain string `target_id` was a bug risk without knowing the pattern name. Same fix applied to both Effect and ParsedCommand.
- **Economy going backwards** — caught the `min(100.0)` ceiling as wrong; economy should be able to decline under disruption.
- **Period-correct faction names** — caught "car-dependent commuters" as anachronistic for 1785.
- **Player choosing which agent to delegate to** — proposed active agent selection rather than automatic assignment.
- **DEFER as explicit action** — distinguished between passive timeout and active political choice.
- **Session identity in localStorage** — independently identified the need for player identity before it was proposed.
- **has_railway: bool on MapNode** — identified the need to track railway presence on the map graph.
- **Railway party phase transition** — proposed the lobby-to-active evolution as a parallel organization mirroring the canal party.
- **Aesthetic Index** — proposed the entire folk-ethic value system as a metric; connected it to the canal party's philosophical identity.
- **Council extensions** — proposed as a limited strategic resource with game dynamic implications.
- **AI players for solo testing** — practical constraint that produced an elegant architectural solution.
- **Councillor skill growth mirroring agents** — identified the parallel structure and proposed reusing it.
