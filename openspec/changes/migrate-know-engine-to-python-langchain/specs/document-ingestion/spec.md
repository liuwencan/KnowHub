# Spec Delta

## Purpose

This capability manages knowledge sources from upload through parsing, chunking, indexing, version changes, and retirement while preserving source traceability and access boundaries.

## ADDED Requirements

### Requirement: Document ingestion lifecycle
The system SHALL accept supported knowledge files and advance each document through visible processing states until it is searchable or reports a recoverable failure.

#### Scenario: Supported file is ingested
- **WHEN** an authorized operator uploads a supported PDF, Word, Excel, Markdown, or text file with its knowledge-base type and metadata
- **THEN** the system stores the original, creates a document record, processes it, and exposes the current conversion, chunking, and indexing state

#### Scenario: Processing fails
- **WHEN** parsing, chunking, or indexing fails
- **THEN** the document retains a visible failed stage and diagnostic status, and an authorized operator or scheduled recovery process can retry the failed work without creating duplicate active chunks

### Requirement: Configurable splitting and segment management
The system SHALL support the existing smart, Markdown heading parent/child, Markdown sibling-context, length, regex/separator, and Excel-aware splitting behaviors, and SHALL allow authorized operators to inspect and edit resulting segments.

#### Scenario: Parent and sibling context is split
- **WHEN** a document is split using a structure-aware strategy
- **THEN** the system preserves chunk order and parent, child, and sibling relationships so retrieval can restore the intended context

#### Scenario: Operator edits a searchable segment
- **WHEN** an authorized operator edits or removes a segment
- **THEN** the system updates its stored representation and corresponding searchable representation, while preventing direct edits to a generated parent segment that is derived from child segments

#### Scenario: Excel rows are chunked
- **WHEN** an Excel or CSV source is processed
- **THEN** each emitted chunk preserves row-to-header meaning and does not split a row across chunks

### Requirement: Document version lifecycle
The system SHALL retain document version history and allow operators to upload, inspect, activate, deactivate, switch, or roll back versions without losing source-to-version traceability.

#### Scenario: New version is uploaded
- **WHEN** an operator uploads a higher version for an existing document
- **THEN** the system records its file, content identity, change note, processing state, and relationship to the document's prior versions

#### Scenario: Active version changes
- **WHEN** an operator activates, deactivates, or switches a version
- **THEN** retrieval uses only eligible active versions and their current indexed segments, and dependent answer-cache entries are invalidated when their source version is no longer valid

### Requirement: Knowledge access and source metadata
The system SHALL enforce document visibility during retrieval and preserve document, version, chunk, expiry, and retrieval metadata for inspection and citations.

#### Scenario: User searches restricted knowledge
- **WHEN** retrieval runs for a user whose identity has a defined visibility scope
- **THEN** documents outside that scope and expired documents are excluded from candidates and are not exposed through returned references

#### Scenario: Operator previews knowledge data
- **WHEN** an authorized operator views a document, its versions, its tabular data, or its segments
- **THEN** the system returns paginated or ordered records with stable document and version identifiers and the stored processing state
