# Civic Engine
*(working title — GridLock was v1; steampunk direction may inspire something better)*

## Idea
A cooperative steampunk city-builder board game where 4–6 players are city councillors guiding a Victorian industrial city through technological transitions — canals to railways, steam to electric, horse-drawn trams to subways — while managing citizen happiness, surviving elections, and chasing a prestige hosting bid. Claude AI powers the voice controller, citizen agent personalities, event generation, and evolving generative art. The city on screen looks different at the end of the game than it did at the start.

## Who It's For
Friend groups who enjoy complex cooperative games — the Pandemic Legacy / Spirit Island crowd. Adults who appreciate systemic depth, emergent surprises, and the satisfaction of watching a city visibly transform through their decisions. Primary format: game night around a central screen, each player on their own phone. Secondary: a pared-down classroom version is a named follow-on project, not this build.

## Inspiration & References
- [World of Communities](https://participedia.net/method/world-of-communities-social-impact-game-simulator) — cooperative civic roles, collective victory, no individual winner. Closest structural analog.
- [Frostpunk](https://store.steampowered.com/app/323190/Frostpunk/) — policy decisions with visible systemic consequences, irreversible choices, the emotional weight of a city in crisis. The Hope meter is the model for how the Road Rage Index should *feel*. Also the tension template: era transitions create Frostpunk-style fateful moments.
- [AI Town (a16z)](https://github.com/a16z-infra/ai-town) — AI agents with personalities, memories, and relationships in a simulated town. The north star for citizen agents: coherent inner lives, emergent behavior, not stat cards.
- MiroClaw — AI agent personality networks as game elements. The original seed of the agent-as-character idea.

**Design energy:** Steampunk. Victorian cobblestones, gaslight, smokestacks and industry — overlaid with a smart-city data dashboard. As the game progresses and players build, the aesthetic evolves: gas lamps get wired for electricity, horse-drawn trams become electrified ones, elevated cycleways thread through the old streetscape. The city's *look* is the progress meter made visible.

**Traffic view:** Top-down grid with live simulation — traffic lights cycling, camera-feed aesthetic, volume heat maps. Human metrics front and center: tradies non-billing while sitting gridlocked, days lost to maintenance, accidents per quarter.

## Goals
- Build a playable demo showing the core loop: councillors make transport decisions → technological era advances → Claude-powered citizens react → metrics shift → election and prestige bid update.
- Showcase Claude as the game's nervous system: voice controller, agent souls, event engine, generative art director, multi-agent orchestrator.
- Demonstrate non-zero-sum cooperative play: the tension is managing shared transitions, not competing against each other.
- Capture the emotional truth underneath: civic decisions have human costs. Transitions displace workers. Heritage gets demolished. Someone always pays the price of progress. The game teaches this without preaching it.
- Create something Grant would be genuinely proud to show a group of friends.

## What "Done" Looks Like
After 3–4 hours of building, a working demo with:

**Central screen:**
- A Victorian steampunk city map, top-down grid. Infrastructure visible: roads, canals, rail lines, tram routes. Visual state changes as projects complete — a new railway terminus appears, a canal district fades, gas lamps flicker to electric.
- Road Rage Index prominent and dramatic. Quarterly metrics panel: citizen happiness, budget, accidents, projects delayed, tradies non-billing.

**Setup moment:**
- Factions revealed like card flips — the city's political landscape is randomised or chosen. Players see what kind of city they've inherited before picking their councillor.

**Councillor selection:**
- Each councillor defined by three axes: political alignment, core values, professional background. Inherent starting skills. Skills grow through action and experience during play.
- Councillors have internal value tensions — a bohemian-greenie who values institutional tradition, for instance — that create genuine dilemmas during play.

**Player mobile view:**
- Personal abilities and current skill level. Agent roster. Action queue.

**Voice commands:**
- Player speaks to Claude controller: "assign the building inspector to approve the new tram route on Cathedral Square" → game state updates.

**Citizen agents:**
- Claude-powered faction characters with group profiles and political sensitivities. They react differently to each decision. Their happiness feeds into election polling.
- **Configurable factions — the key replayability mechanic.** Factions are not hardcoded. Each game, the city's political landscape is either randomly drawn or chosen by players — meaning every game you inherit a different set of citizen pressures and alliances. A city heavy with car-dependent commuters plays completely differently from one dominated by a strong cycling-and-transit culture or a powerful canal-workers' guild.
- **Claude generates faction personalities from descriptions, not from code.** Each faction is defined by a profile (demographic makeup, values, transport priorities, historical context). Claude creates the faction's personality, dialogue, and reactions from that description at runtime. Adding a new faction type requires writing a description, not writing new logic. This means the faction library can grow indefinitely.
- Example transport-relevant factions: car-dependent suburbanites, canal workers facing displacement by the railway, railway investors with capital at stake, street traders dependent on foot traffic, cycling advocates, elderly residents prioritising accessibility, labor unions, visiting merchants.

**Era transitions:**
- Pivotal moments when the city's dominant technology shifts. Players must manage the transition: capital stranded in obsolete infrastructure, workers displaced, factions angry or energised. These are the tensest moments outside elections.

**Dilemma system:**
- Decisions that pit competing goods against each other — never two evils. Heritage precinct vs. cycleway. Canal workers' livelihoods vs. railway efficiency. Players can abstain or defer; both carry political consequences.

**Election mechanic:**
- Party polling tracked against citizen agent happiness. Loss = game over. The tension peak of every game cycle.

**Prestige bid meter:**
- Long-arc goal: hosting rights to a city traffic convention or Formula 1 race. Cumulative progress tracked. Specific metric thresholds unlock the bid (to be defined in PRD).

**Random events:**
- Claude generates plausible disruptions given current city state: labor disputes on the canal works, a visiting transport journalist, a rugby match tripling downtown traffic, a storm flooding the low-lying rail yard.

## What's Explicitly Cut
- **Physical board** — central laptop screen. Gains: rollback, automatic rule enforcement, larger virtual canvas. Less tactile; accepted tradeoff.
- **Full Dunbar networks** — 150 agents per player is a full game. Hackathon demo uses simplified named faction groups, not individual agent networks per player.
- **Forking timeline / counterfactual replay** — compelling, architecturally complex. Named future feature.
- **Multi-city scenarios** — one city, one campaign.
- **Physical cards** — all digital.
- **Classroom version** — explicit follow-on project.
- **Full party policy engine** — party image exists as a stat for now, not a full policy tree.
- **The spy / irreverent councillor archetypes** — fun, not this build.
- **Christchurch 2074 Commonwealth Games sim** — personal future project, separate from this game.

## Loose Implementation Notes
- **Stack:** Web app (central screen) + mobile-responsive UI (player phones). Central server manages game state.
- **Claude roles:**
  - Voice controller: speech-to-text → Claude interprets natural language command → game action dispatched
  - Citizen agents: each faction has a Claude system prompt defining personality, values, political sensitivities, and historical context; responds to game events in character
  - Event engine: Claude generates plausible random events given current city state, era, and turn number
  - Generative art: Claude orchestrates image generation for city visual evolution, event cards, faction portraits — aesthetic shifts from Victorian to modern as game progresses
  - Orchestrator: Claude coordinates subagents for parallel processing
- **Era progression:** Victorian (canals/horse trams) → Industrial (steam rail) → Modern (electric trams, cycleways, subways). Visual and mechanical transitions at each shift.
- **Key metric:** Road Rage Index. Visible, dramatic, fun to watch move.
- **Session length target:** 60–90 minutes for a full game night demo.
