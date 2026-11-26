"""Identity domain objects and rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    principal_id: str
    role: str
    password_hash: str
    active: bool = True
    permissions: frozenset[str] = frozenset()
