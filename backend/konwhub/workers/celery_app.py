from celery import Celery

from konwhub.core.settings import get_settings
from konwhub.ingestion.service import IngestionStateStore, IngestionStage


broker = get_settings().redis_url or "redis://localhost:6379/0"
celery_app = Celery("konwhub", broker=broker, backend=broker)
celery_app.conf.update(task_acks_late=True, task_reject_on_worker_lost=True)
state_store = IngestionStateStore()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_ingestion(self, document_id: int, idempotency_key: str) -> dict[str, object]:
    record = state_store.start(document_id, idempotency_key)
    if record.stage == IngestionStage.VECTOR_STORED:
        return {"document_id": document_id, "idempotency_key": idempotency_key, "status": "already-complete"}
    state_store.transition(idempotency_key, IngestionStage.CONVERTING)
    state_store.transition(idempotency_key, IngestionStage.CONVERTED)
    state_store.transition(idempotency_key, IngestionStage.CHUNKED)
    state_store.transition(idempotency_key, IngestionStage.VECTOR_STORED)
    return {"document_id": document_id, "idempotency_key": idempotency_key, "status": record.stage.value}


def main() -> None:
    celery_app.worker_main(["worker", "--loglevel=INFO"])
