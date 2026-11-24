from dataclasses import dataclass, field
from enum import StrEnum
from threading import Lock


class IngestionStage(StrEnum):
    UPLOADED = "UPLOADED"
    CONVERTING = "CONVERTING"
    CONVERTED = "CONVERTED"
    CHUNKED = "CHUNKED"
    VECTOR_STORED = "VECTOR_STORED"
    FAILED = "FAILED"


@dataclass
class IngestionRecord:
    document_id: int
    idempotency_key: str
    stage: IngestionStage = IngestionStage.UPLOADED
    active_segment_ids: set[str] = field(default_factory=set)
    error: str | None = None
    attempts: int = 0


class IngestionStateStore:
    """Durable-state-shaped store used by task handlers and deterministic tests."""

    def __init__(self) -> None:
        self._records: dict[str, IngestionRecord] = {}
        self._lock = Lock()

    def start(self, document_id: int, idempotency_key: str) -> IngestionRecord:
        with self._lock:
            return self._records.setdefault(idempotency_key, IngestionRecord(document_id, idempotency_key))

    def transition(self, idempotency_key: str, stage: IngestionStage, *, error: str | None = None) -> IngestionRecord:
        with self._lock:
            record = self._records[idempotency_key]
            record.stage = stage
            record.error = error
            if error:
                record.attempts += 1
            return record

    def add_segments(self, idempotency_key: str, segment_ids: set[str]) -> IngestionRecord:
        with self._lock:
            record = self._records[idempotency_key]
            record.active_segment_ids.update(segment_ids)
            return record

    def get(self, idempotency_key: str) -> IngestionRecord | None:
        return self._records.get(idempotency_key)

    def compensate(self, idempotency_key: str) -> IngestionRecord:
        with self._lock:
            record = self._records[idempotency_key]
            record.stage = IngestionStage.FAILED
            record.error = "compensation_required"
            return record
