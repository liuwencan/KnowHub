from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from konwhub.api.dependencies import current_session, require_permission

router = APIRouter(prefix="/qa-cache", tags=["qa-cache"])


class ReviewRequest(BaseModel):
    comment: str | None = None
    dependencies: list[dict[str, object]] = []
    expires_at: datetime | None = None


def serialize(entry) -> dict[str, object]:
    return {"id": entry.entry_id, "question": entry.question, "answer": entry.answer, "status": entry.status.value, "reviewer": entry.reviewer, "review_note": entry.review_note, "expires_at": entry.expires_at.isoformat() if entry.expires_at else None, "index_error": entry.index_error, "hits": entry.hits}


@router.get("")
def list_entries(request: Request, session=Depends(require_permission("reviewer"))) -> list[dict[str, object]]:
    return [serialize(entry) for entry in request.app.state.qa_cache.entries.values()]


@router.post("/{entry_id}/approve")
def approve(entry_id: str, body: ReviewRequest, request: Request, session=Depends(require_permission("reviewer"))) -> dict[str, object]:
    try:
        entry = request.app.state.qa_cache.approve(entry_id, session.principal_id, body.dependencies, body.expires_at)
    except KeyError:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return serialize(entry)


@router.post("/{entry_id}/reject")
def reject(entry_id: str, body: ReviewRequest, request: Request, session=Depends(require_permission("reviewer"))) -> dict[str, object]:
    try:
        entry = request.app.state.qa_cache.entries[entry_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    entry.status = entry.status.REJECTED
    entry.reviewer = session.principal_id
    entry.review_note = body.comment
    return serialize(entry)


@router.post("/{entry_id}/disable")
def disable(entry_id: str, body: ReviewRequest, request: Request, session=Depends(require_permission("reviewer"))) -> dict[str, object]:
    try:
        entry = request.app.state.qa_cache.disable(entry_id, body.comment or "MANUAL")
    except KeyError:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    entry.reviewer = session.principal_id
    return serialize(entry)


@router.post("/{entry_id}/publish")
def publish(entry_id: str, request: Request, session=Depends(require_permission("reviewer"))) -> dict[str, object]:
    try:
        entry = request.app.state.qa_cache.publish(entry_id, lambda _: None)
    except KeyError:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))
    return serialize(entry)
