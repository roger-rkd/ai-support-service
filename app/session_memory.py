"""Short-lived in-memory chat session state."""

from typing import Optional
from collections import defaultdict


MAX_SESSION_MESSAGES = 20
SESSION_STATE = defaultdict(
    lambda: {
        "messages": [],
        "pending_postcode_for_gp": False,
    }
)


def get_session_state(session_id: Optional[str]) -> Optional[dict]:
    """Return per-session in-memory state when a session id is available."""
    if not session_id:
        return None
    return SESSION_STATE[session_id]


def append_session_message(session_state: Optional[dict], role: str, content: str) -> None:
    """Store a bounded list of recent messages for the current browser session."""
    if session_state is None:
        return
    session_state["messages"].append({"role": role, "content": content})
    if len(session_state["messages"]) > MAX_SESSION_MESSAGES:
        session_state["messages"] = session_state["messages"][-MAX_SESSION_MESSAGES:]
