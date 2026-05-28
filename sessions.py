from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class UserSession:
    user_number: str
    request_id: str = ""
    last_message: str = ""
    language: str = "en"
    template_type: str = "agency"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


SESSIONS: dict[str, UserSession] = {}


def get_session(user_number: str) -> UserSession:
    return SESSIONS.get(user_number, UserSession(user_number=user_number))


def upsert_session(
    user_number: str,
    message: str,
    request_id: str = "",
    language: str = "",
    template_type: str = "",
) -> UserSession:
    session = SESSIONS.get(user_number, UserSession(user_number=user_number))
    session.last_message = message
    session.request_id = request_id or session.request_id
    if language:
        session.language = language
    if template_type:
        session.template_type = template_type
    session.updated_at = datetime.now(timezone.utc)
    SESSIONS[user_number] = session
    return session
