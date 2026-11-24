from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json


class CacheStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    DISABLED = "DISABLED"
    EXPIRED = "EXPIRED"


@dataclass
class QaCacheEntry:
    entry_id: str
    question: str
    answer: str
    sources: list[dict[str, object]]
    dependencies: list[dict[str, object]] | None = None
    status: CacheStatus = CacheStatus.PENDING
    reviewer: str | None = None
    review_note: str | None = None
    expires_at: datetime | None = None
    index_error: str | None = None
    vector_deleted: bool = False
    hits: int = 0
    disabled_reason: str | None = None
    activated_at: datetime | None = None


class QaCacheService:
    def __init__(self) -> None:
        self.entries: dict[str, QaCacheEntry] = {}

    @staticmethod
    def normalize(question: str) -> str:
        return " ".join(question.lower().split())

    def curate(self, question: str, answer: str, sources: list[dict[str, object]], frequency: int) -> QaCacheEntry | None:
        normalized = self.normalize(question)
        if frequency < 3 or any(self.normalize(item.question) == normalized and item.status not in {CacheStatus.REJECTED, CacheStatus.DISABLED, CacheStatus.EXPIRED} for item in self.entries.values()):
            return None
        entry_id = hashlib.sha1(normalized.encode()).hexdigest()
        entry = QaCacheEntry(entry_id, question, answer, sources)
        self.entries[entry_id] = entry
        return entry

    def approve(self, entry_id: str, reviewer: str, dependencies: list[dict[str, object]], expires_at: datetime | None = None) -> QaCacheEntry:
        entry = self.entries[entry_id]
        entry.status = CacheStatus.APPROVED
        entry.reviewer = reviewer
        entry.dependencies = json.loads(json.dumps(dependencies))
        entry.expires_at = expires_at
        entry.review_note = "approved"
        return entry

    def publish(self, entry_id: str, indexer) -> QaCacheEntry:
        entry = self.entries[entry_id]
        if entry.status != CacheStatus.APPROVED:
            raise ValueError("only approved entries can be published")
        try:
            indexer(entry)
        except Exception as error:
            entry.index_error = str(error)
            raise
        entry.status = CacheStatus.ACTIVE
        entry.index_error = None
        entry.activated_at = datetime.now(timezone.utc)
        return entry

    def retrieve(self, question: str, similarity: float, dependency_checker) -> QaCacheEntry | None:
        now = datetime.now(timezone.utc)
        for entry in self.entries.values():
            if entry.status != CacheStatus.ACTIVE or similarity < 0.8 or (entry.expires_at and entry.expires_at <= now) or not dependency_checker(entry.dependencies or []):
                continue
            entry.hits += 1
            return entry
        return None

    def disable(self, entry_id: str, reason: str) -> QaCacheEntry:
        entry = self.entries[entry_id]
        entry.status = CacheStatus.DISABLED if reason != "EXPIRED" else CacheStatus.EXPIRED
        entry.disabled_reason = reason
        entry.vector_deleted = False
        return entry

    def cleanup_vectors(self, entry_id: str, deleter) -> None:
        entry = self.entries[entry_id]
        if entry.status in {CacheStatus.DISABLED, CacheStatus.EXPIRED, CacheStatus.REJECTED} and not entry.vector_deleted:
            deleter(entry)
            entry.vector_deleted = True
