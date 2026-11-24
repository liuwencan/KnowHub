from dataclasses import dataclass

from konwhub.core.security import hash_password, verify_password


@dataclass(frozen=True)
class Account:
    principal_id: str
    role: str
    password_hash: str
    active: bool = True
    permissions: frozenset[str] = frozenset()


class AccountDirectory:
    def __init__(self, accounts: list[Account] | None = None) -> None:
        self._accounts = {account.principal_id: account for account in accounts or []}

    def add(self, principal_id: str, password: str, role: str = "customer", permissions: set[str] | None = None) -> None:
        self._accounts[principal_id] = Account(principal_id, role, hash_password(password), True, frozenset(permissions or set()))

    def authenticate(self, principal_id: str, password: str, role: str) -> Account | None:
        account = self._accounts.get(principal_id)
        if not account or account.role != role or not account.active or not verify_password(password, account.password_hash):
            return None
        return account

    def deactivate(self, principal_id: str) -> None:
        account = self._accounts[principal_id]
        self._accounts[principal_id] = Account(account.principal_id, account.role, account.password_hash, False, account.permissions)


class SqlAccountAuthenticator:
    """Read-only adapter for the legacy user_info and staff_info accounts."""

    def __init__(self, engine) -> None:
        self.engine = engine

    def authenticate(self, principal_id: str, password: str, role: str) -> Account | None:
        from sqlalchemy import text

        if role == "customer":
            statement = text("SELECT id, phone, password, status FROM user_info WHERE phone = :principal_id LIMIT 1")
        elif role == "staff":
            statement = text("SELECT emp_id, password, status FROM staff_info WHERE emp_id = :principal_id LIMIT 1")
        else:
            return None
        with self.engine.connect() as connection:
            row = connection.execute(statement, {"principal_id": principal_id}).mappings().first()
        if not row or not row.get("password"):
            return None
        active = row.get("status") == ("ACTIVE" if role == "customer" else "ON_JOB")
        if not active:
            return None
        stored = str(row["password"])
        valid = verify_password(password, stored) if stored.startswith("sha256$") else password == stored
        if not valid:
            return None
        identity = str(row["id"]) if role == "customer" else f"staff_{row['emp_id']}"
        permissions = frozenset({"reviewer"}) if role == "staff" else frozenset()
        return Account(identity, role, "[REDACTED]", active, permissions)
