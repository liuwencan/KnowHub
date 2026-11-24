from fastapi.testclient import TestClient
from time import sleep

from konwhub.api.app import create_app
from konwhub.core.security import redact
from konwhub.application.ownership import ensure_owner
from konwhub.infrastructure.cache.sessions import SessionStore
from konwhub.infrastructure.cache.redis_sessions import RedisSessionStore
from konwhub.infrastructure.health import dependency_health, readiness_status


def test_health_and_session_flow() -> None:
    app = create_app()
    app.state.accounts.add("fixture-user", "fixture-password")
    client = TestClient(app)
    assert client.get("/api/v1/health/live").json() == {"status": "ok"}
    login = client.post("/api/v1/auth/login", json={"phone": "fixture-user", "password": "fixture-password"})
    assert login.status_code == 200
    assert client.get("/api/v1/auth/userInfo").json()["role"] == "customer"


def test_stream_has_typed_events() -> None:
    app = create_app()
    app.state.accounts.add("fixture-user", "fixture-password")
    client = TestClient(app)
    client.post("/api/v1/auth/login", json={"phone": "fixture-user", "password": "fixture-password"})
    response = client.post("/api/v1/chat/send", json={"message": "hello"})
    assert response.status_code == 200
    assert '"type": "done"' in response.text


def test_bad_password_and_staff_role_denied() -> None:
    app = create_app()
    app.state.accounts.add("fixture-user", "fixture-password")
    client = TestClient(app)
    assert client.post("/api/v1/auth/login", json={"phone": "fixture-user", "password": "wrong"}).status_code == 401
    assert client.post("/api/v1/auth/staffLogin", json={"emp_id": "fixture-user", "password": "fixture-password"}).status_code == 401


def test_staff_reviewer_session_can_access_review_route() -> None:
    app = create_app()
    app.state.accounts.add("fixture-staff", "fixture-password", role="staff", permissions={"reviewer"})
    client = TestClient(app)
    assert client.post("/api/v1/auth/staffLogin", json={"emp_id": "fixture-staff", "password": "fixture-password"}).status_code == 200
    assert client.get("/api/v1/qa-cache").status_code == 200


def test_session_expiry_and_redaction() -> None:
    store = SessionStore(ttl_seconds=1)
    session = store.create("fixture-user", "customer")
    assert store.get(session.token) is not None
    sleep(1.05)
    assert store.get(session.token) is None
    assert redact("secret") == "[REDACTED]"


def test_required_secret_validation_names_setting_without_value() -> None:
    from pydantic import ValidationError

    from konwhub.core.settings import Settings

    settings = Settings(required_secrets=("provider_api_key",))
    try:
        settings.validate_required_secrets()
    except ValueError as error:
        assert "provider_api_key" in str(error)
        assert "secret" not in str(error).lower()
    else:
        raise AssertionError("missing required key must fail startup validation")


def test_logout_invalidates_session_and_ownership_is_enforced() -> None:
    app = create_app()
    app.state.accounts.add("fixture-user", "fixture-password")
    client = TestClient(app)
    client.post("/api/v1/auth/login", json={"phone": "fixture-user", "password": "fixture-password"})
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/userInfo").status_code == 401
    try:
        ensure_owner("owner-a", "owner-b")
    except Exception as error:
        assert getattr(error, "status_code", None) == 404
    else:
        raise AssertionError("cross-user access must be denied")


def test_redis_session_store_uses_expiry_and_delete() -> None:
    class FakeRedis:
        def __init__(self):
            self.values = {}

        def setex(self, key, ttl, value):
            self.values[key] = value

        def get(self, key):
            return self.values.get(key)

        def delete(self, key):
            self.values.pop(key, None)

    store = RedisSessionStore(FakeRedis(), ttl_seconds=60)
    created = store.create("fixture-user", "customer")
    assert store.get(created.token).principal_id == "fixture-user"
    store.delete(created.token)
    assert store.get(created.token) is None


def test_health_probes_distinguish_required_and_optional_without_secrets() -> None:
    from konwhub.core.settings import Settings

    settings = Settings(chat_model="configured", provider_api_key="private-value", elasticsearch_url="http://example.invalid")
    checks = dependency_health(settings, {"chat": lambda: True, "elasticsearch": lambda: False})
    assert checks["chat"]["status"] == "up"
    assert checks["elasticsearch"]["status"] == "down"
    assert "private-value" not in str(checks)
    assert readiness_status(checks) == "not_ready"
