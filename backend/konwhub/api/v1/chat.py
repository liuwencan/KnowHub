import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from konwhub.api.dependencies import current_session
from konwhub.rag.events import ChatEvent, legacy_encode
from konwhub.schemas.api import ChatRequest, FeedbackRequest

router = APIRouter(prefix="/chat", tags=["chat"])


async def _chat_events(payload: ChatRequest, conversation_id: str) -> AsyncIterator[str]:
    yield f"data: {json.dumps({'type': 'progress', 'message': 'processing'}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'token', 'content': payload.message}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"


@router.post("/send")
async def send_chat(payload: ChatRequest, request: Request, session=Depends(current_session)) -> StreamingResponse:
    conversation = request.app.state.conversations
    item = conversation.get_owned(payload.conversation_id, session.principal_id) if payload.conversation_id else None
    if payload.conversation_id and item is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    item = item or conversation.create(session.principal_id)
    item.messages.extend([{"message_id": f"{item.conversation_id}-u-{len(item.messages) + 1}", "role": "user", "content": payload.message}, {"message_id": f"{item.conversation_id}-a-{len(item.messages) + 2}", "role": "assistant", "content": "", "references": [], "feedback": None}])
    return StreamingResponse(_chat_events(payload, item.conversation_id), media_type="text/event-stream")


@router.post("/send-legacy")
async def send_legacy_chat(payload: ChatRequest, session=Depends(current_session)) -> StreamingResponse:
    conversation_id = payload.conversation_id or f"conv-{session.principal_id}"

    async def events():
        for event in (ChatEvent("progress", {"message": "processing"}), ChatEvent("token", {"content": payload.message}), ChatEvent("done", {"conversation_id": conversation_id})):
            yield f"data: {legacy_encode(event)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.post("/message/{message_id}/feedback")
def feedback(message_id: str, payload: FeedbackRequest, request: Request, session=Depends(current_session)) -> dict[str, object]:
    for conversation in request.app.state.conversations.list_owned(session.principal_id):
        if any(message.get("message_id") == message_id and message.get("role") == "assistant" for message in conversation.messages):
            if message_id in request.app.state.feedback:
                return {"message_id": message_id, "recorded": False}
            request.app.state.feedback[message_id] = {"helpful": payload.helpful, "comment": payload.comment}
            return {"message_id": message_id, "helpful": payload.helpful, "recorded": True}
    raise HTTPException(status_code=404, detail="Message not found")
