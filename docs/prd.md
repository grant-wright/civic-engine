# Civic Engine — Product Requirements

## Problem Statement
Complex cooperative decision-making games are rarely playable digitally in a way that preserves genuine political tension and human stakes. Civic Engine puts 3 players in the roles of Victorian city councillors with a mandate: complete the canal network before the railway party rises to dominance. Every transport decision affects citizen happiness, Road Rage, and the canal's progress — and the administration survives or falls together. Claude AI powers the citizens, events, voice interface, and the agents councillors hire to get things done.

---

## User Stories

### Epic: Game Setup

- As a player sitting down to a new game, I want to arrive at a living Victorian city and receive a political briefing, so that I understand what kind of city and what kind of opposition I've inherited before making any decisions.
  - [ ] Central screen shows an isometric Victorian city map with existing infrastructure visible: roads, canals (partial), buildings, horse-drawn traffic
  - [ ] An initial council meeting scene triggers automatically
  - [ ] Faction representatives are present in the meeting; each delivers a brief introduction covering their position, demands, and grievances
  - [ ] A faction dossier is available — players can read it in full OR let it reveal progressively as the meeting plays out
  - [ ] The railway party is introduced as the rival faction with a competing vision for the city's future
  - [ ] Players can read ahead in the dossier without waiting for the meeting to progress

- As a player, I want to be assigned a council role, so that I have a clear domain of ownership and a specific councillor to play as.
  - [ ] Three roles are available: Finance, Infrastructure, Transport
  - [ ] Each player selects one of the 12 available councillors to fill their role
  - [ ] Each player sees their councillor's profile on their phone: political alignment, core values, professional background, starting skills
  - [ ] The mayor NPC is established as tiebreaker for deadlocked votes
  - [ ] Council party mandate is visible: complete the canal network

### Epic: Turn Structure & Decision-Making

- As a councillor, I want to receive domain-specific reports on my phone and act on them simultaneously with other councillors, so that turns move quickly and my expertise matters.
  - [ ] Reports arrive from three sources: scheduled (quarterly/annual), threshold-triggered (metric crosses a line), and Claude-generated events
  - [ ] Each report presents 1–3 options to choose from
  - [ ] Reports are private to the relevant councillor by default
  - [ ] All three players act on their reports simultaneously (parallel play)
  - [ ] A councillor can delegate a report/decision to a hired agent instead of deciding personally

- As a councillor, I want to escalate a decision to the full council when it matters, so that contested or complex choices get collective input.
  - [ ] Any player can manually flag a decision for council vote
  - [ ] System automatically detects when two councillors' choices contradict each other and pauses both
  - [ ] Council can define policies that automatically escalate certain decision types
  - [ ] Contested decisions appear on the central screen for all players to see and discuss
  - [ ] Players can negotiate peer-to-peer before a formal vote is called
  - [ ] Formal votes are cast on player phones; result displays on central screen
  - [ ] Mayor NPC casts tiebreaker on deadlocked 1–1 splits

### Epic: Agent Hiring & Delegation

- As a councillor, I want to hire specialist agents for my department, so that I can delegate tasks and access capabilities beyond my own councillor's skills.
  - [ ] Each councillor has an agent roster visible on their phone
  - [ ] Agents are domain-specific specialists (Finance: analysts, assessors, loan brokers; Infrastructure: engineers, surveyors, construction crews; Transport: route planners, canal inspectors, freight coordinators)
  - [ ] Hiring an agent costs departmental budget
  - [ ] Retiring an agent frees up budget
  - [ ] Agent profile shows: abilities, specialisations, risk profile

- As a councillor delegating to an agent, I want the outcome to reflect that agent's abilities — for better or worse — so that delegation is a genuine strategic choice.
  - [ ] When delegating a report/decision, the agent handles it autonomously and reports back
  - [ ] Agent outcomes can be: better than the councillor would have achieved (finds a smarter canal route, faster implementation), equivalent, or worse (cuts corners, creates downstream problems)
  - [ ] Agents may unlock alternative options not available to the councillor directly
  - [ ] Agents can execute faster than the councillor acting alone
  - [ ] Failed or poor agent decisions can create new reports/problems in future turns
  - [ ] A councillor can review an agent's recommendation before it's implemented (at a time cost)

### Epic: Canal Network & City Map

- As a player watching the central screen, I want to see the canal network grow and connect, so that progress is visible and the network effect is tangible.
  - [ ] City map displays current infrastructure: roads, partial canal segments, horse-drawn traffic, buildings
  - [ ] Approved canal segments show a construction-in-progress visual
  - [ ] Completed segments update the map showing a finished canal with barge traffic
  - [ ] When canal segments connect to form a network, a visual and metric shift reflects the network effect
  - [ ] Connected canal visibly relieves road traffic (fewer horses, less congestion shown)
  - [ ] Major disruption events (fire, flood) can interrupt construction and show a disrupted state
  - [ ] Visual style is Victorian steampunk: cobblestones, gas lamps, smokestacks, industrial aesthetic

