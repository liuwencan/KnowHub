# Legacy KnowEngine Inventory (redacted)

Source: `E:/code/agent/LLMentor/know-engine`, inspected 2026-11-24. This inventory contains names and shapes only. Runtime endpoints, credentials, tokens, and private records are excluded.

## Persistence

MySQL tables in `src/main/resources/sql/tables.sql` include `knowledge_document`, `knowledge_document_version`, `knowledge_segment`, `table_meta`, `chat_conversation`, `chat_message`, `car_info`, `my_car`, `car_order`, `staff_info`, `user_info`, and QA-cache tables. Important indexes cover document status and creation time, `(doc_id, version)`, segment `(document_id, chunk_order)`, segment status, conversation id, and message creation time. IDs and lifecycle fields are retained by the migration.

Elasticsearch uses the knowledge index `know-engine-vector` and the QA-cache index `know-engine-qa-cache-v1`. Retrieval metadata includes document/version/chunk identifiers, ACL, expiry, source, and relevance. The Java implementation supports KNN, full-text, and hybrid retrieval, parent/sibling expansion, and reciprocal-rank fusion.

Redis is used by Sa-Token-compatible sessions, distributed document locks, cache state, and job coordination. MinIO stores original and converted documents plus extracted images; object names are derived from document/version identifiers and are never copied into fixtures. Neo4j is an optional read-only graph source. DingTalk callbacks deliver private messages and @mentioned group messages.

## Prompts and parsers

Versioned prompts exist for intent recognition, query transformation, Text2SQL, Text2Cypher, domain answer generation, QA-cache grouping, and QA-cache curation. Parsers cover PDF via the remote MinerU service, Word, Markdown, plain text, Excel, and CSV. Splitters include smart, Markdown parent/child, Markdown sibling, length, regex/separator, and Excel-aware strategies.

## Jobs and recovery

Document conversion/chunking/vector stages are event-driven with compensation for failed work. QA-cache curation runs weekly over a fixed seven-day window; publication/retirement maintenance runs periodically. Distributed locks protect document upload and lifecycle changes. The Python worker maps these stages to Celery tasks with durable stage/idempotency records.

## Representative redacted fixtures

- `fixtures/golden-rag.json`: synthetic questions, expected routes, ACL cases, citation shape, cards, and failure behavior.
- `fixtures/legacy-schema-sample.json`: synthetic row shapes for document, version, segment, conversation, and message records.
- Existing source fixtures used for parity: intent dataset, Markdown manual, Excel recall workbook, splitter tests, query-transformer tests, and QA-cache lifecycle tests.
