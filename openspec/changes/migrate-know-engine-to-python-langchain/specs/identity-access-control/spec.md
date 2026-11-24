# Spec Delta

## Purpose

This capability authenticates customers and staff, scopes each operation to the current identity, and protects documents and administrative actions from unauthorized access.

## ADDED Requirements

### Requirement: User and staff authentication
The system SHALL provide separate supported login flows for customer and staff identities and SHALL expose the authenticated identity and role to authorized clients.

#### Scenario: Valid identity signs in
- **WHEN** a customer or active staff member submits valid credentials to the corresponding login flow
- **THEN** the system establishes a session and returns the identity information needed by the client

#### Scenario: Invalid or inactive identity signs in
- **WHEN** credentials are invalid or a staff account is inactive
- **THEN** the system denies the session and returns a non-sensitive authentication error

#### Scenario: Session ends or expires
- **WHEN** an authenticated user logs out or the configured session expires
- **THEN** subsequent protected requests are denied until the user authenticates again

### Requirement: Ownership and role enforcement
The system SHALL enforce conversation ownership and role-based access for document administration, staff functions, and QA-cache review operations.

#### Scenario: User accesses another user's conversation
- **WHEN** a user requests, updates, or deletes a conversation they do not own
- **THEN** the system denies access without disclosing the conversation's content

#### Scenario: Non-reviewer accesses cache moderation
- **WHEN** a staff user without reviewer permission attempts to inspect evidence or change a QA-cache review state
- **THEN** the system denies the operation and does not expose source conversations

### Requirement: Retrieval-time document authorization
The system SHALL apply the current identity's document visibility scope before returning retrieved context, citations, previews, or generated answers.

#### Scenario: Retrieval filters inaccessible documents
- **WHEN** a query matches both visible and restricted documents
- **THEN** only visible documents can enter the model context or be returned as citations

#### Scenario: Visibility is revoked
- **WHEN** an operator removes a user's or group’s access to a document
- **THEN** subsequent retrieval requests exclude that document even if a cached or indexed representation exists

### Requirement: Secret handling
The system SHALL obtain credentials, signing secrets, and provider keys from protected deployment configuration and SHALL NOT return them in API responses or log them in plaintext.

#### Scenario: Application starts without a required secret
- **WHEN** a required secret is missing or invalid
- **THEN** the affected integration fails with a clear configuration diagnostic and no hard-coded fallback credential
