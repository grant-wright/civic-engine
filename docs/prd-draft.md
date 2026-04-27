# Civic Engine — Product Requirements (Draft v1)

## Problem Statement
Complex cooperative board games require players to navigate shared decisions with real tradeoffs — but most digital implementations flatten this into turn-based solo play. Civic Engine puts 3 players in the roles of Victorian city councillors managing transport infrastructure through technological eras, with Claude AI powering the city's citizens, events, and voice interface. The challenge: every decision has political consequences, and the administration survives or falls together.

---

## User Stories

### Epic: Game Setup

- As a player sitting down to a new game, I want to arrive at a living Victorian city and receive a political briefing, so that I understand what kind of city I've inherited before making any decisions.
  - [ ] Central screen shows an isometric city map with existing infrastructure (roads, canals, buildings) visible
  - [ ] An initial council meeting scene triggers automatically, with faction representatives present
  - [ ] Each faction representative delivers a brief introduction covering their position, demands, or grievances
  - [ ] A dossier is available to read in full OR reveals progressively as the meeting plays out
  - [ ] Players can read ahead in the dossier without waiting for the meeting to progress

- As a player, I want to be assigned a council role (Finance, Infrastructure, or Transport), so that I have a clear domain of ownership and responsibility.
  - [ ] Each of the 3 players is assigned one of the three transport-focused councillor roles
  - [ ] Each player sees their councillor's profile on their phone: political alignment, core values, professional background, starting skills
  - [ ] The mayor NPC is established as tiebreaker for deadlocked votes
  - [ ] 12 available councillors are visible; each player selects one to fill their role

### Epic: Turn Structure & Decision-Making

- As a councillor, I want to receive reports relevant to my domain on my phone, so that I can act on my area of the city without waiting for other players.
  - [ ] Reports arrive from three sources: scheduled (quarterly/annual), threshold-triggered (metric crosses a line), and Claude-generated events
  - [ ] Each report presents 1–3 options to choose from
  - [ ] Reports are private to the relevant councillor unless contested or escalated
  - [ ] All three players can act on their reports simultaneously (parallel play)

- As a councillor, I want to escalate a decision to the full council, so that contested or complex choices get collective input.
  - [ ] Any player can manually flag a decision for council vote
  - [ ] System automatically escalates decisions that contradict another councillor's pending choice
  - [ ] Council can define policies that automatically escalate certain decision types
  - [ ] Contested decisions appear on the central screen for all players to see
  - [ ] Players can negotiate peer-to-peer before a formal vote
  - [ ] Mayor NPC casts tiebreaker vote on deadlocked 1–1 splits
  - [ ] Conflict detection pauses both conflicting decisions until resolved

- As a group of players, I want council votes to feel decisive and visible, so that major decisions feel like real governance moments.
  - [ ] Voting UI appears on central screen when a decision goes to full council
  - [ ] Each player votes via their phone
  - [ ] Result is displayed on central screen
  - [ ] Outcome updates game state immediately

### Epic: City Map & Visual Evolution

- As a player watching the central screen, I want to see the city change as decisions land, so that progress feels visible and earned.
  - [ ] City map displays current infrastructure: roads, canals, rail lines, tram routes, buildings
  - [ ] Approved projects show a construction-in-progress visual
  - [ ] Completed projects update the map with a new visual state (new terminus, electrified tram lines, widened road, cycleway)
  - [ ] Major disruption events (fire, flood) can interrupt construction and show a disrupted state
  - [ ] Visual style is Victorian steampunk: cobblestones, gas lamps, industrial aesthetic

- As a player, I want the Road Rage Index to be visible and dramatic on the central screen, so that I can feel the city's mood at a glance.
  - [ ] Road Rage Index is prominently displayed on central screen
  - [ ] Index rises with: congestion, delays, diversions, excessive tolls, more intersections, accidents, restrictive road rules
  - [ ] Index falls with: faster journeys, more route options, lower average/max journey times, improving conditions
  - [ ] Index updates each round after decisions resolve

### Epic: Metrics & Elections

- As a player, I want to track the quarterly metrics panel, so that I know how the city is performing and can anticipate the election.
  - [ ] Central screen displays: Road Rage Index, citizen happiness, budget, accidents, projects delayed, tradies non-billing
  - [ ] Metrics update each round
  - [ ] Citizen happiness is the primary election polling driver
  - [ ] Crisis conditions can elevate other metrics' electoral importance

- As a group of players, I want elections to be high-stakes collective moments, so that every game cycle builds toward a genuine threat.
  - [ ] Elections occur on a defined cycle (approximately every N rounds — to be specified in /spec)
  - [ ] Election polling is visible and tracks against citizen happiness throughout the cycle
  - [ ] Losing an election triggers hard game over for all players
  - [ ] Game over screen shows how far the administration got
  - [ ] Surviving 4 elections is a win condition (modest victory)

### Epic: Citizen Agents & Faction Reactions

- As a player, I want citizen factions to react to my decisions with personality and political opinion, so that the city feels alive and decisions have human consequences.
  - [ ] Each faction has a Claude-generated personality, values, and political sensitivities
  - [ ] Factions react to decisions that affect their interests
  - [ ] Reactions surface as: central screen notifications, relevant player phone alerts, and changes to faction happiness meters
  - [ ] Faction happiness feeds into overall citizen happiness and election polling

