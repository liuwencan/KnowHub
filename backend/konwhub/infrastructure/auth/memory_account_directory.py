from konwhub.core.security import hash_password, verify_password
from konwhub.domain.identity import Account


class AccountDirectory:
    """In-memory account adapter for local development and tests."""

    def __init__(self, accounts: list[Account] | None = None) -> None:
        self._accounts = {account.principal_id: account for account in accounts or []}

    def add(self, principal_id: str, password: str, role: str = "customer", permissions: set[str] | None = None) -> None:
        self._accounts[principal_id] = Account(principal_id, role, hash_password(password), True, frozenset(permissions or set()))

    def authenticate(self, principal_id: str, password: str, role: str | None = None) -> Account | None:
        account = self._accounts.get(principal_id)
        if not account or (role and account.role != role) or not account.active or not verify_password(password, account.password_hash):
            return None
        return account

    def deactivate(self, principal_id: str) -> None:
        account = self._accounts[principal_id]
        self._accounts[principal_id] = Account(account.principal_id, account.role, account.password_hash, False, account.permissions)
