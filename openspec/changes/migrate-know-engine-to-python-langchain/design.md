# Design

## Context

See proposal.md for motivation and the five capability specs for behavior contracts. The Java service is a Spring Boot application using LangChain4j. It persists documents, versions, segments, conversations, messages, and QA-cache entries in MySQL; indexes text and vectors in Elasticsearch; uses Redis for sessions and caches/locks; stores files in MinIO; and optionally queries Neo4j and business tables. Its static frontend already contains six pages with authenticated workflows and custom SSE parsing. Existing prompt files and current API/SSE behavior are migration inputs.

## Goals / Non-Goals

**Goals:**
- Keep behavior and data traceability across a staged runtime replacement.
- Make model and storage integrations replaceable through narrow interfaces.
- Separate synchronous API work from retryable ingestion and maintenance work.
- Give chat, document administration, and review workflows a maintainable frontend with typed contracts.

**Non-Goals:**
- Replacing the current databases, object store, or DingTalk during this migration.
- Re-embedding all content solely to adopt a new framework; embedding dimensions and model identity must remain compatible with the existing index.
- Turning automotive-specific prompts, cards, and business tables into mandatory dependencies of a generic knowledge engine.

### KonwHub project layout

Use `KonwHub` as the new project/repository identity and `konwhub` as the lowercase Python import package. Use a direct package layout under `backend/`; do not create a top-level or backend `src/` directory.

```text
KonwHub/
├── backend/
│   ├── pyproject.toml
│   ├── konwhub/
│   │   ├── api/v1/              # HTTP routes, dependencies, SSE transport
│   │   ├── application/         # Use cases and deterministic orchestration
│   │   ├── domain/              # Entities, value objects, rules, ports
│   │   ├── infrastructure/      # Database and external provider adapters
│   │   │   ├── persistence/     # MySQL repositories
│   │   │   ├── search/          # Elasticsearch retrieval and indexing
│   │   │   ├── cache/           # Redis sessions, cache, locks
│   │   │   ├── storage/         # MinIO object storage
│   │   │   ├── graph/           # Neo4j adapter
│   │   │   ├── llm/             # LangChain model, prompt, parser adapters
│   │   │   └── integrations/    # DingTalk and other external services
│   │   ├── ingestion/           # Parsing, splitters, ingestion services
│   │   ├── rag/                 # Retrieval, context assembly, reranking
│   │   ├── workers/             # Celery task definitions
│   │   ├── schemas/             # Shared API request/response schemas
│   │   ├── core/                # Settings, logging, security, exceptions
│   │   └── prompts/             # Versioned prompt templates
│   ├── migrations/              # Alembic migrations
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── contract/
│       └── e2e/
├── frontend/                    # Vue 3 + TypeScript application
├── docs/                        # Architecture, API, operations, migration
├── deploy/                      # Container and environment deployment assets
└── scripts/                     # Local development and maintenance commands
```

Keep dependency direction explicit: `api` calls `application`; `application` depends on `domain` and its ports; `infrastructure` implements those ports. Domain code must not import FastAPI, LangChain, SQLAlchemy, or provider SDKs. Keep tests grouped by unit, integration, contract, and end-to-end scope, and keep database migrations, prompts, deployment assets, and documentation outside the Python package where shown. Avoid catch-all modules such as `common` or `utils`; place shared behavior under the owning layer or capability.

## Decisions

### Python service and workflow structure

Use FastAPI for versioned REST endpoints, authentication dependencies, upload handling, OpenAPI generation, and SSE responses. Keep route handlers thin: domain/application services own document, chat, identity, and cache behavior; SQLAlchemy 2 models/repositories own MySQL persistence; Pydantic schemas define external contracts. Orchestrate chat and RAG in ordinary Python application services using an explicit typed request/context object and a fixed sequence of functions: validate input, classify intent, transform the query when configured, select a route, retrieve, expand context, rerank, generate, persist, and emit events. Use explicit conditionals for known route branches and bounded concurrency only where independent retrieval calls benefit from it. LangChain supplies provider clients, prompts, output parsers, and retriever integrations behind application-owned ports; it does not own the control flow. Do not use LangGraph or expose LangChain model or document objects directly through the API. This matches the predominantly deterministic workflow, keeps control flow visible to Python maintainers, and makes each step straightforward to test without graph state or checkpoint machinery.

Use a separate Celery worker with Redis as broker for document conversion, chunking/indexing, QA-cache curation/publication, and compensation jobs. Persist each stage and idempotency key before acknowledging work; retries resume from the last durable stage. This replaces event-listener plus XXL-Job behavior with a Python worker model. Celery is chosen over running long work in FastAPI requests because uploads and vector writes need retry and recovery across process restarts.

### Provider and retrieval boundaries

