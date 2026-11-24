import re
from collections.abc import Iterable, Sequence

from konwhub.domain.ports import RetrievalDocument
from konwhub.rag.retrieval import filter_authorized, reciprocal_rank_fusion


class InMemorySearchAdapter:
    def __init__(self, documents: Iterable[RetrievalDocument] = ()) -> None:
        self.documents = list(documents)

    def search(self, query: str, *, visible_scopes: set[str], limit: int = 10) -> list[RetrievalDocument]:
        terms = {term.lower() for term in re.findall(r"\w+", query)}
        candidates = filter_authorized(self.documents, visible_scopes)
        ranked = sorted(candidates, key=lambda item: (len(terms.intersection(set(re.findall(r"\w+", item.text.lower())))), item.score), reverse=True)
        return ranked[:limit]

    def hybrid_search(self, query: str, vector_results: Sequence[RetrievalDocument], *, visible_scopes: set[str], limit: int = 10) -> list[RetrievalDocument]:
        return reciprocal_rank_fusion(list(vector_results), self.search(query, visible_scopes=visible_scopes, limit=limit))[:limit]

    def upsert(self, document: RetrievalDocument) -> None:
        self.documents = [item for item in self.documents if not (item.document_id == document.document_id and item.chunk_id == document.chunk_id)]
        self.documents.append(document)

    def delete(self, document_id: int | str, chunk_id: str | None = None) -> None:
        self.documents = [item for item in self.documents if item.document_id != document_id or (chunk_id is not None and item.chunk_id != chunk_id)]


class ElasticsearchSearchAdapter:
    def __init__(self, client, index_name: str = "know-engine-vector") -> None:
        self.client = client
        self.index_name = index_name

    def search(self, query: str, *, visible_scopes: set[str], limit: int = 10) -> list[RetrievalDocument]:
        response = self.client.search(index=self.index_name, query={"multi_match": {"query": query, "fields": ["text", "metadata"]}}, size=limit)
        return [RetrievalDocument(hit["_source"]["text"], hit["_source"].get("document_id", hit["_id"]), hit["_source"].get("version_id"), hit["_source"].get("chunk_id"), float(hit.get("_score") or 0), "elasticsearch", hit["_source"].get("metadata")) for hit in response["hits"]["hits"]]


def validate_read_only_sql(statement: str, allowed_tables: set[str], limit: int = 100) -> str:
    normalized = statement.strip().lower()
    if not normalized.startswith("select") or any(token in normalized for token in (" insert ", " update ", " delete ", " drop ", " alter ", ";")):
        raise ValueError("only one read-only SELECT statement is permitted")
    tables = set(re.findall(r"\bfrom\s+([a-zA-Z_][\w]*)|\bjoin\s+([a-zA-Z_][\w]*)", normalized))
    names = {item for pair in tables for item in pair if item}
    if not names.issubset({table.lower() for table in allowed_tables}):
        raise ValueError("query references a table outside the configured allowlist")
    return f"{statement.rstrip(';')} LIMIT {min(max(limit, 1), 1000)}"


def validate_read_only_cypher(statement: str, allowed_labels: set[str]) -> str:
    normalized = statement.lower()
    if any(token in normalized for token in ("create", "merge", "delete", "remove", "set", "drop", "call dbms")):
        raise ValueError("write operations are not permitted")
    labels = set(re.findall(r":([A-Za-z_][\w]*)", statement))
    if not labels.issubset(allowed_labels):
        raise ValueError("query references a label outside the configured allowlist")
    return statement.strip()
