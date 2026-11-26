from collections.abc import Sequence

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from konwhub.infrastructure.persistence.models import ChatConversation, ChatMessage, KnowledgeDocument, KnowledgeDocumentVersion, KnowledgeSegment, TableMeta, Department, Role, User, UserRole, RoleDepartment


class OrganizationRepository:
    """Persistence boundary for organization and authorization records."""
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_department(self, item_id: int): return self.session.get(Department, item_id)
    def list_departments(self): return self.session.scalars(select(Department).where(Department.deleted_at.is_(None)).order_by(Department.sort_order, Department.id)).all()
    def get_role(self, item_id: int): return self.session.get(Role, item_id)
    def list_roles(self): return self.session.scalars(select(Role).order_by(Role.id)).all()
    def get_user(self, item_id: int): return self.session.get(User, item_id)
    def find_user(self, identifier: str):
        return self.session.scalar(select(User).where(User.deleted_at.is_(None), or_(User.username == identifier, User.employee_no == identifier)))
    def list_users(self): return self.session.scalars(select(User).where(User.deleted_at.is_(None)).order_by(User.id)).all()
    def list_user_roles(self, user_id: int | None = None):
        statement = select(UserRole)
        if user_id is not None: statement = statement.where(UserRole.user_id == user_id)
        return self.session.scalars(statement.order_by(UserRole.id)).all()
    def list_role_departments(self, role_id: int | None = None):
        statement = select(RoleDepartment)
        if role_id is not None: statement = statement.where(RoleDepartment.role_id == role_id)
        return self.session.scalars(statement.order_by(RoleDepartment.role_id, RoleDepartment.department_id)).all()


class KnowledgeDocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, doc_id: int) -> KnowledgeDocument | None:
        return self.session.get(KnowledgeDocument, doc_id)

    def list_active(self, limit: int = 100, offset: int = 0) -> Sequence[KnowledgeDocument]:
        return self.session.scalars(select(KnowledgeDocument).where(KnowledgeDocument.deleted.is_(False)).offset(offset).limit(limit)).all()


class KnowledgeSegmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_document(self, document_id: int, limit: int = 100, offset: int = 0) -> Sequence[KnowledgeSegment]:
        statement = select(KnowledgeSegment).where(KnowledgeSegment.document_id == document_id, KnowledgeSegment.deleted.is_(False)).order_by(KnowledgeSegment.chunk_order).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


class DocumentLifecycleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_version(self, version_id: int) -> KnowledgeDocumentVersion | None:
        return self.session.get(KnowledgeDocumentVersion, version_id)

    def list_versions(self, doc_id: int) -> Sequence[KnowledgeDocumentVersion]:
        return self.session.scalars(select(KnowledgeDocumentVersion).where(KnowledgeDocumentVersion.doc_id == doc_id, KnowledgeDocumentVersion.deleted.is_(False)).order_by(KnowledgeDocumentVersion.version_id)).all()

    def get_table_meta(self, table_name: str) -> TableMeta | None:
        return self.session.scalar(select(TableMeta).where(TableMeta.table_name == table_name, TableMeta.deleted.is_(False)))


class ConversationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_owned(self, conversation_id: str, user_id: str) -> ChatConversation | None:
        return self.session.scalar(select(ChatConversation).where(ChatConversation.conversation_id == conversation_id, ChatConversation.user_id == user_id, ChatConversation.deleted.is_(False)))

    def list_messages(self, conversation_id: str, user_id: str) -> Sequence[ChatMessage]:
        if not self.get_owned(conversation_id, user_id):
            return []
        return self.session.scalars(select(ChatMessage).where(ChatMessage.conversation_id == conversation_id, ChatMessage.deleted.is_(False)).order_by(ChatMessage.id)).all()
