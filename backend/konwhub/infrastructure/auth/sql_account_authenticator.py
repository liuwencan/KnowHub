from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from konwhub.core.security import verify_password
from konwhub.domain.identity import Account
from konwhub.infrastructure.persistence.models import Role, User, UserRole


class SqlAccountAuthenticator:
    """SQL adapter for the departments/roles/users authorization model."""

    def __init__(self, engine: Engine, session_factory: sessionmaker | None = None) -> None:
        self.engine = engine
        self.session_factory = session_factory or sessionmaker(bind=engine, expire_on_commit=False)

    def authenticate(self, principal_id: str, password: str, role: str | None = None) -> Account | None:
        with self.session_factory() as session:
            user = session.scalar(select(User).where(User.deleted_at.is_(None), (User.username == principal_id) | (User.employee_no == principal_id)))
            if not user or user.status != 1 or not (verify_password(password, user.password) or password == user.password):
                return None
            role_codes = {row[0] for row in session.execute(select(Role.code).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)).all()}
            mapped_role = "staff" if role_codes.intersection({"admin", "employee", "staff", "manager"}) else "customer"
            if role == "staff" and mapped_role != "staff":
                return None
            return Account(str(user.id), mapped_role, "[REDACTED]", True, frozenset(role_codes | ({"staff"} if mapped_role == "staff" else set())))
