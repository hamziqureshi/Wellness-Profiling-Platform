import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

FAST_API_PORT = os.getenv("FAST_API_PORT", "3000")

BASE_WS_URL = f"ws://localhost:{FAST_API_PORT}/ws/profile/test-session"

async def handle_incoming(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            event = data.get("event")
            message_text = data.get("message")

            if event == "PING":
                # print(f"[↔] Received PING at {data.get('timestamp')}")
                continue

            if message_text:
                print(f"[←] {event}: {message_text}")

            if event == "PROFILE_COMPLETE":
                print("[✓] Profile collection complete.")
                print("[📄] Final Profile:", json.dumps(data.get("profile", {}), indent=2))
                return

            # Only prompt user for answers when there's a message (e.g., assistant questions)
            if event == "ASSISTANT_QUESTION" and message_text:
                user_input = input("Your answer: ")
                await websocket.send(json.dumps({
                    "event": "USER_ANSWER",
                    "message": user_input
                }))
            else:
                print(f"[ℹ] Skipped event: {event}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"[x] WebSocket closed: {e.code} - {e.reason}")

async def test_websocket():
    async with websockets.connect(BASE_WS_URL, ping_interval=None, ping_timeout=None) as websocket:
        # Send INIT_PROFILE
        await websocket.send(json.dumps({
            "event": "INIT_PROFILE",
            "message": ""
        }))
        print("[→] INIT_PROFILE sent")

        await handle_incoming(websocket)

if __name__ == "__main__":
    asyncio.run(test_websocket())