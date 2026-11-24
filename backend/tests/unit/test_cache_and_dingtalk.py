from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac

from konwhub.application.qa_cache import CacheStatus, QaCacheService
from konwhub.infrastructure.integrations.dingtalk import verify_callback


def test_cache_requires_review_and_invalidates_dependencies() -> None:
    service = QaCacheService()
    entry = service.curate("same question", "answer", [{"document_id": 1, "version_id": 1}], 3)
    assert entry and entry.status == CacheStatus.PENDING
    service.approve(entry.entry_id, "reviewer", [{"document_id": 1, "version_id": 1}])
    service.publish(entry.entry_id, lambda _: None)
    assert service.retrieve("same question", .9, lambda dependencies: True) is entry
    assert service.retrieve("same question", .9, lambda dependencies: False) is None
    service.disable(entry.entry_id, "KNOWLEDGE_CHANGED")
    service.cleanup_vectors(entry.entry_id, lambda _: None)
    assert entry.vector_deleted is True


def test_callback_signature_rejects_stale_or_invalid_message() -> None:
    timestamp = str(1_700_000_000_000)
    signature = base64.b64encode(hmac.new(b"secret", f"{timestamp}\nsecret".encode(), hashlib.sha256).digest()).decode()
    assert verify_callback(timestamp, signature, "secret", now=1_700_000_000)
    assert verify_callback(timestamp, signature, "secret", now=1_800_000_000) is False
    assert verify_callback(timestamp, "invalid", "secret", now=1_700_000_000) is False
