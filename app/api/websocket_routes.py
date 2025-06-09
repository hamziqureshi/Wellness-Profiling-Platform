from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sockets import handlers as WSHandlers
from sockets import events as EVENTS
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.websocket("/ws/profile/{session_id}")
async def profile_websocket(websocket: WebSocket, session_id: str):
    logger.info(f"New websocket connection attempt for session: {session_id}")
    
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for session: {session_id}")

    try:
        while True:
            data = await websocket.receive_json()
            logger.debug(f"Received data from session {session_id}: {data}")

            event = data.get("event")
            message = data.get("message", "")

            if event == EVENTS.INIT_PROFILE:
                logger.info(f"Handling INIT_PROFILE for session: {session_id}")
                await WSHandlers.handle_init_profile(websocket, session_id)

            elif event == EVENTS.USER_ANSWER:
                logger.info(f"Handling USER_ANSWER for session: {session_id} with message: {message}")
                await WSHandlers.handle_user_answer(websocket, session_id, message)

            else:
                logger.warning(f"Invalid event type received from session {session_id}: {event}")
                await websocket.send_json({
                    "event": "ERROR",
                    "message": "Invalid event type."
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")

    except Exception as e:
        logger.exception(f"Unexpected error in websocket session {session_id}: {e}")
        await websocket.send_json({
            "event": "ERROR",
            "message": "Internal server error."
        })