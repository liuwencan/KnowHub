from fastapi import APIRouter, Depends, HTTPException, Request

from konwhub.api.dependencies import current_session

router = APIRouter(prefix="/chat/conversation", tags=["conversations"])


@router.get("/list")
def conversation_list(request: Request, session=Depends(current_session)) -> list[dict[str, str]]:
    return [{"conversation_id": item.conversation_id, "message_count": str(len(item.messages))} for item in request.app.state.conversations.list_owned(session.principal_id)]


@router.get("/{conversation_id}/messages")
def conversation_messages(conversation_id: str, request: Request, session=Depends(current_session)) -> list[dict[str, object]]:
    item = request.app.state.conversations.get_owned(conversation_id, session.principal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item.messages


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, request: Request, session=Depends(current_session)) -> dict[str, bool]:
    if not request.app.state.conversations.delete_owned(conversation_id, session.principal_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}


@router.post("/{conversation_id}/archive")
def archive_conversation(conversation_id: str, request: Request, session=Depends(current_session)) -> dict[str, bool]:
    if not request.app.state.conversations.archive_owned(conversation_id, session.principal_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}
