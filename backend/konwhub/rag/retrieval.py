from collections import defaultdict
from datetime import date
from typing import Iterable

from konwhub.domain.ports import RetrievalDocument


def is_visible(document: RetrievalDocument, visible_scopes: set[str], today: date | None = None) -> bool:
    metadata = document.metadata or {}
    scopes = metadata.get("accessible_by", "VISITOR")
    allowed = {str(scope) for scope in scopes.split(",")} if isinstance(scopes, str) else set(scopes)
    expiry = metadata.get("expire_date")
    current = today or date.today()
    if expiry and str(expiry) < current.isoformat():
        return False
    if metadata.get("active_version") is False or metadata.get("deleted") is True:
        return False
    return not allowed or bool(allowed.intersection(visible_scopes))


def filter_authorized(documents: Iterable[RetrievalDocument], visible_scopes: set[str]) -> list[RetrievalDocument]:
    return [document for document in documents if is_visible(document, visible_scopes)]


def reciprocal_rank_fusion(*ranked_lists: list[RetrievalDocument], k: int = 60) -> list[RetrievalDocument]:
    scores: dict[tuple[str, str], float] = defaultdict(float)
    values: dict[tuple[str, str], RetrievalDocument] = {}
    for results in ranked_lists:
        for rank, document in enumerate(results, start=1):
            key = (str(document.document_id), str(document.chunk_id or document.text[:32]))
            scores[key] += 1 / (k + rank)
            values[key] = document
    return sorted((values[key] for key in scores), key=lambda item: scores[(str(item.document_id), str(item.chunk_id or item.text[:32]))], reverse=True)


def expand_parent_children(documents: Iterable[RetrievalDocument], all_documents: Iterable[RetrievalDocument]) -> list[RetrievalDocument]:
    source = list(all_documents)
    wanted = {str((item.metadata or {}).get("parent_chunk_id")) for item in documents if (item.metadata or {}).get("parent_chunk_id")}
    result = list(documents)
    seen = {(str(item.document_id), item.chunk_id) for item in result}
    for item in source:
        if str(item.chunk_id) in wanted and (str(item.document_id), item.chunk_id) not in seen:
            result.append(item)
    return result


def rerank_by_score(documents: Iterable[RetrievalDocument]) -> list[RetrievalDocument]:
    return sorted(documents, key=lambda item: item.score, reverse=True)
