import logging
from profiling.schema import UserProfile

# Setup logger
logger = logging.getLogger(__name__)

# In-memory session state
profile_sessions = {}


def get_set_and_unset_fields(session_id: str):
    session = get_session(session_id)
    if not session:
        logger.warning(f"No session found for session_id: {session_id}")
        return [], []

    profile = session["profile"]
    set_fields = []
    unset_fields = []

    for field_name, value in profile.dict().items():
        if value is not None and str(value).strip().lower() not in {"", "none", "not mentioned"}:
            set_fields.append(field_name)
        else:
            unset_fields.append(field_name)

    logger.info(f"Set fields for {session_id}: {set_fields}")
    logger.info(f"Unset fields for {session_id}: {unset_fields}")
    return set_fields, unset_fields

def init_user_session(session_id: str):
    logger.info(f"Initializing session for session_id: {session_id}")
    profile_sessions[session_id] = {
        "profile": UserProfile(),
        "question_count": 0
    }
    logger.debug(f"Session state after initialization: {profile_sessions[session_id]}")

def get_session(session_id: str):
    session = profile_sessions.get(session_id)
    if session:
        logger.debug(f"Retrieved session for session_id: {session_id} -> {session}")
    else:
        logger.warning(f"Attempted to retrieve nonexistent session for session_id: {session_id}")
    return session

def update_profile(session_id: str, data: dict):
    session = profile_sessions.get(session_id)
    if not session:
        logger.warning(f"Attempted to update profile for nonexistent session: {session_id}")
        return None
    old_profile = session["profile"]
    session["profile"] = old_profile.copy(update=data)
    logger.info(f"Updated profile for session_id: {session_id} with data: {data}")
    logger.info(f"New Profile: {session['profile'].dict()}")
    return session["profile"]

def increment_question_count(session_id: str):
    if session_id in profile_sessions:
        profile_sessions[session_id]["question_count"] += 1
        logger.info(f"Incremented question count for session_id: {session_id}")
        logger.debug(f"New question count: {profile_sessions[session_id]['question_count']}")
    else:
        logger.warning(f"Attempted to increment question count for nonexistent session: {session_id}")

def set_last_question(session_id: str, question: str):
    session = get_session(session_id)
    if session:
        session["last_question"] = question
        logger.debug(f"Set last question for session_id {session_id}: {question}")
    else:
        logger.warning(f"Tried to set last question for nonexistent session: {session_id}")


def get_last_question(session_id: str):
    session = get_session(session_id)
    if session:
        return session.get("last_question")
    logger.warning(f"Tried to get last question for nonexistent session: {session_id}")
    return None