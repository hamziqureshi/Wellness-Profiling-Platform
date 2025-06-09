from fastapi import WebSocket
import logging
import asyncio
import time

from llm.make_prompt import extract_user_profile_field
from profiling import state as ProfileState
from profiling.schema import UserProfile
from sockets import events as EVENTS
from llm.question_generator import generate_followup_question


from common import constants as CONSTS

logger = logging.getLogger(__name__)


async def ping_websocket(websocket):
    while True:
        try:
            await websocket.send_json({"event": "PING", "timestamp": time.time()})
            logging.debug("Sent PING to client.")
            await asyncio.sleep(30)
        except Exception as e:
            logging.info(f"Stopped PINGs — likely disconnected: {e}")
            break

async def handle_init_profile(websocket: WebSocket, session_id: str):
    logger.info(f"Initializing user session for session_id: {session_id}")

    
    ProfileState.init_user_session(session_id)
    logger.debug(f"Session initialized in state store for session_id: {session_id}")
    
    _, unset_fields = ProfileState.get_set_and_unset_fields(session_id)
    unset_field_descriptions = [CONSTS.FIELD_METADATA[f] for f in unset_fields if f in CONSTS.FIELD_METADATA]

    message = generate_followup_question(remaining_fields=unset_field_descriptions)
    await websocket.send_json({
        "event": EVENTS.ASSISTANT_QUESTION,
        "message": message
    })
    ProfileState.set_last_question(session_id, message)
    logger.info(f"Sent initial assistant question to session_id: {session_id}")

async def handle_user_answer(websocket: WebSocket, session_id: str, answer: str):
    logger.info(f"Handling user answer for session_id: {session_id}, answer: {answer}")
    asyncio.create_task(ping_websocket(websocket))
    

    session = ProfileState.get_session(session_id)
    if not session:
        logger.warning(f"Session not found for session_id: {session_id}")
        await websocket.send_json({
            "event": "ERROR",
            "message": "Session not found."
        })
        return

    logger.debug(f"Current session state: {session}")

    # Get set and unset fields
    _, unset_fields = ProfileState.get_set_and_unset_fields(session_id)

    for field in unset_fields:
        last_question = ProfileState.get_last_question(session_id)
        value = extract_user_profile_field(field=field, question=last_question, user_text=answer)
        if value and value.strip().lower() not in {"none", "not mentioned"}:
            ProfileState.update_profile(session_id, {field: value})

    ProfileState.increment_question_count(session_id)
    logger.debug(f"Incremented question count for session_id: {session_id}")

    # Re-fetch after update
    session = ProfileState.get_session(session_id)

    # Get unset fields again
    _, unset_fields = ProfileState.get_set_and_unset_fields(session_id)

    if not unset_fields or session["question_count"] >= CONSTS.MAX_QUESTIONS:
        logger.info(f"Profile complete for session_id: {session_id}")
        await websocket.send_json({
            "event": EVENTS.PROFILE_COMPLETE,
            "message": "Thanks! Your profile is complete.",
            "profile": session["profile"].dict()
        })
        return

    try:
        # Prepare metadata for unset fields only
        _, unset_fields = ProfileState.get_set_and_unset_fields(session_id)
        unset_field_descriptions = [CONSTS.FIELD_METADATA[f] for f in unset_fields if f in CONSTS.FIELD_METADATA]

        next_question = generate_followup_question(last_question, answer, unset_field_descriptions)
        ProfileState.set_last_question(session_id, next_question)
        logger.info(f"Generated follow-up question for session_id: {session_id}")
    except Exception as e:
        logger.exception(f"Failed to generate follow-up question for session_id: {session_id}")
        next_question = "Sorry, I couldn't come up with a next question. Can you clarify more?"

    await websocket.send_json({
        "event": EVENTS.ASSISTANT_QUESTION,
        "message": next_question
    })
    logger.debug(f"Sent assistant question to session_id: {session_id}")