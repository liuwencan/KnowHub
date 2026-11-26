from collections.abc import Iterator

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def make_engine(database_url: str | None) -> Engine | None:
    return create_engine(database_url, pool_pre_ping=True) if database_url else None


def make_session_factory(engine: Engine | None):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False) if engine else None


def session_scope(factory) -> Session:
    if factory is None:
        raise RuntimeError("Database is not configured")
    return factory()


def inspect_tables(engine: Engine) -> list[str]:
    """Read table names only; this function never creates or alters schema."""
    return sorted(inspect(engine).get_table_names())


def readonly_connection(engine: Engine) -> Iterator[object]:
    with engine.connect() as connection:
        yield connection
