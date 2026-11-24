from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from konwhub.core.security import new_session_token


@dataclass(frozen=True)
class Session:
    token: str
    principal_id: str
    role: str
    permissions: frozenset[str]
    expires_at: datetime


class SessionStore:
    """Opaque session store with an in-memory adapter for tests and local startup."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self._sessions: dict[str, Session] = {}

    def create(self, principal_id: str, role: str, permissions: set[str] | None = None) -> Session:
        session = Session(new_session_token(), principal_id, role, frozenset(permissions or set()), datetime.now(timezone.utc) + self.ttl)
        self._sessions[session.token] = session
        return session

    def get(self, token: str | None) -> Session | None:
        if not token:
            return None
        session = self._sessions.get(token)
        if session and session.expires_at > datetime.now(timezone.utc):
            return session
        if session:
            self._sessions.pop(token, None)
        return None

    def delete(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)
