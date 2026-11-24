from fastapi.testclient import TestClient

from konwhub.api.app import create_app


def test_legacy_stream_emits_compatibility_markers() -> None:
    app = create_app()
    app.state.accounts.add("fixture-user", "fixture-password")
    client = TestClient(app)
    client.post("/api/v1/auth/login", json={"phone": "fixture-user", "password": "fixture-password"})
    response = client.post("/api/v1/chat/send-legacy", json={"message": "hello"})
    assert "[PROGRESS]:processing" in response.text
    assert "[DONE]:" in response.text
