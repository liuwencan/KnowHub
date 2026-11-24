# Spec Delta

## Purpose

This capability turns repeated, well-supported conversations into reusable answers only after human review, and keeps published answers synchronized with their evidence and validity.

## ADDED Requirements

### Requirement: Candidate curation
The system SHALL identify eligible repeated conversations, preserve their source evidence, and create deduplicated QA-cache candidates for human review.

#### Scenario: Eligible repeated questions are curated
- **WHEN** the configured curation job processes the defined history window
- **THEN** it groups eligible conversations, creates candidates with source question, answer, citations, frequency, and quality evidence, and does not publish them automatically

#### Scenario: Candidate duplicates an existing entry
- **WHEN** curation finds a candidate with the same normalized question or an equivalent active published answer
- **THEN** the system does not create a duplicate active cache entry

### Requirement: Human review and publication
The system SHALL require an authorized reviewer to approve, reject, edit, publish, disable, or reactivate a cache entry and SHALL record the review result and validity period.

#### Scenario: Reviewer approves candidate
- **WHEN** an authorized reviewer approves a candidate with a valid answer and expiration policy
- **THEN** the system records reviewer and review metadata, verifies its source dependencies, and publishes its question vector before the entry becomes active

#### Scenario: Publication fails
- **WHEN** approval is recorded but vector indexing fails
- **THEN** the entry remains non-active with an observable retryable error and a recovery task can retry publication

#### Scenario: Reviewer rejects or disables entry
- **WHEN** a reviewer rejects a candidate or disables an active entry
- **THEN** the entry cannot answer subsequent user queries and its vector is scheduled for cleanup

### Requirement: Safe cache retrieval
The system SHALL return a cached answer only when the entry is active, unexpired, sufficiently similar, and its source dependencies remain valid.

#### Scenario: Valid cache entry matches
- **WHEN** a user question matches an active entry above the configured similarity threshold and all referenced document versions remain eligible
- **THEN** the system returns the reviewed answer, records the hit, and marks the response as cache-served

#### Scenario: Cache entry is stale or weakly matched
- **WHEN** an entry is expired, disabled, below the threshold, or depends on changed or unverifiable knowledge
- **THEN** the cached answer is not returned and the request continues through the normal retrieval path where available

### Requirement: Cache maintenance and invalidation
The system SHALL maintain publication retries, expired vector cleanup, and source-dependent invalidation without allowing maintenance failures to reactivate invalid entries.

#### Scenario: Source knowledge changes
- **WHEN** a referenced document version is switched, removed, or loses required public visibility
- **THEN** dependent cache entries become ineligible immediately and their search vectors are removed by maintenance

#### Scenario: Scheduled maintenance retries failed work
- **WHEN** a maintenance run encounters an approved unpublished entry or a vector awaiting cleanup
- **THEN** it retries the pending operation, records per-entry outcomes, and leaves failed work visible for a later retry
