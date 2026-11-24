from konwhub.application.chat import DeterministicChatOrchestrator
from konwhub.domain.ports import RetrievalDocument
from konwhub.infrastructure.providers import FakeChatModel
from konwhub.infrastructure.search.adapter import validate_read_only_cypher, validate_read_only_sql
from konwhub.rag.events import ChatEvent, legacy_encode
from konwhub.rag.query import IntentResult


def test_read_only_guards_and_legacy_sse() -> None:
    assert "LIMIT" in validate_read_only_sql("SELECT * FROM car_info", {"car_info"})
    assert validate_read_only_cypher("MATCH (c:Car) RETURN c", {"Car"}).startswith("MATCH")
    try:
        validate_read_only_sql("DELETE FROM car_info", {"car_info"})
    except ValueError:
        pass
    else:
        raise AssertionError("write query must be rejected")
    assert legacy_encode(ChatEvent("done", {"conversation_id": "conv-1"})) == "[DONE]:conv-1"


def test_orchestrator_has_ordered_events_and_citations() -> None:
    model = FakeChatModel("**answer**")
    events = list(DeterministicChatOrchestrator(model).run("question", "user", intent=IntentResult(True, "知识查询"), documents=[RetrievalDocument("source", 1, chunk_id="c1")]))
    assert [event.type for event in events] == ["progress", "progress", "reference", "token", "done"]
    assert events[-1].payload["conversation_id"]
