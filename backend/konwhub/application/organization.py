from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from konwhub.core.security import hash_password
from konwhub.infrastructure.persistence.models import Department, Role, RoleDepartment, User, UserRole
from konwhub.infrastructure.persistence.repositories import OrganizationRepository


class OrganizationService:
    """Use-case boundary for departments, roles, users and their bindings."""
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def _session(self):
        if self.session_factory is None:
            raise RuntimeError("Database is not configured")
        return self.session_factory()

    def register_user(self, payload):
        with self._session() as session:
            user = User(employee_no=payload.employee_no or f"EMP{uuid4().hex[:12].upper()}", username=payload.username, real_name=payload.real_name, password=hash_password(payload.password), department_id=payload.department_id, status=1, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            session.add(user)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise ValueError("username or employee_no already exists") from error
            session.refresh(user)
            return user

    def create_department(self, payload):
        with self._session() as session:
            item = Department(parent_id=payload.parent_id, name=payload.name, path=payload.path or "/", sort_order=payload.sort_order, status=payload.status, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            session.add(item); session.commit(); session.refresh(item)
            if not payload.path:
                item.path = f"/{item.id}/" if not item.parent_id else f"/{item.parent_id}/{item.id}/"
                session.commit(); session.refresh(item)
            return item

    def create_role(self, payload):
        with self._session() as session:
            item = Role(code=payload.code, name=payload.name, description=payload.description, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            session.add(item)
            try: session.commit()
            except IntegrityError as error:
                session.rollback(); raise ValueError("role code already exists") from error
            session.refresh(item); return item

    def update_user(self, user_id, payload):
        with self._session() as session:
            item = OrganizationRepository(session).get_user(user_id)
            if not item or item.deleted_at is not None: return None
            for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
            item.updated_at = datetime.utcnow(); session.commit(); session.refresh(item); return item

    def delete_user(self, user_id):
        with self._session() as session:
            item = OrganizationRepository(session).get_user(user_id)
            if not item: return False
            item.deleted_at = datetime.utcnow(); item.status = 0; session.commit(); return True

    def update_department(self, item_id, payload):
        return self._update(Department, item_id, payload)

    def update_role(self, item_id, payload):
        return self._update(Role, item_id, payload)

    def delete_department(self, item_id):
        return self._delete(Department, item_id)

    def delete_role(self, item_id):
        return self._delete(Role, item_id)

    def _update(self, model, item_id, payload):
        with self._session() as session:
            item = session.get(model, item_id)
            if not item: return None
            for key, value in payload.model_dump(exclude_unset=True).items():
                if value is not None or key in {"parent_id", "description", "path"}: setattr(item, key, value)
            item.updated_at = datetime.utcnow(); session.commit(); session.refresh(item); return item

    def _delete(self, model, item_id):
        with self._session() as session:
            item = session.get(model, item_id)
            if not item: return False
            if model is Department:
                item.deleted_at = datetime.utcnow(); item.status = 0
            else:
                session.delete(item)
            session.commit(); return True

    def add_user_role(self, payload):
        with self._session() as session:
            item = UserRole(**payload.model_dump(), created_at=datetime.utcnow()); session.add(item)
            try: session.commit()
            except IntegrityError as error:
                session.rollback(); raise ValueError("user role binding already exists") from error
            return item

    def add_role_department(self, payload):
        with self._session() as session:
            item = RoleDepartment(**payload.model_dump(), created_at=datetime.utcnow()); session.add(item)
            try: session.commit()
            except IntegrityError as error:
                session.rollback(); raise ValueError("role department binding already exists") from error
            return item

    def list(self, kind, identifier=None):
        with self._session() as session:
            repo = OrganizationRepository(session)
            return getattr(repo, f"list_{kind}")(identifier) if identifier is not None else getattr(repo, f"list_{kind}")()
