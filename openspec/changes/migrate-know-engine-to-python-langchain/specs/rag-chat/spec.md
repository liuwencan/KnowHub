# Spec Delta

## Purpose

This capability provides authenticated, traceable conversations that combine direct model responses with routed retrieval over approved knowledge and business data.

## ADDED Requirements

### Requirement: Streaming conversation lifecycle
The system SHALL let an authenticated user create or continue a conversation, persist user and assistant messages, and stream answer output and processing status to the client.

#### Scenario: User streams a new RAG answer
- **WHEN** an authenticated user submits a question without a conversation identifier
- **THEN** the system creates a conversation, streams progress and answer content, persists both messages, and emits a completion event containing the conversation identifier

#### Scenario: User continues an existing conversation
- **WHEN** an authenticated user submits a question for an owned active conversation
- **THEN** the system includes permitted conversation context, persists the new exchange, and keeps the same conversation identifier

#### Scenario: Stream encounters a processing error
- **WHEN** a model or retrieval provider fails after streaming begins
- **THEN** the stream emits a client-readable error or warning and a terminal event, and the conversation remains available with its persisted partial or failed state clearly represented

### Requirement: Retrieval routing and answer grounding
The system SHALL route questions to the applicable general-chat, document-search, relational-data, or graph-data path and ground knowledge answers in authorized retrieved content.

#### Scenario: Knowledge question is routed
- **WHEN** a question is classified for document, relational, or graph retrieval
- **THEN** the system executes the selected route, applies configured fallback behavior on route failure, and generates an answer using the resulting context

#### Scenario: Question is unrelated to indexed knowledge
- **WHEN** intent handling determines that a question does not require the configured knowledge domain
- **THEN** the system uses the general-chat path without exposing unrelated retrieval results as evidence

#### Scenario: No relevant evidence is found
- **WHEN** retrieval returns no authorized result above the configured relevance threshold
- **THEN** the system does not present unsupported retrieved claims as grounded facts and informs the user that evidence was insufficient

### Requirement: Citations and structured response events
The system SHALL stream machine-readable progress, citations, warnings, structured cards, and completion metadata while preserving ordinary answer text and Markdown formatting.

#### Scenario: Retrieved evidence is used
- **WHEN** the assistant generates an answer from retrieved sources
- **THEN** the stream includes citations with stable document, version, chunk, source, and relevance metadata that the client can render alongside the answer

#### Scenario: Answer contains a supported card
- **WHEN** the response includes a recognized structured business card
- **THEN** the stream emits a typed card payload with validated data and continues or completes the answer stream without corrupting plain text

### Requirement: Conversation history and feedback
The system SHALL let users list, inspect, archive or delete their own conversations and submit feedback for an assistant message.

#### Scenario: User reads conversation history
- **WHEN** a user requests conversation history or message detail
- **THEN** only conversations owned by that user are returned in stable chronological order with their stored citations and message metadata

#### Scenario: User rates an answer
- **WHEN** a user submits helpful or unhelpful feedback for an assistant message they can access
- **THEN** the system records the first valid feedback and optional comment against that message for later quality analysis