- As a player, I want canal completion milestones to be celebrated as they happen, so that progress feels earned and meaningful.
  - [ ] First canal connection: notification on central screen, Canal Efficiency index jumps
  - [ ] Engineering feat completed (aqueduct over road or river): special event card displayed
  - [ ] Canal Mania triggered (network reaches critical mass): investment event fires, Finance gets windfall with bubble risk
  - [ ] Full coverage achieved: celebration win sequence

### Epic: Metrics

- As a player, I want to track two headline metrics — Road Rage and Canal Efficiency — so that I can see both the problem and the solution at a glance.
  - [ ] **Road Rage Index** is prominently displayed on central screen
    - [ ] Rises with: congestion, delays, diversions, excessive tolls, intersections, accidents, restrictive road rules, horse volume, horse pollution events
    - [ ] Falls with: faster journeys, more route options, lower average/max journey times, canal segments absorbing freight
  - [ ] **Canal Efficiency Index** is displayed alongside Road Rage
    - [ ] Starts low (partial, disconnected canal)
    - [ ] Rises as segments complete and connect
    - [ ] Jumps when network effect activates (connected nodes)
    - [ ] Reflects water transport's goods-per-load advantage over horse and cart
  - [ ] Both metrics update each round after decisions resolve

- As a player, I want to track the quarterly metrics panel, so that I can anticipate the election and manage departmental health.
  - [ ] Central screen displays: Road Rage Index, Canal Efficiency Index, citizen happiness, budget, accidents, projects delayed, tradies non-billing
  - [ ] Metrics update each round
  - [ ] Citizen happiness is the primary election polling driver
  - [ ] Horse pollution and public health pressure visible as a secondary metric

### Epic: Citizen Agents & Faction Reactions

- As a player, I want citizen factions to react to council decisions with distinct personalities, so that the city feels alive and decisions carry human consequences.
  - [ ] Each faction has a Claude-generated personality, values, transport priorities, and political sensitivities
  - [ ] Factions react to decisions that affect their interests (canal workers energised by canal progress; car-dependent commuters indifferent; railway investors growing restless)
  - [ ] The railway party faction grows in influence each round the canal makes insufficient progress
  - [ ] Reactions surface as: central screen notifications, relevant player phone alerts, changes to faction happiness meters
  - [ ] Faction happiness feeds into overall citizen happiness and election polling

### Epic: Railway Party & Time Pressure

- As a group of players, I want to feel the railway party's growing threat, so that the canal mandate has genuine urgency.
  - [ ] Railway party influence meter is visible on central screen
  - [ ] Influence grows each round based on canal progress (slow progress = faster railway rise)
  - [ ] Railway party generates competing reports and lobbying events that councillors must respond to
  - [ ] If railway party influence reaches a threshold before canal completion, a crisis event fires
  - [ ] Coal and steel scarcity constrains railway party in early game (their window is not immediate)
  - [ ] Railway party's rise can be slowed but not stopped — canal completion is the only counter

### Epic: Elections

- As a group of players, I want elections to be high-stakes collective moments, so that every game cycle builds toward a genuine threat.
  - [ ] Setup screen offers three game lengths: 4 cycles (beginner), 5 cycles (standard), 6 cycles (experienced)
  - [ ] Each cycle is 20 turns; each turn has a 40-second time limit
  - [ ] Election polling tracks citizen happiness throughout each cycle and is visible on central screen
  - [ ] Losing an election triggers hard game over for all players simultaneously
  - [ ] Game over screen shows how far the canal got and key decisions made
  - [ ] Surviving all cycles without Gold completion is a modest win; canal completion tiers determine final win state

### Epic: Voice Commands

- As a councillor, I want to issue commands to my domain by voice on my phone, so that gameplay feels natural and fast.
  - [ ] Voice input is per-player on their own phone (not shared mic)
  - [ ] Claude interprets natural language commands scoped to the player's councillor domain
  - [ ] Valid command dispatches as a game action
  - [ ] Result of the command appears on central screen
  - [ ] If command triggers a conflict with another councillor's pending action, standard conflict resolution flow begins

### Epic: Game End

- As a player at game end, I want a satisfying summary of what the administration achieved, so that the journey feels meaningful regardless of outcome.
  - [ ] Central screen plays a time-lapse replay of the canal network's growth over the game
  - [ ] Each player's phone shows a personal summary: major decisions, milestones, achievements, agent outcomes
  - [ ] Each player receives a personal popularity/friction score
  - [ ] Win state clearly communicated:
    - [ ] **Hard game over** (election loss): administration falls, canal progress shown, epitaph displayed
    - [ ] **Modest win** (survived 4 elections, canal connected): city carries on, canal works
    - [ ] **Full win** (canal coverage complete): celebration sequence, city transformed
    - [ ] **Prestige win** (Canal Mania or engineering feat achieved en route): special commendation added

