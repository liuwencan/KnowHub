import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import UploadFile

from konwhub.api.dependencies import current_session, require_staff
from konwhub.ingestion.splitters import split_length, split_markdown_parent_child, split_markdown_sibling, split_regex, split_smart

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(request: Request, limit: int = 100, offset: int = 0, session=Depends(current_session)) -> list[dict[str, object]]:
    records = list(request.app.state.documents.documents.values())
    return [{"doc_id": item.doc_id, "doc_title": item.title, "status": item.status, "current_version_id": item.current_version_id} for item in records[offset:offset + limit]]


@router.post("/upload")
async def upload_document(request: Request, session=Depends(require_staff)) -> dict[str, object]:
    try:
        form = await request.form()
        file = form.get("file")
        filename = file.filename if isinstance(file, UploadFile) else request.headers.get("x-file-name")
        content = await file.read() if isinstance(file, UploadFile) else await request.body()
    except AssertionError:
        filename = request.headers.get("x-file-name")
        content = await request.body()
    if not filename or filename.rsplit(".", 1)[-1].lower() not in {"pdf", "docx", "xlsx", "xlsm", "csv", "md", "txt"}:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload exceeds 50 MiB limit")
    store = request.app.state.documents
    record = store.create(filename)
    version = store.add_version(record, hashlib.sha256(content).hexdigest())
    return {"doc_id": record.doc_id, "version_id": version.version_id, "status": record.status}


@router.get("/{doc_id}/segments")
def list_segments(doc_id: int, request: Request, limit: int = 100, offset: int = 0, session=Depends(current_session)) -> list[dict[str, object]]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return [{"id": item.segment_id, "text": item.text, "chunk_order": item.chunk_order, "metadata": item.metadata} for item in record.segments[offset:offset + limit] if not item.deleted]


@router.put("/{doc_id}/segments/{segment_id}")
async def edit_segment(doc_id: int, segment_id: int, request: Request, session=Depends(require_staff)) -> dict[str, object]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    segment = next((item for item in record.segments if item.segment_id == segment_id and not item.deleted), None)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    if segment.metadata.get("is_parent"):
        raise HTTPException(status_code=409, detail="Generated parent segment cannot be edited directly")
    body = await request.json()
    if "text" in body:
        segment.text = str(body["text"])
    segment.status = "STORED"
    return {"id": segment.segment_id, "text": segment.text, "status": segment.status}


@router.delete("/{doc_id}/segments/{segment_id}")
def delete_segment(doc_id: int, segment_id: int, request: Request, session=Depends(require_staff)) -> dict[str, bool]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    segment = next((item for item in record.segments if item.segment_id == segment_id), None)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    segment.deleted = True
    return {"success": True}


@router.get("/{doc_id}")
def get_document(doc_id: int, request: Request, session=Depends(current_session)) -> dict[str, object]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": record.doc_id, "doc_title": record.title, "status": record.status, "current_version_id": record.current_version_id, "accessible_by": record.accessible_by}


@router.get("/{doc_id}/versions")
def list_versions(doc_id: int, request: Request, session=Depends(current_session)) -> list[dict[str, object]]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return [{"version_id": item.version_id, "version": item.version, "status": item.status, "content_hash": item.content_hash} for item in record.versions]


@router.post("/{doc_id}/versions/{version_id}/activate")
def activate_version(doc_id: int, version_id: int, request: Request, session=Depends(require_staff)) -> dict[str, object]:
    try:
        record = request.app.state.documents.activate_version(doc_id, version_id)
    except (KeyError, StopIteration):
        raise HTTPException(status_code=404, detail="Version not found")
    return {"doc_id": record.doc_id, "current_version_id": record.current_version_id, "status": record.status}


@router.post("/{doc_id}/versions/{version_id}/deactivate")
def deactivate_version(doc_id: int, version_id: int, request: Request, session=Depends(require_staff)) -> dict[str, object]:
    try:
        record = request.app.state.documents.deactivate_version(doc_id, version_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": record.doc_id, "current_version_id": record.current_version_id, "status": record.status}


@router.post("/{doc_id}/split")
async def split_document(doc_id: int, request: Request, session=Depends(require_staff)) -> dict[str, object]:
    record = request.app.state.documents.documents.get(doc_id)
    if not record or not record.versions:
        raise HTTPException(status_code=404, detail="Document or version not found")
    body = await request.json()
    text = str(body.get("text", ""))
    split_type = body.get("split_type", "smart")
    max_length = int(body.get("max_length", 1200))
    splitters = {"smart": split_smart, "markdown_parent_child": split_markdown_parent_child, "markdown_sibling": split_markdown_sibling, "length": split_length}
    if split_type == "regex":
        parts = split_regex(text, str(body.get("pattern", "\\n+")))
    elif split_type in splitters:
        parts = splitters[split_type](text, max_length)
    else:
        raise HTTPException(status_code=422, detail="Unsupported split type")
    record.segments.clear()
    for part in parts:
        request.app.state.documents.add_segment(record, record.versions[-1].version_id, part.text, part.metadata)
    record.status = "CHUNKED"
    return {"doc_id": doc_id, "count": len(parts), "status": record.status}
