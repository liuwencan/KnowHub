from dataclasses import dataclass, field
from uuid import uuid4

from konwhub.domain.ports import ChatModelPort, RetrievalDocument
from konwhub.rag.events import ChatEvent
from konwhub.rag.query import IntentResult, route_intent


@dataclass
class Conversation:
    conversation_id: str
    owner_id: str
    messages: list[dict[str, object]] = field(default_factory=list)


class ConversationStore:
    def __init__(self) -> None:
        self._items: dict[str, Conversation] = {}

    def get_owned(self, conversation_id: str, owner_id: str) -> Conversation | None:
        item = self._items.get(conversation_id)
        return item if item and item.owner_id == owner_id else None

    def create(self, owner_id: str) -> Conversation:
        item = Conversation(str(uuid4()), owner_id)
        self._items[item.conversation_id] = item
        return item

    def list_owned(self, owner_id: str) -> list[Conversation]:
        return sorted((item for item in self._items.values() if item.owner_id == owner_id and not getattr(item, "archived", False)), key=lambda item: item.conversation_id)

    def delete_owned(self, conversation_id: str, owner_id: str) -> bool:
        item = self.get_owned(conversation_id, owner_id)
        if not item:
            return False
        del self._items[conversation_id]
        return True

    def archive_owned(self, conversation_id: str, owner_id: str) -> bool:
        item = self.get_owned(conversation_id, owner_id)
        if not item:
            return False
        item.archived = True
        return True


class DeterministicChatOrchestrator:
    def __init__(self, model: ChatModelPort, conversations: ConversationStore | None = None) -> None:
        self.model = model
        self.conversations = conversations or ConversationStore()

    def run(self, question: str, owner_id: str, conversation_id: str | None = None, intent: IntentResult | None = None, documents: list[RetrievalDocument] | None = None):
        conversation = self.conversations.get_owned(conversation_id, owner_id) if conversation_id else None
        if conversation_id and conversation is None:
            raise ValueError("conversation not found")
        if conversation is None:
            conversation = self.conversations.create(owner_id)
        yield ChatEvent("progress", {"message": "正在识别您的意图..."})
        decision = route_intent(intent or IntentResult(True, "知识查询"))
        yield ChatEvent("progress", {"message": f"route:{decision.route}"})
        citations = documents or []
        if decision.route != "general_chat" and not citations:
            yield ChatEvent("warning", {"message": "insufficient_evidence"})
        if citations:
            yield ChatEvent("reference", {"data": [item.__dict__ for item in citations]})
        answer = self.model.complete(question)
        conversation.messages.append({"role": "user", "content": question})
        conversation.messages.append({"role": "assistant", "content": answer})
        if answer:
            yield ChatEvent("token", {"content": answer})
        yield ChatEvent("done", {"conversation_id": conversation.conversation_id})
