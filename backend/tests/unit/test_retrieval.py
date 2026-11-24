from konwhub.domain.ports import RetrievalDocument
from konwhub.rag.query import IntentResult, parse_structured_intent, route_intent
from konwhub.rag.retrieval import filter_authorized, reciprocal_rank_fusion


def test_acl_expiry_and_fusion() -> None:
    visible = RetrievalDocument("visible", 1, chunk_id="a", score=.4, metadata={"accessible_by": "VISITOR"})
    restricted = RetrievalDocument("restricted", 2, chunk_id="b", metadata={"accessible_by": "STAFF"})
    assert filter_authorized([visible, restricted], {"VISITOR"}) == [visible]
    result = reciprocal_rank_fusion([visible], [visible, restricted])
    assert result[0] == visible


def test_intent_validation_and_routes() -> None:
    intent = parse_structured_intent('{"related": true, "intent": "订单查询", "entities": {"order_id": "ORD-TEST"}}')
    assert route_intent(intent).route == "relational_data"
