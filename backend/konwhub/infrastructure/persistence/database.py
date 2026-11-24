from collections.abc import Iterator

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine


def make_engine(database_url: str | None) -> Engine | None:
    return create_engine(database_url, pool_pre_ping=True) if database_url else None


def inspect_tables(engine: Engine) -> list[str]:
    """Read table names only; this function never creates or alters schema."""
    return sorted(inspect(engine).get_table_names())


def readonly_connection(engine: Engine) -> Iterator[object]:
    with engine.connect() as connection:
        yield connection
