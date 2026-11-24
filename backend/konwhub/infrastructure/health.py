from collections.abc import Callable, Mapping


DEPENDENCIES = {
    "chat": ("chat_model", True),
    "embeddings": ("embedding_model", True),
    "reranking": ("reranker", False),
    "elasticsearch": ("elasticsearch_url", True),
    "neo4j": ("neo4j_url", False),
    "read_only_sql": ("database_url", True),
    "minio": ("minio_endpoint", True),
    "dingtalk": ("dingtalk_signing_secret", False),
}


def dependency_health(settings: object, probes: Mapping[str, Callable[[], bool]] | None = None) -> Mapping[str, dict[str, object]]:
    probes = probes or {}
    result: dict[str, dict[str, object]] = {}
    for name, (setting, required) in DEPENDENCIES.items():
        configured = bool(getattr(settings, setting, None))
        if not configured:
            status, detail = "unconfigured", None
        elif name not in probes:
            status, detail = "degraded", "connectivity probe unavailable"
        else:
            try:
                status, detail = ("up", None) if probes[name]() else ("down", "connectivity check failed")
            except Exception:
                status, detail = "down", "connectivity check failed"
        result[name] = {"status": status, "required": required, "detail": detail}
    return result


def readiness_status(dependencies: Mapping[str, Mapping[str, object]]) -> str:
    required = [item for item in dependencies.values() if item["required"]]
    if any(item["status"] in {"down", "unconfigured"} for item in required):
        return "not_ready"
    if any(item["status"] in {"down", "degraded"} for item in dependencies.values()):
        return "degraded"
    return "ready"
