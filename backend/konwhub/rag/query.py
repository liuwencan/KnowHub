from dataclasses import dataclass, field
import json

from konwhub.domain.ports import ChatModelPort


@dataclass(frozen=True)
class IntentResult:
    related: bool
    intent: str
    entities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteDecision:
    route: str
    confidence: float


def parse_structured_intent(raw: str) -> IntentResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("model response was not valid JSON") from error
    if not isinstance(data.get("related"), bool) or not isinstance(data.get("intent"), str):
        raise ValueError("intent response must contain related and intent")
    return IntentResult(data["related"], data["intent"], {str(k): str(v) for k, v in (data.get("entities") or {}).items()})


def recognize_intent(model: ChatModelPort, question: str) -> IntentResult:
    return parse_structured_intent(model.complete(question))


def transform_query(model: ChatModelPort, question: str, user_id: str | None = None) -> str:
    response = model.complete(question).strip()
    return response or question


def route_intent(intent: IntentResult) -> RouteDecision:
    if not intent.related:
        return RouteDecision("general_chat", 1.0)
    name = intent.intent.lower()
    if "订单" in name or "order" in name or "数据库" in name:
        return RouteDecision("relational_data", 0.8)
    if "图" in name or "graph" in name:
        return RouteDecision("graph_data", 0.8)
    return RouteDecision("document_search", 0.8)
