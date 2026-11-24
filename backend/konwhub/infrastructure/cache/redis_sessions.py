import json
from datetime import datetime, timezone

from typing import Any

from konwhub.infrastructure.cache.sessions import Session


class RedisSessionStore:
    """Opaque session implementation for deployments with Redis configured."""

    def __init__(self, client: Any, ttl_seconds: int = 3600, prefix: str = "konwhub:session:") -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix

    def create(self, principal_id: str, role: str, permissions: set[str] | None = None) -> Session:
        from konwhub.core.security import new_session_token

        token = new_session_token()
        expires_at = datetime.now(timezone.utc).timestamp() + self.ttl_seconds
        payload = {"principal_id": principal_id, "role": role, "permissions": sorted(permissions or set()), "expires_at": expires_at}
        self.client.setex(self.prefix + token, self.ttl_seconds, json.dumps(payload))
        return Session(token, principal_id, role, frozenset(payload["permissions"]), datetime.fromtimestamp(expires_at, timezone.utc))

    def get(self, token: str | None) -> Session | None:
        if not token:
            return None
        raw = self.client.get(self.prefix + token)
        if not raw:
            return None
        payload = json.loads(raw)
        return Session(token, payload["principal_id"], payload["role"], frozenset(payload["permissions"]), datetime.fromtimestamp(payload["expires_at"], timezone.utc))

    def delete(self, token: str | None) -> None:
        if token:
            self.client.delete(self.prefix + token)
