import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from konwhub.api.dependencies import current_session
from konwhub.core.settings import Settings
from konwhub.infrastructure.health import dependency_health, readiness_status
from konwhub.rag.events import ChatEvent, legacy_encode
from konwhub.infrastructure.providers import FakeChatModel
from konwhub.application.chat import DeterministicChatOrchestrator
from konwhub.schemas.api import ChatRequest, FeedbackRequest, Identity, LoginRequest, LoginResponse, StaffLoginRequest

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(request: Request) -> dict[str, object]:
    checks = dependency_health(_settings(request), request.app.state.health_probes)
    return {"status": readiness_status(checks), "dependencies": checks}


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response) -> LoginResponse:
    account = request.app.state.accounts.authenticate(payload.phone, payload.password, "customer")
    if not account:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session = request.app.state.sessions.create(account.principal_id, account.role, set(account.permissions))
    response.set_cookie(request.app.state.settings.session_cookie_name, session.token, httponly=True)
    return LoginResponse(identity=Identity(user_id=session.principal_id, role="customer"), expires_in=request.app.state.settings.session_ttl_seconds)


@router.post("/auth/staffLogin", response_model=LoginResponse)
def staff_login(payload: StaffLoginRequest, request: Request, response: Response) -> LoginResponse:
    account = request.app.state.accounts.authenticate(payload.emp_id, payload.password, "staff")
    if not account:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session = request.app.state.sessions.create(account.principal_id, account.role, set(account.permissions))
    response.set_cookie(request.app.state.settings.session_cookie_name, session.token, httponly=True)
    return LoginResponse(identity=Identity(user_id=session.principal_id, role="staff", permissions=set(session.permissions)), expires_in=request.app.state.settings.session_ttl_seconds)


@router.post("/auth/logout")
def logout(request: Request, response: Response, session=Depends(current_session)) -> dict[str, bool]:
    request.app.state.sessions.delete(session.token)
    response.delete_cookie(request.app.state.settings.session_cookie_name)
    return {"success": True}


@router.get("/auth/userInfo", response_model=Identity)
def user_info(session=Depends(current_session)) -> Identity:
    return Identity(user_id=session.principal_id, role=session.role, permissions=set(session.permissions))


@router.get("/auth/isLogin")
def is_login(request: Request) -> dict[str, bool]:
    token = request.headers.get("satoken") or request.cookies.get(request.app.state.settings.session_cookie_name)
    return {"isLogin": request.app.state.sessions.get(token) is not None}


async def _chat_events(payload: ChatRequest, conversation_id: str) -> AsyncIterator[str]:
    yield f"data: {json.dumps({'type': 'progress', 'message': 'processing'}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'token', 'content': payload.message}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"


@router.post("/chat/send")
async def send_chat(payload: ChatRequest, request: Request, session=Depends(current_session)) -> StreamingResponse:
    conversation = request.app.state.conversations
    item = conversation.get_owned(payload.conversation_id, session.principal_id) if payload.conversation_id else None
    if payload.conversation_id and item is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    item = item or conversation.create(session.principal_id)
    item.messages.extend([{"message_id": f"{item.conversation_id}-u-{len(item.messages) + 1}", "role": "user", "content": payload.message}, {"message_id": f"{item.conversation_id}-a-{len(item.messages) + 2}", "role": "assistant", "content": "", "references": [], "feedback": None}])
    return StreamingResponse(_chat_events(payload, item.conversation_id), media_type="text/event-stream")


@router.post("/chat/send-legacy")
async def send_legacy_chat(payload: ChatRequest, session=Depends(current_session)) -> StreamingResponse:
    conversation_id = payload.conversation_id or f"conv-{session.principal_id}"

    async def events():
        for event in (ChatEvent("progress", {"message": "processing"}), ChatEvent("token", {"content": payload.message}), ChatEvent("done", {"conversation_id": conversation_id})):
            yield f"data: {legacy_encode(event)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.post("/chat/message/{message_id}/feedback")
def feedback(message_id: str, payload: FeedbackRequest, request: Request, session=Depends(current_session)) -> dict[str, object]:
    for conversation in request.app.state.conversations.list_owned(session.principal_id):
        if any(message.get("message_id") == message_id and message.get("role") == "assistant" for message in conversation.messages):
            if message_id in request.app.state.feedback:
                return {"message_id": message_id, "recorded": False}
            request.app.state.feedback[message_id] = {"helpful": payload.helpful, "comment": payload.comment}
            return {"message_id": message_id, "helpful": payload.helpful, "recorded": True}
    raise HTTPException(status_code=404, detail="Message not found")


@router.get("/chat/conversation/list")
def conversation_list(request: Request, session=Depends(current_session)) -> list[dict[str, str]]:
    return [{"conversation_id": item.conversation_id, "message_count": str(len(item.messages))} for item in request.app.state.conversations.list_owned(session.principal_id)]


@router.get("/chat/conversation/{conversation_id}/messages")
def conversation_messages(conversation_id: str, request: Request, session=Depends(current_session)) -> list[dict[str, object]]:
    item = request.app.state.conversations.get_owned(conversation_id, session.principal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item.messages


@router.delete("/chat/conversation/{conversation_id}")
def delete_conversation(conversation_id: str, request: Request, session=Depends(current_session)) -> dict[str, bool]:
    if not request.app.state.conversations.delete_owned(conversation_id, session.principal_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}


@router.post("/chat/conversation/{conversation_id}/archive")
def archive_conversation(conversation_id: str, request: Request, session=Depends(current_session)) -> dict[str, bool]:
    if not request.app.state.conversations.archive_owned(conversation_id, session.principal_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}
