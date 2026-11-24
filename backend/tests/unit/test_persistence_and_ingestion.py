from sqlalchemy import create_engine, inspect

from konwhub.infrastructure.persistence.models import Base
from konwhub.infrastructure.persistence.database import inspect_tables
from konwhub.ingestion.service import IngestionStateStore, IngestionStage


def test_sqlalchemy_models_inspect_without_mutation() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    assert "knowledge_document" in inspect_tables(engine)
    assert inspect(engine).get_table_names()


def test_duplicate_ingestion_is_idempotent() -> None:
    store = IngestionStateStore()
    first = store.start(10, "key")
    store.add_segments("key", {"segment-1"})
    store.transition("key", IngestionStage.VECTOR_STORED)
    second = store.start(10, "key")
    assert first is second
    assert second.active_segment_ids == {"segment-1"}
    assert second.stage == IngestionStage.VECTOR_STORED
