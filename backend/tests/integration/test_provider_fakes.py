from konwhub.core.settings import Settings
from konwhub.infrastructure.health import dependency_health, readiness_status
from konwhub.infrastructure.integrations.dingtalk import DingTalkMessenger
from konwhub.infrastructure.providers import FakeChatModel, FakeEmbeddings, IdentityReranker
from konwhub.infrastructure.search.adapter import InMemorySearchAdapter
from konwhub.domain.ports import RetrievalDocument


def test_fake_provider_contracts_and_degraded_health() -> None:
    assert FakeChatModel("ok").complete("prompt") == "ok"
    assert len(FakeEmbeddings(4).embed("text")) == 4
    assert IdentityReranker().rerank("q", [RetrievalDocument("a", 1)])
    results = InMemorySearchAdapter([RetrievalDocument("car answer", 1, metadata={"accessible_by": "VISITOR"})]).search("car", visible_scopes={"VISITOR"})
    assert results[0].document_id == 1
    checks = dependency_health(Settings(chat_model="fake", embedding_model="fake", database_url="fake"), {"chat": lambda: True, "embeddings": lambda: True, "read_only_sql": lambda: False})
    assert checks["read_only_sql"]["status"] == "down"
    assert readiness_status(checks) == "not_ready"


def test_dingtalk_sender_is_observable() -> None:
    calls: list[tuple[str, str]] = []
    DingTalkMessenger(lambda recipient, message: calls.append((recipient, message))).deliver("fixture-user", "answer")
    assert calls == [("fixture-user", "answer")]
