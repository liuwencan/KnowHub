import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChatEvent:
    type: str
    payload: dict[str, Any]


def legacy_encode(event: ChatEvent) -> str:
    mapping = {"progress": "[PROGRESS]", "reference": "[REFERENCE]", "card": "[CARD]", "warning": "[WARN]", "done": "[DONE]", "error": "[ERROR]", "answer_message": "[ANSWER_MESSAGE]"}
    marker = mapping.get(event.type)
    if not marker:
        return event.payload.get("content", "")
    if event.type in {"reference", "card"}:
        value = json.dumps(event.payload.get("data", event.payload), ensure_ascii=False)
    elif event.type == "done":
        value = str(event.payload.get("conversation_id", ""))
    elif event.type == "answer_message":
        value = str(event.payload.get("message_id", ""))
    else:
        value = str(event.payload.get("message", event.payload.get("error", "")))
    return f"{marker}:{value}"


def typed_sse(event: ChatEvent) -> str:
    return f"data: {json.dumps({'type': event.type, **event.payload}, ensure_ascii=False)}\n\n"