Define application interfaces for chat, embeddings, reranking, vector/full-text retrieval, graph retrieval, read-only relational retrieval, file storage, and messaging. The first adapters target the current OpenAI-compatible Qwen endpoint, Elasticsearch, Neo4j, MySQL, MinIO, Redis, local BGE ONNX reranking, and DingTalk. Preserve current index names, metadata fields, vector dimensions, chunk IDs, and access/version filters unless an explicit migration is added. Keep the current remote MinerU PDF parsing endpoint behind a parser interface; use Python parsers for supported Word, Excel/CSV, Markdown, and text inputs where existing behavior can be matched.

Run Text2SQL through a dedicated read-only database identity, configured schema/table allowlists, SQL parsing/validation, row limits, and timeouts. Run Text2Cypher with read-only credentials, allowed labels/relationships, query limits, and timeouts. Generated queries are untrusted input; execution failure follows the configured fallback and never bypasses document authorization. These controls are part of the adapter boundary rather than prompts alone.

### Frontend choice

Use Vue 3, TypeScript, and Vite for a separately built SPA. The existing UI has six pages and stateful workflows: chat streams and renders progress/citations/cards, document pages manage uploads and versions, and QA-cache pages support reviewer decisions. Component state, routing, form validation, and typed API models justify a framework. Vue is the recommendation because its single-file components support incremental conversion from the current HTML/JavaScript pages with a relatively direct template-to-component path. React is a sound alternative when the implementation team already standardizes on React or needs its broader component ecosystem; this repository gives no such signal. Plain HTML remains appropriate for a tiny static tool, but would leave these workflows as hand-managed DOM and event state.

Publish a versioned OpenAPI contract and define a typed SSE event union for `progress`, `token`, `reference`, `card`, `warning`, `error`, and `done`. During cutover, a compatibility endpoint maps this event model to the current `[PROGRESS]`, `[REFERENCE]`, `[CARD]`, `[WARN]`, and `[DONE]` markers, including conversation IDs. The Vue client consumes the typed event contract; legacy marker encoding is temporary compatibility behavior.

### Authentication, persistence, and deployment settings

Keep customer and staff identity flows distinct, but represent sessions as opaque server-side tokens stored in Redis. Accept the existing `satoken` cookie/header during the compatibility period; never assume Sa-Token internals are a Python contract. Enforce ownership and document ACL filters in application services on every request. Load credentials from environment variables or the deployment secret manager; validate required settings at startup and redact them from logs.

Map the existing MySQL schema first rather than redesigning it during the runtime rewrite. Add Alembic migrations only for required schema evolution, and include forward/rollback SQL and a backup prerequisite. Preserve IDs and referential metadata. Keep file objects and existing Elasticsearch indexes in place when model and mapping compatibility checks pass; create a versioned index and reindex only when dimensions, model, or mapping changes.

## Risks / Trade-offs

- [RAG result drift between LangChain and LangChain4j] → Capture representative queries, routes, citations, and event sequences from the Java service; compare the Python shadow path before switching traffic.
- [Existing data and search mappings encode undocumented assumptions] → Inventory the live schema, indexes, metadata, and representative documents before implementation; validate with a production-like snapshot and preserve source IDs.
- [Long-running document work is duplicated after retries] → Use per-document stage transitions, idempotency keys, distributed locks where needed, and compensation jobs; test worker restart and duplicate delivery.
- [Text2SQL/Text2Cypher can access more data than intended] → Use read-only credentials, allowlists, parser-based validation, result limits, and execution timeouts; do not rely on prompt instructions as a security boundary.
- [Frontend/API migration breaks existing clients] → Keep the legacy route and SSE encoder during cutover, publish the new schema, and remove compatibility behavior only in a separately announced version.
- [Framework adoption adds operational services] → Start with one API deployment and one worker deployment using existing Redis; monitor queue depth, processing latency, model latency, and failure rates before scaling workers.

## Migration Plan

1. Inventory the current API contracts, SQL schema/data, Elasticsearch mappings and document counts, Redis session/cache use, MinIO objects, prompts, parser behavior, scheduler jobs, and DingTalk callback settings. Export representative fixtures and redact all secrets.
2. Build the Python API, worker, adapter contracts, health checks, and contract tests. First support read-only inspection of existing MySQL, Elasticsearch, and object data; verify IDs, versions, ACL metadata, vectors, and citations without writes.
3. Port ingestion and chat workflows behind a non-production/shadow route. Run a fixed evaluation set and compare state transitions, retrieval sources, relevance ordering, citations, stream events, and failure behavior against Java. Verify frontend flows against the versioned API.
4. Deploy Python alongside Java with one designated writer at a time. At cutover, pause writes and background jobs, take database/index/object-store backups, drain in-flight processing, verify pending-job counts, then switch API and worker ownership to Python. Avoid dual-writing the same lifecycle because partial cross-store writes cannot be made atomic.
5. Observe errors, queue lag, retrieval quality, cache publication, auth denials, and DingTalk delivery. Keep Java deployable and route traffic back only after reconciling any Python-side writes with the rollback snapshot. Once parity and recovery windows pass, retire Java endpoints and remove the static pages in a separate release.

## Open Questions

None. The initial plan assumes feature parity for the current user-facing and integration workflows, and uses the current production stores as the migration baseline.
