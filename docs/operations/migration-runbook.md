# KonwHub Migration Runbook

This runbook is a staging checklist. Production execution requires an approved backup, named operator, and a tested rollback target.

## Before switching ownership

1. Record the current Java API, worker, queue, and scheduled-job versions.
2. Take consistent backups of MySQL, Elasticsearch indexes, Redis session/cache state, and MinIO objects. Record backup IDs and restore commands.
3. Pause document writes and QA-cache maintenance. Drain Celery/legacy jobs and record pending IDs.
4. Run `GET /api/v1/health/ready`, a login smoke test, a document metadata read, and a chat stream smoke test.
5. Confirm exactly one writer owns document lifecycle and QA-cache state.

## Switch and observe

1. Route staging API traffic to `konwhub-api` and start one worker deployment.
2. Monitor required dependency health, queue lag, ingestion failures, stream completion rate, auth denials, retrieval citations, and DingTalk delivery retries.
3. Compare the shadow/parity report with the thresholds approved for the release.

## Rollback

1. Stop Python writers and workers, preserve logs and pending-job IDs, and route API traffic back to Java.
2. Reconcile Python writes against the recorded snapshot before resuming Java jobs.
3. Restore only the affected store from the backup when reconciliation cannot prove safety.
4. Re-run auth, ingestion, chat, cache, DingTalk, health, and restore smoke tests before reopening writes.
