# Tasks

## 1. Contract and Data Inventory

- [x] 1.1 Record current REST routes, request/response models, auth behavior, and SSE markers in a versioned API contract; verify the contract covers chat, documents, segments, conversations, login, and QA-cache endpoints.
- [ ] 1.2 Inventory MySQL tables, indexes, Elasticsearch mappings and counts, Redis uses, MinIO object keys, prompt files, parser services, and scheduled jobs; verify the inventory is redacted and includes representative test fixtures.
- [x] 1.3 Build a golden RAG evaluation set from representative existing tests and prompts, including routes, citations, ACL cases, cards, and failure cases; verify fixtures contain no production secrets or private data.

## 2. Python Service Foundation

- [x] 2.1 Scaffold the `KonwHub` monorepo using the documented direct package layout: backend code under `backend/konwhub/` with no `/src` directory, plus separate frontend, migrations, tests, docs, deploy, and scripts; configure the import package as `konwhub`, pinned dependencies, settings validation, structured logging, and API/worker entry points; verify package installation/imports, layer-boundary checks, startup diagnostics, and health endpoints in CI.
- [x] 2.2 Add FastAPI routers, Pydantic schemas, SQLAlchemy repositories, and Alembic baseline inspection for existing MySQL tables; verify schema inspection does not mutate the existing database.
- [x] 2.3 Implement Redis-backed opaque sessions, customer/staff login dependencies, role checks, ownership checks, and secret redaction; verify authentication, expiry, logout, cross-user denial, and missing-secret tests.
- [ ] 2.4 Define application ports and health checks for chat, embeddings, reranking, Elasticsearch, Neo4j, read-only SQL, MinIO, and DingTalk; verify provider configuration can be tested with fakes and exposes no secret values.

## 3. Document Ingestion and Administration

- [ ] 3.1 Port document, version, segment, and table-metadata persistence while preserving IDs and lifecycle fields; verify repository tests against a disposable MySQL-compatible database and compare rows with the Java schema.
- [x] 3.2 Implement file parsing adapters and smart, Markdown parent/child, sibling, length, regex/separator, and Excel/CSV splitters; verify fixtures preserve row integrity, order, and parent/sibling metadata.
- [ ] 3.3 Add Celery ingestion stages with idempotency, durable status transitions, retries, locking, and compensation; verify duplicate delivery and worker restart do not create duplicate active segments or vectors.
- [ ] 3.4 Implement Elasticsearch indexing, ACL/version/expiry metadata filters, segment edit/delete synchronization, and version activation behavior; verify retrieval excludes inaccessible, inactive, and expired content.
- [ ] 3.5 Implement document, version, table preview, and segment administration APIs and document the endpoints; verify pagination, ordering, upload limits, permissions, and lifecycle state responses.

## 4. Retrieval and Streaming Chat

- [ ] 4.1 Port intent recognition, query transformation, prompt routing, and structured output validation as ordinary Python application functions using LangChain model and parser components; verify golden-set route and transformation results with mocked model responses.
- [ ] 4.2 Implement vector/full-text/hybrid search, parent-child expansion, reciprocal-rank fusion, BGE reranking, and SQL/graph retrieval adapters; verify ranking, citation metadata, read-only query validation, limits, and configured fallbacks.
- [ ] 4.3 Implement deterministic Python chat orchestration, conversation persistence, ownership-scoped history, answer feedback, and typed SSE events; verify stage ordering, explicit route branches, completion IDs, Markdown preservation, partial failures, and citation serialization without LangGraph.
- [x] 4.4 Add the legacy SSE compatibility encoder and API contract documentation; verify existing marker clients can consume progress, references, cards, warnings, and done events during transition.
- [ ] 4.5 Compare Python and Java outputs on the golden evaluation set and publish a retrieval parity report; verify material differences in route, source set, ranking, ACL, citations, and latency are reviewed before cutover.

## 5. Authentication and Frontend

- [x] 5.1 Create the Vue 3, TypeScript, Vite application with router, generated/typed API clients, session handling, and reusable SSE client; verify lint, type-check, and production build in CI.
- [ ] 5.2 Implement login, chat history, streaming answer, citations, cards, feedback, and conversation actions; verify browser-level flows against the Python API, including expired sessions and stream errors.
- [ ] 5.3 Implement document upload, split configuration, document/version management, segment preview/edit, and tabular data preview; verify role restrictions, upload progress, and processing-state refresh.
- [ ] 5.4 Implement QA-cache reviewer pages and staff workflows; verify reviewer-only access, approval/rejection/disable actions, validation errors, and visible publication status.
- [x] 5.5 Publish frontend setup, environment, build, and API/SSE documentation; verify a clean checkout can configure, build, and run the UI against a local backend.

## 6. QA Cache and External Integrations

- [ ] 6.1 Port QA-cache curation, deduplication, review, publication, retrieval, expiration, dependency invalidation, and maintenance tasks; verify lifecycle tests cover failed indexing, stale sources, expiration, and idempotent retries.
- [ ] 6.2 Port DingTalk callback signature validation and private/group message delivery through the shared chat workflow; verify invalid signatures are rejected and delivery failures are observable and retryable.
- [ ] 6.3 Add integration tests for MySQL, Elasticsearch, Redis, MinIO, Neo4j, the configured model provider, and DingTalk sandbox/fakes; verify health reports distinguish required failures from optional degraded services.

## 7. Cutover and Recovery

- [ ] 7.1 Add backup, pause/drain, pending-job inspection, single-writer switch, smoke-test, and rollback runbooks; verify every command and recovery prerequisite is exercised in staging.
- [ ] 7.2 Run read-only data and index compatibility checks against a production-like snapshot; verify document/version/chunk counts, IDs, ACL metadata, embeddings, object references, and sampled citations match.
- [ ] 7.3 Deploy Python in shadow mode and compare representative requests, stream events, retrieval quality, processing states, and queue recovery; verify parity thresholds and sign-off evidence are recorded.
- [ ] 7.4 Switch API and worker ownership to Python in staging, rehearse rollback after writes, then verify auth, ingestion, chat, cache jobs, DingTalk, monitoring, and restore procedures end to end.
- [ ] 7.5 Remove Java/static-page compatibility only after the agreed observation window; verify no traffic depends on legacy routes and archived data remains readable.
