from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


IdType = BigInteger().with_variant(Integer, "sqlite")


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(128))
    path: Mapped[str] = mapped_column(String(512), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    employee_no: Mapped[str] = mapped_column(String(64), unique=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    real_name: Mapped[str] = mapped_column(String(128))
    password: Mapped[str] = mapped_column(String(255))
    department_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", "department_id", name="uk_user_roles_scope"),)
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role_id: Mapped[int] = mapped_column(BigInteger, index=True)
    department_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class RoleDepartment(Base):
    __tablename__ = "role_departments"
    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    department_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_document"
    doc_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    doc_title: Mapped[str] = mapped_column(String(1024))
    expire_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(String(512))
    knowledge_base_type: Mapped[str | None] = mapped_column(String(32))
    extension: Mapped[str | None] = mapped_column(Text)
    accessible_by: Mapped[str | None] = mapped_column(String(1024))
    current_version_id: Mapped[int | None] = mapped_column(BigInteger)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)


class KnowledgeDocumentVersion(Base):
    __tablename__ = "knowledge_document_version"
    version_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    doc_id: Mapped[int] = mapped_column(BigInteger)
    version: Mapped[str] = mapped_column(String(32))
    doc_url: Mapped[str | None] = mapped_column(String(2048))
    converted_doc_url: Mapped[str | None] = mapped_column(String(2048))
    content_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    upload_user: Mapped[str | None] = mapped_column(String(255))
    changelog: Mapped[str | None] = mapped_column(String(1024))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)


class KnowledgeSegment(Base):
    __tablename__ = "knowledge_segment"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    chunk_id: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column("metadata", String(2048))
    document_id: Mapped[int] = mapped_column(BigInteger)
    document_version: Mapped[int | None] = mapped_column(BigInteger)
    chunk_order: Mapped[int] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(255))
    embedding_id: Mapped[str | None] = mapped_column(String(255))
    skip_embedding: Mapped[int | None] = mapped_column(Integer)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)


class TableMeta(Base):
    __tablename__ = "table_meta"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    table_name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(String(512))
    create_sql: Mapped[str | None] = mapped_column(Text)
    columns_info: Mapped[str | None] = mapped_column(Text)
    version_id: Mapped[int | None] = mapped_column(BigInteger)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)


class ChatConversation(Base):
    __tablename__ = "chat_conversation"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="active")
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)


class ChatMessage(Base):
    __tablename__ = "chat_message"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_id: Mapped[str] = mapped_column(String(64), unique=True)
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    type: Mapped[str] = mapped_column(String(32))
    content: Mapped[str | None] = mapped_column(Text)
    transform_content: Mapped[str | None] = mapped_column(Text)
    rag_references: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column("metadata", Text)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    helpful: Mapped[bool | None] = mapped_column(Boolean)
    feedback_comment: Mapped[str | None] = mapped_column(String(1000))
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    lock_version: Mapped[int] = mapped_column(Integer, default=0)
