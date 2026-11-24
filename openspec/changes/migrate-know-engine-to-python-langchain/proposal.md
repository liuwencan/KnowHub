# Proposal

## Why

The existing Java RAG system provides document ingestion, multi-source retrieval, streaming chat, knowledge administration, and reviewed answer caching, but those behaviors are coupled to a Java/Spring implementation. Rebuilding it as the Python project KonwHub with LangChain will make the RAG pipeline easier to extend and evaluate while preserving the workflows and data already in use.

## What Changes

- Replace the Java service with a Python API and worker application using FastAPI for HTTP/SSE and LangChain components for model, prompt, output parsing, and retrieval integrations. Deterministic chat and RAG steps are orchestrated by ordinary application code; LangGraph is not used.
- Preserve the existing document lifecycle, supported file types and split strategies, versioning, segment management, access filters, citations, chat history, feedback, and QA-cache review/publish lifecycle.
- Keep MySQL, Elasticsearch, Redis, Neo4j, and MinIO integration boundaries compatible during the first migration; provide explicit provider adapters and configuration rather than embedding infrastructure assumptions in chains.
- Port the existing query transformation, intent routing, hybrid/vector/full-text retrieval, Text2SQL/Text2Cypher routes, parent-child expansion, reranking, structured cards, and DingTalk adapter as independently testable components.
- Replace the static multi-page UI with a Vue 3 + TypeScript + Vite application covering chat, authentication, document/segment administration, and QA-cache review. Keep a documented API contract so another client can be used independently.
- Add a staged migration and verification path for existing MySQL records, Elasticsearch indexes, object files, authentication behavior, and external integrations. **BREAKING**: the Python service becomes the maintained runtime; existing Java endpoints and event payloads remain compatible during the transition, then are retired only after parity is verified.

## Capabilities

### New Capabilities
- `document-ingestion`: Upload, parse, split, version, index, inspect, edit, and remove knowledge documents and segments.
- `rag-chat`: Authenticated streaming conversations with routing, retrieval, citations, cards, feedback, and persisted history.
- `identity-access-control`: User/staff login, session handling, role and organization visibility, and retrieval-time document authorization.
- `qa-cache-lifecycle`: Curate, review, publish, retrieve, expire, invalidate, and maintain approved reusable answers.
- `integration-adapters`: Configurable LLM, embedding, vector/search, graph, relational query, object storage, and DingTalk integration boundaries.

### Modified Capabilities

None. This planning repository has no existing capability specs.

## Impact

The new Python project is named `KonwHub`; its migration source is the legacy Java repository at `E:\code\agent\LLMentor\know-engine`. A Python backend and Vue frontend will replace that Java/Spring runtime and its bundled static pages. The migration touches the current MySQL schema and data contracts, Elasticsearch mappings and indexes, Redis-backed sessions/cache/locks, MinIO objects, prompt files, model settings, scheduled compensation and QA-cache jobs, and DingTalk callbacks. Existing Java APIs and SSE markers are the compatibility baseline to document before implementation. Initial database and search-store compatibility is preferred; schema changes require explicit migration scripts and rollback guidance. Credentials must move to environment-based secrets and must not be copied from the current application configuration.
