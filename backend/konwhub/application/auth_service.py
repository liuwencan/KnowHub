from dataclasses import dataclass
from typing import Protocol

from konwhub.core.settings import Settings
from konwhub.domain.identity import Account
from konwhub.infrastructure.cache.sessions import Session


class AccountAuthenticator(Protocol):
    def authenticate(self, principal_id: str, password: str, role: str) -> Account | None:
        ...


class SessionStore(Protocol):
    def create(self, principal_id: str, role: str, permissions: set[str] | None = None) -> Session:
        ...

    def get(self, token: str | None) -> Session | None:
        ...

    def delete(self, token: str | None) -> None:
        ...


@dataclass(frozen=True)
class AuthService:
    """Application service for identity verification and session lifecycle."""

    accounts: AccountAuthenticator
    sessions: SessionStore
    settings: Settings

    def login(self, principal_id: str, password: str, role: str | None = None) -> Session | None:
        account: Account | None = self.accounts.authenticate(principal_id, password, role)
        if account is None:
            return None
        return self.sessions.create(account.principal_id, account.role, set(account.permissions))

    def logout(self, token: str | None) -> None:
        self.sessions.delete(token)

    def is_logged_in(self, token: str | None) -> bool:
        return self.sessions.get(token) is not None

    @property
    def session_cookie_name(self) -> str:
        return self.settings.session_cookie_name

    @property
    def session_ttl_seconds(self) -> int:
        return self.settings.session_ttl_seconds
