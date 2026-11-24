from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class RetrievalDocument:
    text: str
    document_id: int | str
    version_id: int | str | None = None
    chunk_id: str | None = None
    score: float = 0.0
    source: str = "document"
    metadata: dict[str, object] | None = None


class ChatModelPort(Protocol):
    def complete(self, prompt: str) -> str: ...


class EmbeddingPort(Protocol):
    def embed(self, text: str) -> Sequence[float]: ...


class RerankerPort(Protocol):
    def rerank(self, query: str, documents: Sequence[RetrievalDocument]) -> list[RetrievalDocument]: ...


class DocumentSearchPort(Protocol):
    def search(self, query: str, *, visible_scopes: set[str], limit: int = 10) -> list[RetrievalDocument]: ...


class RelationalQueryPort(Protocol):
    def query(self, statement: str, *, limit: int = 100) -> list[dict[str, object]]: ...


class GraphQueryPort(Protocol):
    def query(self, statement: str, *, limit: int = 100) -> list[dict[str, object]]: ...


class ObjectStoragePort(Protocol):
    def put(self, key: str, content: bytes, content_type: str) -> str: ...
    def delete(self, key: str) -> None: ...


class MessagingPort(Protocol):
    def send(self, recipient: str, message: str) -> None: ...
