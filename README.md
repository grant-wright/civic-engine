# Civic Engine

A real-time cooperative city-building game where three players act as Victorian councillors racing to complete a canal network before the railway party rises to dominance — powered by Claude AI as the game's nervous system.

---

## What it is

Players take roles as Finance, Infrastructure, and Transport councillors in a Victorian city. Each turn they receive private reports on their phones, make decisions simultaneously, and watch their choices ripple through the city on the central screen. Claude generates the events, plays the AI councillors, voices the citizen factions, and interprets spoken voice commands.

The canal is the win condition. The railway is the clock.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, python-socketio |
| AI | Anthropic Claude (claude-sonnet-4-6), tool use + prompt caching |
| Game engine | Pydantic models, NetworkX (canal connectivity) |
| Frontend | React 19, TypeScript, Vite |
| Map | React Flow (@xyflow/react) |
| Real-time | socket.io (WebSocket + polling fallback) |

---

## How to run

### Prerequisites

- Python 3.12+
- Node.js 20+
- An Anthropic API key

### 1. Clone the repo

```bash
git clone <repo-url>
cd civic-engine
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# or: source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create `backend/.env`:

```
ANTHROPIC_API_KEY=your_key_here
ADMIN_TOKEN=dev-admin
```

### 3. Frontend setup

```bash
cd frontend
npm install --legacy-peer-deps
```

Create `frontend/.env`:

```
VITE_ADMIN_TOKEN=dev-admin
```

### 4. Run

In one terminal (backend):

```bash
cd backend
venv\Scripts\uvicorn main:app --reload
```

In a second terminal (frontend):

```bash
cd frontend
npm run dev
```

- Central screen (projector/TV): `http://localhost:5173/central`
- Player phone: `http://localhost:5173/phone`
- API docs: `http://localhost:8000/docs`

### 5. Start a game

Open `/central`, press **Ctrl+Shift+D** to open the dev panel, click **fresh game**, then use the FastAPI docs at `/docs` to call `POST /admin/start-game?token=dev-admin`.

---

## Dev panel

Press **Ctrl+Shift+D** on `/central` to toggle the dev panel (only visible in `npm run dev` mode). It lets you load any named scenario, advance turns, adjust metrics with sliders, and save/restore game state.

---

## Project structure

```
backend/
  api/          FastAPI routers (admin, health)
  claude/       Claude integrations (map gen, events, AI players, voice, citizens)
  game/         Game engine (state, rules, engine, elections, factions, map, scenarios)
  main.py       FastAPI + socketio app entry point
  saves/        Saved maps and game states (gitignored)

frontend/
  src/
    components/ Shared components (DevPanel, DistrictNode, CanalEdge, ...)
    views/
      CentralScreen/   City map + dashboard (MetricsDash, EventFeed, InfluenceMeter, VotePanel)
      PlayerPhone/     Report queue + decisions (ReportCard, VoiceButton, TurnTimer, ...)
    hooks/      useVoiceInput, useSocket, useGameState
    store.tsx   React Context (live game state mirror + player identity)
    socket.ts   Shared socket.io-client instance
```

---

## Built for

Anthropic + Devpost Hackathon, April 2025.

Spec-driven development: the full scope, PRD, and technical spec were written before a single line of code. The design documents are in `docs/`.
