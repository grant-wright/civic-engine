# Process Notes

## /onboard

**Technical experience:** Intermediate-to-experienced developer (Delphi, C#, Oracle/MySQL, Unity). Zero prior AI coding agent experience — Claude Code is his first. Just installed Cursor.

**Learning goals:** (1) Learn Claude Code as a coding agent, (2) understand formal planning artifacts (scope, PRD, spec), (3) complete first hackathon. Longer-term interest in PM roles on IT projects.

**Creative sensibility:** Strong puzzle/logic affinity. Zydeco/accordion music, Modern Jive dancing, historical novels. Caught by MiroClaw (AI agent personality graph networks) — wants something like it but as game elements. Systemic thinker with playful depth.

**Prior SDD experience:** Wrote basic system diagrams, UI flows, data entity models for client projects. Informal but relevant. Not starting from zero — just learning the structured, AI-collaborative form.

**Energy and engagement:** Thoughtful and open. Here to learn the process, not just ship. Potential PM trajectory makes the planning-first approach genuinely motivating for him. Strong candidate for deepening rounds in /scope — he'll appreciate the rigour.

## /scope

**How the idea evolved:** Started as a sweeping Monopoly/Civilization/SimCity/Pandemic hybrid with full economic simulation, Dunbar-scale agent networks, and forking timelines. Through structured scoping, landed on a focused cooperative steampunk city transport sim — Victorian city guided through technological eras by councillors chasing a prestige hosting bid. The core values (interdependence, non-zero-sum, civic education) stayed constant; scope contracted sharply around transport as the single domain.

**Key pushback received:** Challenge to cut "too complicated" instincts early. Grant responded well — he self-edited the forking timeline, physical board, and multi-domain simulation without much resistance once framing shifted to "what can you demo in 2 minutes?"

**What resonated:**
- World of Communities — immediate affinity ("I would love to play it")
- Frostpunk — strong resonance; prompted a separate future game idea (civilization reboot scenarios)
- AI Town — understood conceptually; confirmed emergent agent behavior as north star
- "Dilemmas between competing goods, not two evils" — named explicitly as a design principle
- Steampunk aesthetic — lit up strongly; Victorian + smart city data dashboard
- Dramatic faction reveal at setup (card flip) — enthusiastic "wow yes, I love that!!"
- Era transitions as the game's tension peaks — canals/railways/electric, labor displacement, Irish navvies

**Emotional undercurrent:** Post-earthquake Christchurch surfaced when asked about the city's visual feel. Grant pivoted away from it toward steampunk/Victorian but it explains why civic decision-making and heritage dilemmas resonate so personally. Named a future project: Christchurch 2074 Commonwealth Games sim.

**Deepening rounds:** One substantive round covering factions, councillor archetypes, value tension dilemmas, visual aesthetic, and era transitions. Scope doc v1 written mid-conversation; v2 updated after deepening. The contrast was significant — v2 gained the steampunk evolution mechanic, the three-axis councillor system, the era transition tension peaks, and the "competing goods" dilemma design principle. All materially improved the document.

**Active shaping:** Grant drove the direction strongly throughout. Key steering moments: insisting on cooperative non-zero-sum over competitive; introducing Dunbar's number unprompted; pivoting from physical board to screen himself; cutting to transport domain on his own initiative; naming the Christchurch connection and then consciously choosing steampunk as an alternative; explicitly cutting the spy/porn-empire councillor archetypes himself ("no, not for this hackathon"). He accepted suggestions on framing (steampunk label, "competing goods" dilemma principle) but the core design decisions were his.

## /prd

**Key pivot from scope:** The era transition mechanic was replaced entirely. Grant researched real canal-to-railway timescales (60+ years) and found historically-based transitions implausible. Proposed instead: players run a party with a purpose — complete the canal system before the railway party rises to dominance. This fundamentally reframed the game from "manage transitions that happen to you" to "build something before it's too late." Stronger design, cleaner arc.

**What changed vs scope doc:**
- Era transitions → removed for demo; may return in full game
- Prestige bid → replaced by canal completion milestones (first connection, engineering feat, Canal Mania, full coverage)
- Road Rage Index → joined by Canal Efficiency Index as dual headline metrics
- Railway party → elevated from background faction to rival political party with a growing influence meter
- Horse pollution → named as both Road Rage driver and public health pressure (historically accurate: the Great Manure Crisis)
- Network effects → canal value jumps when connected; half-built canal is strategically weak
- Canal Mania → historical speculative bubble as triggerable game event
- Agent hiring → elaborated as genuine risk/reward delegation; agents can find better solutions OR cut corners

**Surprising "what if" moments:**
- Grant raised historical accuracy himself and used it to improve the design — self-initiated pivot
- The railway party as rival (not just faction) reframed the tension completely
- Canal network effect as a strategic mechanic (don't build disconnected segments) surfaced naturally
- Horse pollution as a Road Rage driver emerged from historical context ("a mountain of poo")

**Scope guard conversations:**
- Dilemma system: cut for demo ("we don't need era thresholds or a dilemma system")
- Era transitions: removed for demo, preserved as future feature
- Agent hiring retained and expanded — Grant felt it was important enough to elaborate

**Deepening rounds:** One structured deepening round (draft PRD written mid-conversation, then revised). Grant requested to see the draft first and compare — strong planning instinct. The pivot to canal completion arc happened after the draft, substantially reshaping the document.

**Active shaping:** Grant drove every major decision. Key moments: raising historical accuracy concern and proposing the canal completion arc himself; identifying three core council roles (Finance, Infrastructure, Transport) for the demo; proposing hard game over as simpler than partial loss; insisting on per-player voice commands after weighing the chaos of shared mic. The railway rival as a growing threat was a collaborative build — Grant confirmed and extended it with the coal/steel constraint and network effects.

---

## /spec

**Stack decisions:** FastAPI (Python) backend + React/Vite/TypeScript frontend + python-socketio for real-time + Anthropic Python SDK. Grant chose Python for AI/data ecosystem exposure and TypeScript over JavaScript for its closeness to C#. Deployment: local for the hackathon, architecture designed to be cloud-ready without rewrite. Railway.app identified for future deployment.

**TypeScript type generation:** Option C chosen — FastAPI OpenAPI + openapi-typescript. Types auto-generated from live backend schema each dev startup. Option B (datamodel-code-generator) documented as backup. Grant's reasoning: one source of truth, everything flows from the game engine.

**What Grant was confident about:** Client/server boundary (independently identified React as "dumb display" before it was proposed). Session identity in localStorage (independently identified need for player_id before it was proposed). Target ID disambiguation as a bug risk (caught independently in both Effect and ParsedCommand). Economy declining under disruption (caught `min(100)` ceiling as wrong). Period accuracy (caught "car-dependent commuters" as anachronistic for 1785).

**What Grant was uncertain about:** Arrow function syntax in TypeScript (flagged for /build walkthrough). Full discriminated union Pydantic pattern (learned it from the conversation, understood the concept). Full detail of openapi-typescript toolchain (trusted the recommendation without full understanding — appropriate for his level).

**Key design decisions and rationale:**
- City map as graph (nodes + edges) over grid — canal connectivity is a graph problem; networkx handles it in two lines
- Waypoints as sub-nodes (Option B) over progress percentage — Grant chose richer model knowing it cost 4–5 extra hours; adds character, makes spatial competition concrete
- Effects system with target_type disambiguation — prevents cross-namespace ID collisions
- Economy with inertia model — can rise AND fall, not capped artificially
- Railway party phase transition (LOBBY → ACTIVE) — Grant's design; passive pressure becoming active rival organisation mirroring canal party structure
- Aesthetic Index as folk-ethic metric — Grant's design; canal party's value system vs railway's speed/capital; unlocks amenity waypoints, Heritage Commendation win tier
- AI players for Finance and Infrastructure — practical solo testing constraint producing elegant architectural solution; same make_ai_decision() mechanism, cooperative goal
- Council extensions as limited strategic resource — Grant's design; adds when-to-spend tension, political cost for indecision
- Dev mode with named seed scenarios — essential for solo testing; three-layer (scenarios.py + admin endpoints + DevPanel overlay)
- Councillor model mirrors agent skill growth — Grant identified the parallel and proposed reusing it

**Deepening rounds:** One round of five questions. All five surfaced real architectural gaps:
1. Railway party active behavior → phase transition design (major architectural addition)
2. Aesthetic Index → entire new metric, value system, faction set, win tier (Grant's pivot from starting-state question)
3. Dev mode seeding → three-layer testing infrastructure + answered starting state question
4. TypeScript type sync → tool comparison, Option C decision
5. Error resilience → concrete fallback cascade for all three failure modes

Deeper specification caught: railway party had no defined behavior on the map (major gap); economic model was incomplete (gap identified by Grant); aesthetic dimension of the canal party was missing (Grant's addition); starting state undefined (resolved with AI-generated stubs + dev seeding).

**Active shaping:** Grant drove architecture more actively than in any previous session. This reflects both his technical experience and the nature of spec work — he was making real engineering decisions, not just expressing preferences. He pushed back on or improved 12 distinct design proposals. The aesthetic metric, railway phase transition, and council extensions were entirely his ideas. He accepted tool recommendations (FastAPI, React Flow, openapi-typescript) but drove every game design and data model decision himself.

---

## /build

### Step 1: Project scaffold + Git init

**What was built:** Python venv created in `backend/`; all six packages installed (fastapi[standard], python-socketio, anthropic, networkx, pydantic, python-dotenv). Frontend scaffolded with Vite 7 + React-TS template; @xyflow/react, socket.io-client, and openapi-typescript installed (the last required `--legacy-peer-deps` due to Vite 7 shipping TypeScript 6, while openapi-typescript's peer dep declaration still targets ^5). Git initialised at project root; .gitignore excludes `.env`, `venv/`, `node_modules/`, `saves/`, `dist/`, `.claude/`. First commit made.

**Verification:** FastAPI docs page confirmed loading at localhost:8000/docs (title "Civic Engine", version "0.1.0", default tag, GET / endpoint visible). Vite default page confirmed loading at localhost:5173 (HMR demo, counter, Vite + React logos).

**Comprehension check:** Asked why `.env` is gitignored but `.env.example` is committed. Answer: ".env.example is safe to share" — correct. No follow-up needed.

---

### Step 2: Data models + dev seeding

**What was built:** All Pydantic models written in `game/state.py` — 25+ models and enums covering the full game data model (GameState, Player, CityMap, CanalSegment with `@computed_field` status, Councillor, Faction, Effect, Report, Vote, WinState, GameEvent, ParsedCommand, and all supporting enums). `game/store.py` created as shared mutable game state reference to avoid circular imports. `game/scenarios.py` created with `scenario_fresh_game()` seeding: 6 Victorian district nodes, 2 canal segments (seg_01 complete stub Ironbridge Wharf → Millbrook Basin, seg_02 proposed Millbrook Basin → Coppergate Market), 12 councillors (4 per role, with full profiles for Claude system prompts), 4 factions with personality profiles, 3 players (human Transport, AI Finance, AI Infrastructure). `api/admin.py` created with `GET /admin/state` behind ADMIN_TOKEN. `main.py` updated to initialize game state and include admin router.

**Issues encountered:** (1) CityMap referenced Faction before it was defined — resolved by adding `from __future__ import annotations` to allow lazy annotation evaluation. (2) `/admin/state` endpoint initially missing `response_model=GameState` — FastAPI omitted all sub-model schemas from /docs until this was added. Fixed and re-verified.

**Verification:** GET /admin/state returned full GameState JSON with players dict, city_map with nodes and canal_segments (seg_01 status: "complete", seg_02 status: "proposed"), metrics with all headline fields, factions list. Schemas section in /docs showed GameState and all sub-models after adding response_model annotation.

**Comprehension check:** Asked why seg_01's computed `status` appears in the JSON response despite being a `@property` not a field. Answer: "computed_field decorator" — correct. Understood that `@computed_field` promotes a property into the Pydantic schema and JSON output; plain `@property` is invisible to Pydantic.

**Issues encountered:** (1) Backend directory and files were already partially scaffolded from a prior session — no conflict, just picked up where it left off. (2) `openapi-typescript` install failed with ERESOLVE due to TS 6 / peer dep ^5 mismatch — resolved with `--legacy-peer-deps`. (3) Git identity not configured — set globally with Grant's name and email before first commit.

---

### Step 3: AI map generation

**What was built:** `backend/claude/__init__.py`, `backend/claude/client.py` (shared `AsyncAnthropic` client, `UsageRecord` dataclass, `usage_log`, `record_usage()`, `safe_claude_call()` with truncation retry), `backend/claude/map_gen.py` (two-phase generation: phase 1 generates nodes + canal_segments + factions; phase 2 generates 12 councillors in a separate focused call). `POST /admin/generate-map`, `GET /admin/usage`, `POST /admin/save-map`, `POST /admin/load-map` endpoints added to `api/admin.py`. `main.py` updated to auto-load `saves/map_default.json` on startup if it exists.

**Issues encountered:**
1. Original single-call approach: `CityMap` schema marks `councillors` as optional (has a default `[]`), so Claude skipped it entirely and generated factions but not councillors.
2. Split into two calls: councillor call used `_CouncillorBatch.model_json_schema()` as the tool schema. Claude returned `{}` (empty tool input). Initially suspected schema complexity (`$defs`/`$ref` references), so replaced with a flat inline schema — but the error persisted. Diagnosed via `GET /admin/usage`: `output_tokens` was exactly equal to `max_tokens` on both the primary (4000) and fallback (6000) calls, proving truncation not schema refusal. Fixed by raising to `max_tokens=8000` / `fallback_tokens=12000`.
3. Map phase was also truncating (3000 limit, needed 4641 tokens). Bumped map phase to `max_tokens=5000` / `fallback_tokens=8000`.
4. Total generation time: ~4–5 minutes across 4 API calls (two truncated retries). Save/load system added specifically to avoid regeneration during testing and gameplay.

**Verification:** `POST /admin/generate-map` returned 10 nodes (2 PORT, 3 INDUSTRIAL, 3 RESIDENTIAL, 1 COMMERCIAL, 1 MARKET), 6 canal segments, 6 factions with multi-sentence profiles, 12 councillors (4 per role). `POST /admin/save-map?slot=default` confirmed save with all counts. `GET /admin/usage` showed 4 records (2 map_gen, 2 councillor_gen) with correct token counts and cost_usd values.

**Comprehension check:** Asked how we confirmed truncation vs Claude skipping councillors. Answer: "Checked GET /admin/usage" — correct. `output_tokens` exactly matching `max_tokens` is the truncation signature; a natural completion leaves headroom.

**Follow-up items for /iterate:**
1. **Parallel councillor generation** — split the single 12-councillor call into 3 concurrent calls via `asyncio.gather()` (one per role: finance/infrastructure/transport, 4 councillors each). Would cut councillor generation time by ~3× and reduce max_tokens needed per call to ~3000. Token budget per call: 3000/5000. **Quality caveat:** parallel calls don't see each other — risk of personality homogeneity across roles (e.g. all three roles independently generating a "cautious Whig" archetype). Before shipping this change, run a quality comparison: generate a full set under both approaches and compare name variety, political_alignment diversity, value_tension uniqueness, and core_values spread across all 12. The single-call approach has an inherent advantage here; only switch if quality holds up.
2. **Test save/load fully** — verify `POST /admin/load-map?slot=default` correctly restores all game state (city_map, factions, player councillors) after a server restart. Also test saving to a named slot (e.g. `slot=backup`) and loading it back.
3. **Toggle generation steps** — add query params to `POST /admin/generate-map` to skip steps: `?include_councillors=false` skips phase 2 (useful for fast map geometry testing), `?include_factions=false` skips faction generation. Lets developers iterate on map layout without waiting for the full 5-minute run.
4. **Schema drift test** — add a test or startup assertion that the hardcoded `_COUNCILLOR_TOOL_SCHEMA` in `claude/map_gen.py` stays in sync with the Pydantic `Councillor` model. If a field is added to `Councillor`, the flat schema won't update automatically — silent mismatch risk. Could compare field names at import time: `assert set(_COUNCILLOR_TOOL_SCHEMA["properties"]["councillors"]["items"]["required"]) == set(Councillor.model_fields.keys()) - {"decisions_made", "value_aligned_decisions", "milestones_achieved"}`.

---

### Step 4: WebSocket server + game state broadcast

**What was built:** `socketio.AsyncServer` integrated with FastAPI via `socketio.ASGIApp` — both share port 8000. `game/store.py` extended with `connected_clients` dict and `broadcast_game_state()` helper (uses a `_sio` reference assigned by main.py at startup to avoid circular imports). `api/health.py` added with `GET /health`. Socket event handlers implemented: `connect` (no-op), `register` (stores client identity, emits full state targeted to the new sid only), `player_action` (logs MAJOR_DECISION event, broadcasts), `voice_command` (stub), `council_extension` (decrements remaining, adds 30s, nudges polling -2, logs event, broadcasts), `new_game` (resets state preserving generated city map, broadcasts), `disconnect` (logs CONNECTION_LOST, removes from registry). `backend/scripts/test_socket.py` written using stdlib `urllib.request` and `python-socketio` AsyncClient (requires `aiohttp` installed in venv).

**Issues encountered:** (1) Unicode box-drawing characters in test script caused cp1252 encoding error on Windows — replaced with plain ASCII. (2) Test script initially imported `httpx` (not a project dependency) — replaced with stdlib `urllib.request`. (3) `python-socketio` async client requires `aiohttp` as a transport layer — installed in venv (not added to requirements.txt, test-only). (4) Port 8000 was held by the previous session's server — closed manually before restarting.

**Verification:** All 10 test script assertions passed: GET /health → 200, socket connect + register → game_state_update received with turn=1 and council_extensions_remaining=3, council_extension event → broadcast with extensions decremented to 2 and turn_time_limit at 70, disconnect → server still healthy.

**Comprehension check:** Asked why `register` uses targeted `to=sid` emit instead of calling `broadcast_game_state()`. Answer: "Efficiency" — all other connected clients already have the current state; broadcasting on every connect would be redundant. Correct, no follow-up needed.

---

### Step 5: Frontend scaffold + socket connection + type generation

**What was built:** `react-router-dom` installed (`--legacy-peer-deps` required, same TS6/openapi-typescript conflict as step 1). `src/socket.ts` — shared socket.io-client instance pointed at localhost:8000 with auto-reconnect. `src/types.ts` — stub placeholder (overwritten by `npm run generate-types` on each dev start). `src/store.ts` — `GameStateProvider` React Context holding live `GameState` mirror (updated on every `game_state_update` socket event) and `PlayerIdentity` read/written from localStorage (defaults: player_transport/transport, new UUID). `src/hooks/useSocket.ts` — registers player identity with backend on socket connect; re-registers if identity changes. `src/hooks/useGameState.ts` — thin hook over `useGameContext`. `src/views/CentralScreen/index.tsx` and `src/views/PlayerPhone/index.tsx` — placeholder divs. `src/App.tsx` rewritten with React Router (`/central`, `/phone`, catch-all redirect to `/central`); `useSocket()` called at app root so registration fires regardless of route. `src/main.tsx` wraps app in `GameStateProvider`. `vite.config.ts` adds `/socket.io` proxy to localhost:8000 (WebSocket-aware). `package.json` scripts: `generate-types` added, `dev` updated to `npm run generate-types && vite`.

**Engagement:** Grant paused before `store.ts` was written to ask for a full explanation of the file. Received walkthrough of TypeScript syntax (type imports, interfaces, generics, `| null`), and the store's role in the architecture. Then asked two follow-up questions: (1) where each layer physically runs (laptop vs browser), and (2) what TypeScript compilation does and why React is called React rather than "HTML functions". Both questions answered in depth before proceeding. Strong conceptual engagement — building mental model of the full stack before writing code.

**Verification:** `npm run dev` passed after renaming `store.ts` → `store.tsx` (JSX in a `.ts` file caused a parse error). Browser refresh required to capture socket connection in DevTools Network tab — expected. Socket polling visible in Network WS filter and in uvicorn backend terminal. React DevTools installed during this step; GameStateProvider Context confirmed showing live gameState after refresh.

**Comprehension check:** Asked which statement is true about game state when `/central` and `/phone` are open in separate tabs. Answer: "Shared — one object, both tabs read from it" — incorrect. Correct answer: each tab runs its own independent React app with its own copy of gameState, both updated independently by backend broadcasts. Explanation given: no shared memory between browser tabs; the backend is the single source of truth that keeps them in sync.

**Issues encountered:** `store.ts` → `store.tsx` rename required (JSX parse error). `--legacy-peer-deps` expected and applied without friction.

---

### Step 6: Central screen city map (React Flow)

**What was built:** `src/components/DistrictNode.tsx` (custom React Flow node — district name, colour-coded node_type badge, railway station and canal wharf indicators), `src/components/WaypointMarker.tsx` (SVG circle rendered along edge paths, colour-coded by waypoint status with native browser tooltip via `<title>`), `src/components/CanalEdge.tsx` (custom React Flow edge — straight path via `getStraightPath`/`BaseEdge`, colour-coded by segment status, dashed for proposed, waypoint markers interpolated along path using `t = (i+1)/(length+1)`), `src/components/RailwayEdge.tsx` (dark iron-red edge, no waypoint detail). `src/views/CentralScreen/CityMap.tsx` maps `city_map.nodes` → React Flow nodes and `canal_segments`/`railway_segments` → React Flow edges; `edgeHandles()` computes which side of each node an edge should enter/exit by comparing normalised node positions; `ConnectionMode.Loose` allows source-to-source handle connections. `src/views/CentralScreen/index.tsx` updated to two-column layout (map left, dashboard placeholder right) using `position: fixed; inset: 0` to bypass the `#root` width constraint.

**Verification:** Map visible at localhost:5173/central with district nodes, canal edges, and waypoint dots. Complete segments showing green waypoints confirmed. Pan and zoom working.

**Issues encountered:** (1) Nodes initially too large, obscuring edges — reduced padding, font size, minWidth. (2) Edges connecting at top/bottom only — added handles at all four sides of DistrictNode with IDs (top/right/bottom/left) and `edgeHandles()` direction computation in CityMap.tsx.

**Comprehension check:** Asked how CityMap.tsx decides which side of a node an edge exits from. Answer: "edgeHandles() compares node positions" — correct.

**Iterate flag:** Grant noted the map could be visually improved further. Saved to memory for /iterate (candidate improvements: bezier edge routing, minimap, zoom-level-aware labels).

### Step 7: Central screen full dashboard

**What was built:** Four new components wired into the CentralScreen right panel. `MetricsDash.tsx` — three headline metric bars (Road Rage, Canal Efficiency, Aesthetic) with colour coding reflecting value direction (Road Rage red when high; Efficiency/Aesthetic green when high), a quarterly stats grid (citizen happiness, horse pollution, accidents, projects delayed, tradies non-billing), department budget figures, and a row of summary chips for polling, economy, and cycle. `InfluenceMeter.tsx` — two labelled progress bars (Canal Party blue, Railway Party red), both 0–100 scale, with "APPROACHING CROSSOVER" amber banner within 10 points and "RAILWAY CRISIS" red banner when railway overtakes canal; shows railway phase and activation threshold. `EventFeed.tsx` — scrollable list of `game_state.event_log` entries rendered newest-first using `[...event_log].reverse()`; each row shows a colour-coded dot by event type (milestones gold, crises red, agent events green/red, extensions amber, default grey), turn/cycle stamp, and description. `VotePanel.tsx` — conditionally rendered when `pending_vote` is non-null; shows vote options with current tally and mayor tiebreaker badge; returns `null` when no vote is active. `CentralScreen/index.tsx` updated: dashboard panel widened from 300px to 360px, rebuilt as a flex column with VotePanel → InfluenceMeter → MetricsDash → EventFeed (EventFeed takes flex: 1 and scrolls).

**Issue encountered:** `EventFeed.tsx` used `import { components } from '../../types'` — TypeScript interfaces have no runtime value, so Vite threw "does not provide an export named 'components'". Fixed with `import type { components }`.

**Verification:** Grant confirmed the dashboard rendered correctly — MetricsDash showing all metrics and budgets, InfluenceMeter showing Canal at 50 and Railway at 20 with no crisis banner, EventFeed showing event count (empty or connection event from seed), VotePanel not visible (no pending_vote in fresh scenario).

**Comprehension check:** Asked how VotePanel takes up no space when there's no active vote. Answer: "Returns null" — correct. Explained: `return null` means React renders nothing and the component has no DOM presence. `display: none` would still occupy layout space.

---

### Step 8: Player phone (ReportQueue + ReportCard + AgentRoster + TurnTimer + ExtensionButton + VoiceButton stub)

**What was built:** Seven new files under `src/views/PlayerPhone/`. `index.tsx` — full layout replacing the placeholder: header with role badge and councillor name, controls row (TurnTimer + ExtensionButton + VoiceButton), ReportQueue list, and conditional ReportCard when a report is selected. `ReportQueue.tsx` — filters `pending_reports[player_id]` to PENDING status, sorts urgent-first then by turn_deadline, shows title/domain badge/urgency indicator/defer_count badge. `ReportCard.tsx` — full report detail with options filtered by councillor skill level (min_skill_level check against councillor.skills); buttons: Choose (emits player_action), Delegate (opens AgentRoster modal), Defer (only if not urgent and defer_count < 2), Flag for Council. `AgentRoster.tsx` — fixed-position modal listing player agents with name, specialisations, risk profile label, track record, hiring cost. `TurnTimer.tsx` — listens for `turn_started` socket event; starts setInterval countdown; falls back to static `turn_time_limit` display until step 9 activates it. `ExtensionButton.tsx` — reads council_extensions_remaining from game state, disabled at 0, emits council_extension with player_id payload. `VoiceButton.tsx` — mic button stub showing "Voice commands coming in step 11" tooltip on press. Backend: added one seeded Report (Market Embankment Survey Request, 3 options, LOW/MEDIUM/HIGH risk) to `scenario_fresh_game()` for verification; fixed `council_extension` socket handler to accept optional data (`data: dict | None = None`).

**Issues encountered:** (1) `player_id` localStorage default was `'player_transport'` but scenario uses `'p_transport'` — required clearing localStorage and fixing the default in `store.tsx`. (2) `socket.emit('council_extension')` sent no payload; Python handler required a `data` argument — crashed with `TypeError: council_extension() missing 1 required positional argument: 'data'`. Fixed by making `data` optional on the server and sending `{ player_id }` from the client.

**Verification:** Grant confirmed: report queue visible with seeded report, ReportCard opens with 3 options on tap, Choose emits `player_action`, ExtensionButton decremented from (3) to (2), COUNCIL_EXTENSION event appeared in EventFeed on /central. Councillor name showing as Claude-generated "Obadiah Fenn" (not hardcoded "Lord William Trentham") — expected, generate-map from step 3 updated player councillors and server has maintained that state.

**Grant's verification observation:** "Events(1) — C1 T1 council extension — p_transport called a council extension. 2 remaining." Correct. The MAJOR_DECISION event from the earlier Choose press was wiped by uvicorn hot-reload when main.py was fixed; only the post-fix council_extension survived.

**Comprehension check:** Asked why the server threw `TypeError: council_extension() missing 1 required positional argument: 'data'`. Answer: "socket.emit sent no payload" — correct. Python-socketio called the handler with only `sid`; the signature required a second argument `data`.

**Layout flag:** EventFeed on /central only visible after significant browser zoom-out — MetricsDash is consuming most of the right panel height. Flagged for /iterate alongside the existing city map visual polish flag.

---

### Step 9 — Turn loop + effects engine

**File split rationale.**
Turn logic split across `factions.py`, `map.py`, `elections.py`, and `engine.py` — one concern per file. `engine.py` is the top-level orchestrator and the only public entry point. Each sub-module is independently testable, and the separation mirrors the spec's domain sections exactly.

**Circular import resolution.**
`elections.py` uses lazy imports (inside function bodies) for `map.check_canal_connectivity` to break the `elections → map → state → elections` cycle. All other cross-module imports are top-level.

**Metric update order.**
Inside `advance_turn`: effects → construction → `update_metrics` → `check_cycle_end`. `update_metrics` runs *before* `check_cycle_end`, so the election check always uses freshly recomputed polling — not a stale value from the previous turn.

**Road rage formula (step c).**
`target = road_freight_pct × RoadRage.freight_weight + horse_pollution × RoadRage.pollution_weight`, nudged at most `RoadRage.max_step_per_turn` per turn. Weights (0.6 / 0.4) and cap (5.0) are in `rules.RoadRage`. Design decision approved during step 9 review.

**Construction auto-chaining.**
When a waypoint's `turns_spent >= construction_turns_required`, it's marked COMPLETE and the next UNSTARTED waypoint in the same segment is automatically set to UNDER_CONSTRUCTION. Players don't need to manually trigger each waypoint.

**`set-field` endpoint design.**
Accepts dot-notation paths (`metrics.election_polling`). Type is inferred from the existing attribute value — float → `float(value)`, int → `int(value)`, else string. One level of nesting only, sufficient for current state shape.

**`election_pressure` scenario note.**
Seeds `citizen_happiness=42` and `canal_efficiency_index=18`, but `update_metrics` recomputes both immediately. Happiness lands ~55 (faction weighted avg) and efficiency lands at 0 (no complete canal segment connecting all major nodes). Polling therefore nudges *up*, not down. Correct engine behaviour — the scenario needs per-faction `happiness` overrides to create realistic pressure. Addressed in step 12 scenarios.

**Game-over inertia.**
`loss_threshold` is 40. `update_metrics` runs first each turn, so polling moves `+= polling_lag × (happiness − polling)` before the check. To trigger game_over on turn 20, polling must be set to ≤36 so the inertia step still lands below 40 at typical happiness values (~55).

**Known issue: railway activation timing.**
The spec defines different activation *cycle/turn* per game length (Beginner: Cycle 3 T1, Standard: Cycle 2 T10, Experienced: Cycle 2 T1). Currently only the influence threshold is checked. Documented in `rules.Railway` with a recommended fix for /iterate.

---

## /checklist

**Build mode:** Step-by-step. Grant chose this deliberately — he's here to learn the stack and the agent workflow, not just ship. Comprehension checks: yes, with notes flagged for post-delivery follow-up. Verification: yes, per-item. Check-in cadence: learning-driven.

**Git:** Grant has Git installed but has never used it. Build agent will walk through every git command. Repo initialization is part of step 1.

**Sequencing decisions and rationale:**
- Data models (step 2) before everything else — `game/state.py` is the single import foundation; nothing can work without it.
- Dev seeding included in step 2 — gives a validation loop (FastAPI /docs as "object browser") before any frontend exists. This was Grant's instinct and it's correct.
- AI map generation (step 3) third — high-risk Claude integration; do it early while there's room to fix problems. The seeded state from step 2 is replaced by a real generated city after this.
- WebSocket server (step 4) before frontend — the backend must exist before the frontend can connect to it.
- React Flow city map (step 6) placed early in the frontend sequence — highest-risk new technology; surface problems before building on top of it.
- Turn loop + effects engine (step 9) before Claude report generation (step 10) — the engine must exist before Claude-generated reports can flow through it.
- Admin/dev mode (step 12) last of the build items — depends on everything else being in place, but the named scenarios need real game state models to seed from.

**13 items total. Estimated build time: 5–7 hours active.** Grant has 2 hours tonight (April 27) + full day April 28 (3–5 × 2-hour sessions) + Wednesday April 29 morning (until midday NZT gym appointment). Total available: 10–14 hours. Very comfortable — no squeeze.

**What Grant was confident about:** Sequencing logic — his initial instinct (backend first, data models, seeding, object browser) was correct and required minimal adjustment. He independently identified the right foundation order.

**What Grant needed guidance on:** Git (never used it; walks through every command in the build). TypeScript arrow functions flagged in the spec for /build walkthrough.

**Submission planning:** Grant is outcome-agnostic — he cares about the integrity of the work and the learning process, not the submission polish. Simple submission: GitHub push + basic Devpost form. No deployment required. The pivot story (from The Pivot Story section below) is the natural Devpost description if needed.

**Post-hackathon:** Grant is committed to continuing development after the April 29 deadline. The larger vision (era transitions, full 6-player mode, Dunbar-scale agents) is explicitly a future project. The curriculum's /iterate and /reflect commands are next after submission.

**Deepening rounds:** Zero deepening rounds. Checklist is more procedural than earlier planning commands — the heavy design thinking happened in /spec. Grant accepted the proposed sequence without pushback and confirmed the structure immediately. His instinct and the proposed order aligned closely from the start.

**Active shaping:** Grant engaged directly with sequencing logic — his opening answer named the right foundational order (minimal backend → data structures → game engine → dev seeding → object browser). This wasn't passive acceptance; he understood the dependency chain intuitively from his C#/Delphi background. The main additions from the conversation were: making the "object browser" explicit as FastAPI /docs, positioning React Flow early as a high-risk item, and clarifying that admin/dev mode goes last.

---

## The Pivot Story
*(Captured for use in /reflect — this is the narrative thread worth telling on the Devpost submission page)*

The scope doc described Civic Engine as a game about managing technological era transitions — canals giving way to railways giving way to electrification. It was a good idea. But during /prd, Grant looked up the real history and found that those transitions took 60+ years. Historically-based era pacing would be implausible in a 60-minute game.

Rather than patch the problem, Grant pivoted the entire arc. Instead of transitions happening *to* the players, the players would have a *purpose*: complete the canal network before the railway party rises to dominance. The administration isn't just managing a city — it's racing a rival vision of the future.

That one decision cascaded into better design across the board:
- The railway party became a rival faction with a growing influence meter, not just background flavour
- Canal Efficiency became a headline metric to race against railway efficiency — a dynamic threshold, not an arbitrary number
- The network effect made strategic sense: a half-built canal is weak; a connected one is competitive
- Horse pollution became a Road Rage driver and a public health argument *for* the canal — historically accurate and mechanically useful
- Canal Mania (the real 1790s speculative bubble) became a triggerable game event
- Three canal completion tiers (Bronze/Silver/Gold) replaced the prestige bid, giving players something to chase at every level of ambition

The lesson: **constraints don't kill ideas, they focus them.** Paring back for a demo forced a design decision that made the game significantly better. The canal completion arc is more coherent, more urgent, and more teachable than era transitions would have been.

This is also a demonstration of what spec-driven development with a coding agent looks like in practice: the thinking and planning *before* any code is written is where the real design work happens. The build will be faster and more directed because of this session.