### Epic: Era Transitions

- As a player, I want era transitions to arrive as dramatic turning points, so that the game has genuine tension peaks beyond elections.
  - [ ] Transitions trigger automatically when city metrics cross defined thresholds
  - [ ] Factions and events can give advance warning before a transition arrives
  - [ ] Council decisions (e.g., passing a law to close the canals) can deliberately trigger a transition
  - [ ] Transition events surface on central screen as a dramatic moment
  - [ ] Transition consequences include: displaced workers, stranded capital, faction anger or excitement, visual changes to city map
  - [ ] Three eras: Victorian (canals/horse trams) → Industrial (steam rail) → Modern (electric trams, cycleways)

### Epic: Voice Commands

- As a councillor, I want to issue commands to my domain by voice on my phone, so that gameplay feels natural and fluid.
  - [ ] Voice input is per-player on their own phone (not shared mic)
  - [ ] Claude interprets natural language commands scoped to the player's domain
  - [ ] Valid command is dispatched as a game action
  - [ ] Result of the command appears on central screen
  - [ ] If the command triggers a conflict, standard conflict resolution flow begins

### Epic: Prestige Bid

- As a group of players, I want to pursue a prestige hosting bid as a long-arc goal, so that the game has an aspirational target beyond mere survival.
  - [ ] Prestige bid meter is visible on central screen
  - [ ] Specific metric thresholds unlock the bid (thresholds to be defined in /spec)
  - [ ] Achieving the prestige bid triggers a celebration ending
  - [ ] Civic pride from meeting bid milestones begins to influence election polling

### Epic: Game End

- As a player at game end, I want a satisfying summary of what the administration achieved, so that the journey feels meaningful regardless of outcome.
  - [ ] Central screen plays a replay of the city's visual transformation over time
  - [ ] Each player's phone shows a personal summary: major milestones, decisions, achievements
  - [ ] Each player receives a personal popularity/friction score
  - [ ] End state is clearly communicated: hard game over (election loss), modest win (survived 4 elections), or prestige win (hosting bid achieved)

---

## What We're Building
The core playable demo for 3 players covering one full game cycle:

1. **Game setup** — Isometric Victorian city map, faction dossier/meeting scene, councillor role assignment
2. **Turn loop** — Parallel private reports on phones, 1–3 option decisions, conflict detection, council votes on central screen
3. **City map evolution** — Construction-in-progress and completed visuals for approved transport projects
4. **Road Rage Index** — Prominent, reactive, fed by city state
5. **Quarterly metrics panel** — Citizen happiness, budget, accidents, tradies non-billing, projects delayed
6. **Citizen agent reactions** — Claude-powered faction responses to decisions, surfaced on screen and phone
7. **Era transitions** — Threshold-triggered dramatic turning points with faction consequences
8. **Election mechanic** — Hard game over on loss; four-election survival as win condition
9. **Prestige bid meter** — Long-arc goal with celebration ending
10. **Voice commands** — Per-player on phone, scoped to their domain
11. **Game end** — City replay, personal scorecards, legacy scores

---

## What We'd Add With More Time

- **Full 6-player mode** — All six council roles active, with Business Units, Building, Community Relations, and Public Utilities domains
- **Dunbar-scale agent networks** — Individual AI agents per faction member rather than faction-level groups
- **Forking timelines** — Counterfactual replay: "what if we'd kept the canals?"
- **Candidate promotion mechanic** — Players promote candidates for future elections; winners enter the councillor pool
- **Council reshuffle** — Players can reassign councillors to new roles at a political cost
- **Classroom version** — Pared-down educational edition
- **Multi-stage construction** — Visual progress stages for major projects beyond in-progress/complete
- **Peer negotiation UI** — Dedicated interface for councillors to negotiate before formal votes
- **Generative art evolution** — AI-directed image generation for city aesthetic shifts across eras

---

## Non-Goals

- **Physical components** — No physical board, cards, or tokens. Central laptop screen only.
- **Individual agent networks** — Hackathon demo uses faction groups, not 150 individual agents per player (Dunbar networks are a future feature)
- **Multi-city campaigns** — One city, one campaign
- **Full party policy engine** — Party image exists as a stat; no policy tree this build
- **The spy / irreverent councillor archetypes** — Cut by Grant; not this build

---

## Open Questions

- **Election cycle length** — How many rounds per election? Needs a number before /spec. *(Answer before /spec)*
- **Prestige bid thresholds** — What specific metric values unlock the bid? *(Answer before /spec)*
- **Era transition thresholds** — What triggers the shift from Victorian → Industrial → Modern? *(Answer before /spec)*
- **Starting city state** — What infrastructure exists at game start? Is it randomised or fixed? *(Can wait until build)*
- **Faction count for demo** — How many factions in the starting dossier? *(Can wait until build)*
- **Councillor roster** — Are the 12 councillors fixed archetypes or procedurally generated each game? *(Can wait until build)*
- **Agent hiring mechanics** — What do hired subagents actually do within a domain, and what does managing them look like on the phone? *(Needs more detail — surfaced in deepening round)*
