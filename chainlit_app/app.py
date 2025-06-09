import json
import asyncio
import websockets
import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

FAST_API_PORT = os.getenv("FAST_API_PORT")

BASE_WS_URL = f"ws://chatbot-apis:{FAST_API_PORT}/ws/profile/test-session"


async def handle_incoming(websocket):
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            event = data.get("event")
            message_text = data.get("message")

            # Handle heartbeat pings from the server
            if event == "PING":
                continue

            # When profile collection is complete
            if event == "PROFILE_COMPLETE":
                await cl.Message(
                    content=f"[✓] Profile collection complete.\n\n[📄] Final Profile:\n```json\n{json.dumps(data.get('profile', {}), indent=2)}\n```"
                ).send()
                break

            # When the assistant is asking the user a question
            if event == "ASSISTANT_QUESTION" and message_text:
                try:
                    # Ask user with a timeout (graceful fallback if they take too long)
                    user_response = await cl.AskUserMessage(
                        content=message_text,
                        timeout=60  # Adjust this as needed
                    ).send()

                    if user_response and user_response.get("output"):
                        await websocket.send(json.dumps({
                            "event": "USER_ANSWER",
                            "message": user_response["output"]
                        }))
                    else:
                        await cl.Message(content="⏳ You didn’t respond in time. Please try again.").send()
                        # Optionally: Ask the same question again
                        # await cl.Message(content="Let’s try that again.").send()
                        # continue  # Uncomment to re-ask

                except Exception as timeout_err:
                    await cl.Message(content=f"[!] Timeout or input error: {str(timeout_err)}").send()

            # Other messages that are not direct questions
            elif message_text:
                await cl.Message(content=f"[←] {event}: {message_text}").send()
            else:
                await cl.Message(content=f"[ℹ] Skipped event: {event}").send()

        except websockets.exceptions.ConnectionClosed as e:
            await cl.Message(content=f"[x] WebSocket closed: {e.code} - {e.reason}").send()
            break
        except Exception as e:
            await cl.Message(content=f"[!] Unexpected error: {str(e)}").send()
            break

@cl.on_chat_start
async def start_chat():
    try:
        async with websockets.connect(BASE_WS_URL, ping_interval=None, ping_timeout=None) as websocket:
            # Initiate profile collection session
            await websocket.send(json.dumps({
                "event": "INIT_PROFILE",
                "message": ""
            }))
            await cl.Message(content="[→] INIT_PROFILE sent").send()

            await handle_incoming(websocket)

    except Exception as e:
        await cl.Message(content=f"[!] Failed to connect or handle session: {str(e)}").send()
