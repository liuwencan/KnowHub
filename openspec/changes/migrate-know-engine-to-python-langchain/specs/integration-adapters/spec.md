# Spec Delta

## Purpose

This capability connects the knowledge system to model providers, search and data stores, file storage, and messaging platforms through explicit, configurable boundaries.

## ADDED Requirements

### Requirement: Provider configuration
The system SHALL allow operators to configure chat models, embedding models, rerankers, and their credentials independently of application code.

#### Scenario: Operator changes a model provider
- **WHEN** an operator supplies valid provider, endpoint, model, and secret settings
- **THEN** the corresponding model or embedding capability uses those settings without changing conversation or document contracts

#### Scenario: Provider is unavailable
- **WHEN** a configured model or embedding provider is unavailable or rejects a request
- **THEN** the system reports a bounded integration error, preserves retryable work where applicable, and does not silently mark ingestion or generation successful

### Requirement: Search and data-source adapters
The system SHALL provide independently configurable adapters for vector and full-text search, relational queries, graph queries, and object storage.

#### Scenario: Search index is unavailable
- **WHEN** a search request cannot reach its configured index
- **THEN** the system returns a clear retrieval failure or uses an explicitly configured fallback and records which source produced the result

#### Scenario: Graph query fails
- **WHEN** graph query generation or execution fails
- **THEN** the system follows the configured document-search fallback and does not expose an unvalidated query result

#### Scenario: Relational query is generated
- **WHEN** natural language is routed to a relational data source
- **THEN** the system constrains execution to configured schemas and read-only allowed operations and returns results with their source identity

### Requirement: External messaging integration
The system SHALL accept configured DingTalk callbacks, validate their authenticity, and map accepted messages to the same conversation behavior exposed by the chat API.

#### Scenario: Valid private or group callback arrives
- **WHEN** a correctly signed callback contains a supported private message or an @mentioned group message
- **THEN** the system extracts the user question, invokes the shared chat workflow, and sends the completed response through the messaging provider

#### Scenario: Callback signature is invalid
- **WHEN** a callback signature or timestamp validation fails
- **THEN** the system rejects the callback without invoking model or retrieval services

### Requirement: Operational integration health
The system SHALL expose non-secret health and readiness information for required configured dependencies and SHALL identify degraded optional integrations.

#### Scenario: Operator checks readiness
- **WHEN** an operator requests readiness status
- **THEN** the system reports availability by dependency without returning credentials, connection strings, or private document content
