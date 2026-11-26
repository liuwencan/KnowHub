# KnowHub API Contract v1

This contract records the Java service surface used as the compatibility baseline for the Python migration. Values in examples are synthetic. Credentials, tokens, hostnames, and private document content are intentionally omitted.

## Envelope and authentication

All JSON endpoints in the Python API return the common envelope `{success, message, errorCode, data}`. Successful business values are always under `data`; errors set `success` to `false` and provide a stable HTTP or validation code in `errorCode`. Streaming chat endpoints remain `text/event-stream` and keep their typed event format. The versioned `/api/v1` namespace is used for new clients. Customer login is `POST /auth/login`; staff login is `POST /auth/staffLogin`; logout is `POST /auth/logout`; identity and status are `GET /auth/userInfo` and `GET /auth/isLogin`.

The compatibility client may send the opaque session in the `satoken` cookie or header. Protected requests require a live server-side session. Customer and staff sessions have separate principals; staff operations additionally require the configured reviewer/admin role.

## Chat and conversation routes

| Method | Legacy path | Request | Response |
| --- | --- | --- | --- |
| POST | `/chat/send` | `ChatParam` (`message`, optional `conversationId`) | `text/event-stream` |
| GET | `/chat/list` | none | `ChatConversation[]` |
| GET | `/chat/messages` | `conversationId` | `ChatMessage[]` |
| DELETE | `/chat/{conversationId}` | path id | boolean |
| GET | `/chat/conversation/list` | none | `{code,message,data}` |
| GET | `/chat/conversation/detail` | `conversationId` | `{code,message,data}` |
| POST | `/chat/conversation/create` | optional `title` | `{code,message,data}` |
| PUT | `/chat/conversation/archive` | `conversationId` | `{code,message,data}` |
| DELETE | `/chat/conversation/delete` | `conversationId` | `{code,message,data}` |
| GET | `/chat/message/list` | `conversationId` | `{code,message,data}` |
| GET | `/chat/message/detail` | `messageId` | `{code,message,data}` |
| POST | `/chat/message/saveUser` | `conversationId`, message fields | `{code,message,data}` |
| GET | `/chat/message/recent` | `conversationId`, optional limit | `{code,message,data}` |
| DELETE | `/chat/message/deleteByConversation` | `conversationId` | `{code,message,data}` |
| POST | `/chat/message/{messageId}/feedback` | `{helpful, comment?}` | empty success |

The Python typed event union is `progress`, `token`, `reference`, `card`, `warning`, `error`, and `done`. Legacy encoding is retained during cutover:

```text
[PROGRESS]:<message>
[REFERENCE]:<JSON array>
[CARD]:<JSON or display payload>
[WARN]:<message>
[ANSWER_MESSAGE]:<assistant message id>
[DONE]:<conversation id>
```

## Documents and segments

| Method | Legacy path | Purpose |
| --- | --- | --- |
| POST | `/api/document/upload` | Upload a supported file and create the first version |
| POST | `/api/document/upload-version` | Upload a new version |
| GET | `/api/document/page` | Paginated document listing (`current`, `size`, filters) |
| GET | `/api/document/list` | Filtered document list |
| GET | `/api/document/{id}` | Document detail |
| GET | `/api/document/versions/{docId}` | Version history |
| GET | `/api/document/data/{docId}` | Tabular preview |
| POST | `/api/document/split/{documentId}` | Split with `splitType` and options |
| POST | `/api/document/switch-version` | Activate a version for retrieval |
| POST | `/api/document/activate-version` | Activate a version |
| POST | `/api/document/deactivate-version` | Deactivate a version |
| PUT/DELETE | `/api/document` and `/api/document/{id}` | Admin update/delete |
| GET | `/api/segment/page`, `/api/segment/page-by-document` | Paginated segment listing |
| GET | `/api/segment/{id}`, `/api/segment/list-by-document` | Segment inspection |
| POST/PUT/DELETE | `/api/segment`, `/api/segment/{id}` | Segment create/edit/delete |

Document responses preserve `doc_id`, `current_version_id`, lifecycle status, ACL (`accessible_by`), expiry, and timestamps. Segment responses preserve `id`, `chunk_id`, `document_id`, `document_version`, `chunk_order`, `metadata`, `status`, and deletion state.

## QA-cache routes

`GET /api/qa-cache` lists candidates and reviewed entries. `GET /api/qa-cache/curate` and `GET /api/qa-cache/retire` are staff maintenance operations. Review transitions are `POST /api/qa-cache/{id}/approve`, `/reject`, `/disable`, `/publish`, and `/reactivate`; review bodies contain an optional comment, validity period, or disable reason. Only reviewers may inspect evidence or change review state.

## Error behavior

Authentication failures return a non-sensitive 401/403. Validation failures identify fields without echoing secrets. SSE errors use a typed `error` event followed by `done` when a stream has started. No response or log field contains passwords, API keys, session tokens, database URLs, or object-store credentials.
