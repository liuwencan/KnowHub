from fastapi.testclient import TestClient

from konwhub.api.app import create_app


def test_reviewer_can_transition_cache_entry() -> None:
    app = create_app()
    app.state.accounts.add("staff-1", "secret", role="staff", permissions={"reviewer"})
    entry = app.state.qa_cache.curate("question", "answer", [], 3)
    client = TestClient(app)
    client.post("/api/v1/auth/staffLogin", json={"emp_id": "staff-1", "password": "secret"})
    approved = client.post(f"/api/v1/qa-cache/{entry.entry_id}/approve", json={"dependencies": []})
    assert approved.status_code == 200
    published = client.post(f"/api/v1/qa-cache/{entry.entry_id}/publish")
    assert published.json()["status"] == "ACTIVE"