---

## What We're Building
A playable 3-player demo covering one full game cycle:

1. **Game setup** — Isometric Victorian city, faction dossier/meeting scene with railway party as rival, councillor role assignment (Finance, Infrastructure, Transport)
2. **Turn loop** — Parallel private reports on phones, 1–3 option decisions, conflict detection and resolution, council votes on central screen
3. **Agent system** — Hire/retire domain specialists; delegate decisions with genuine risk/reward outcomes
4. **Canal network** — Segment-by-segment construction on city map, connected network triggering efficiency jump, milestone celebrations
5. **Dual metrics** — Road Rage Index and Canal Efficiency Index as headline measures, quarterly panel for budget/happiness/accidents
6. **Railway rival** — Growing influence meter, competing lobbying events, coal/steel constraint in early game
7. **Citizen factions** — Claude-powered reactions to decisions surfaced on screen and phone
8. **Elections** — Hard game over on loss; four-election survival as modest win
9. **Voice commands** — Per-player on phone, scoped to domain
10. **Game end** — Canal time-lapse replay, personal scorecards, tiered win states

---

## What We'd Add With More Time

- **Full 6-player mode** — All six council roles active with distinct domains and mechanics
- **Dunbar-scale agent networks** — Individual AI citizen agents rather than faction-level groups
- **Council reshuffle mechanic** — Reassign councillors to new roles at a political cost
- **Candidate promotion** — Players back candidates for future elections who may or may not win
- **Dilemma system** — Structured "competing goods" decisions (heritage precinct vs. cycleway) surfaced as special event cards
- **Era transitions** — Full Victorian → Industrial → Modern arc for longer campaign play
- **Forking timelines** — Counterfactual replay: "what if we'd prioritised roads?"
- **Generative art evolution** — AI-directed city aesthetic shifts as canal network grows
- **Classroom version** — Pared-down educational edition
- **Multi-stage construction** — Visual progress stages for major projects
- **Agent reputation system** — Agents build track records; past performance informs future delegation risk

---

## Non-Goals

- **Physical components** — No physical board, cards, or tokens. Central laptop screen only.
- **Individual agent networks** — Demo uses faction groups, not Dunbar-scale individual agent networks
- **Multi-city campaigns** — One city, one campaign
- **Full party policy engine** — Party image exists as a stat; no policy tree this build
- **Historical accuracy constraint** — Game is inspired by the canal era, not bound to it. Timescales and events are compressed for playability.
- **The spy / irreverent councillor archetypes** — Cut by Grant; not this build

---

## Game Parameters (Resolved)

- **Election cycle length** — 5 cycles default (20 turns per cycle, 40 seconds per turn ≈ 67 minutes). Setup screen offers 4 cycles (beginners, ≈53 min) / 5 cycles (standard) / 6 cycles (experienced, ≈80 min).
- **Historical period** — Approximately 1775–1800, the critical canal era before railway dominance.
- **Railway crisis trigger** — Fires when railway efficiency overtakes Canal Efficiency Index (dynamic race, not a fixed threshold). Also pressured by: railways claiming map corridors (spatial competition), railway stations making adjacent canal construction more expensive.
- **Railway negotiation** — Agents can propose working with the railway faction as a compromise option; accepted compromises carry a prestige/influence cost with canal-mandate supporters.
- **Canal win tiers:**
  - **Bronze (connected win)** — All major nodes linked
  - **Silver win** — All major nodes + all nodes of one type (e.g. all ports, all industrial yards)
  - **Gold (full coverage win)** — Every district connected, 80% map coverage

**Full win state matrix:**

| Canal completion | Elections survived | Outcome |
|---|---|---|
| None | 4–6 | Survived (no canal legacy) |
| Bronze+ | 4–6 | Modest win |
| Silver | 4–6 | Strong win |
| Gold | 4–6 | Celebration — canal era complete |
| Any | Lost before cycle end | Hard game over |

## Open Questions

- **Starting canal state** — What segments already exist at game start? Fixed or randomised? *(Can wait until build)*
- **Faction count for demo** — How many factions in the starting dossier? *(Can wait until build)*
- **Agent failure mechanics** — When an agent decision goes wrong, what exactly happens? New problem report next turn, construction delay, budget overrun? *(Can wait until build)*
- **Horse pollution mechanic** — Is this a periodic event, a threshold metric, or a constant Road Rage modifier? *(Can wait until build)*
- **Canal Mania bubble risk** — If the investment flood triggers a bubble, what does the burst look like mechanically? *(Can wait until build)*
