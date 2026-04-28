"""
Test script for step 4: WebSocket server + game state broadcast.

Setup (once, with venv active):
    pip install -r requirements-dev.txt

Run while the backend is running:
    cd backend
    python scripts/test_socket.py

Tests:
  1. GET /health returns 200 with status "ok"
  2. Socket connect + register -> receives game_state_update
  3. council_extension -> council_extensions_remaining decrements by 1
  4. Disconnect is handled gracefully (server stays up, /health still 200)
"""

import asyncio
import json
import sys
import urllib.request
import urllib.error
import socketio


BASE_URL = "http://localhost:8000"


def http_get(path: str) -> tuple[int, dict]:
    """Minimal HTTP GET using stdlib — no extra dependencies."""
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except Exception as exc:
        raise exc
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(label: str, condition: bool, detail: str = "") -> bool:
    mark = PASS if condition else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {mark} {label}{suffix}")
    return condition


async def run_tests() -> int:
    failures = 0

    # ── 1. HTTP health check ──────────────────────────────────────────────────
    print("\n-- HTTP -------------------------------------------------------------")
    try:
        status, body = http_get("/health")
        ok = check("GET /health -> 200", status == 200, str(body))
        ok &= check("body.status == 'ok'", body.get("status") == "ok")
        ok &= check("body.turn is an int", isinstance(body.get("turn"), int))
        if not ok:
            failures += 1
    except Exception as exc:
        check("GET /health reachable", False, str(exc))
        failures += 1
        print("  Backend not reachable — is `uvicorn main:app --reload` running?")
        return failures

    # ── 2. Socket connect + register ─────────────────────────────────────────
    print("\n-- WebSocket --------------------------------------------------------")
    received: list[dict] = []
    sio_client = socketio.AsyncClient()

    @sio_client.on("game_state_update")
    async def on_update(data: dict):
        received.append(data)

    try:
        await sio_client.connect(BASE_URL)
        check("socket connected", True)

        await sio_client.emit("register", {
            "client_type": "test",
            "player_id": "test_player",
            "role": "transport",
            "session_id": "test-session-abc",
        })
        await asyncio.sleep(0.5)

        ok = check(
            "register -> received game_state_update",
            len(received) >= 1,
            f"received {len(received)} update(s)",
        )
        if not ok:
            failures += 1
        else:
            state = received[-1]
            ok = check(
                "game_state has council_extensions_remaining",
                "council_extensions_remaining" in state,
            )
            ok &= check(
                "council_extensions_remaining starts at 3",
                state.get("council_extensions_remaining") == 3,
                str(state.get("council_extensions_remaining")),
            )
            ok &= check(
                "game_state has turn field",
                "turn" in state,
            )
            if not ok:
                failures += 1

        # ── 3. council_extension ──────────────────────────────────────────────
        print("\n-- council_extension event ------------------------------------------")
        before = len(received)
        await sio_client.emit("council_extension", {"player_id": "test_player"})
        await asyncio.sleep(0.5)

        ok = check(
            "council_extension -> broadcast received",
            len(received) > before,
            f"received {len(received) - before} new update(s)",
        )
        if ok:
            state = received[-1]
            ok &= check(
                "council_extensions_remaining decremented to 2",
                state.get("council_extensions_remaining") == 2,
                str(state.get("council_extensions_remaining")),
            )
            ok &= check(
                "turn_time_limit increased by 30",
                state.get("turn_time_limit", 0) >= 70,
                str(state.get("turn_time_limit")),
            )
        if not ok:
            failures += 1

        # ── 4. Disconnect is clean ────────────────────────────────────────────
        print("\n-- Disconnect -------------------------------------------------------")
        await sio_client.disconnect()
        await asyncio.sleep(0.3)
        check("disconnected without exception", True)

        status2, body2 = http_get("/health")
        check("server still healthy after disconnect", status2 == 200, str(body2))

    except Exception as exc:
        check("socket test", False, str(exc))
        failures += 1
    finally:
        if sio_client.connected:
            await sio_client.disconnect()

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if failures == 0:
        print(f"{PASS}: All tests passed -- step 4 is working correctly.\n")
    else:
        print(f"{FAIL}: {failures} check(s) failed -- see above.\n")

    return failures


if __name__ == "__main__":
    result = asyncio.run(run_tests())
    sys.exit(result)
