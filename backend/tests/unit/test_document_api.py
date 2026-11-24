from fastapi.testclient import TestClient

from konwhub.api.app import create_app


def staff_client() -> TestClient:
    app = create_app()
    app.state.accounts.add("fixture-staff", "fixture-password", role="staff", permissions={"reviewer"})
    client = TestClient(app)
    assert client.post("/api/v1/auth/staffLogin", json={"emp_id": "fixture-staff", "password": "fixture-password"}).status_code == 200
    return client


def test_document_version_split_and_segment_edit() -> None:
    client = staff_client()
    response = client.post("/api/v1/documents/upload", content=b"# A\nhello\n# B\nworld", headers={"x-file-name": "guide.md"})
    assert response.status_code == 200
    doc_id = response.json()["doc_id"]
    version_id = response.json()["version_id"]
    assert client.post(f"/api/v1/documents/{doc_id}/versions/{version_id}/activate").status_code == 200
    split = client.post(f"/api/v1/documents/{doc_id}/split", json={"text": "# A\nhello\n# B\nworld", "split_type": "markdown_parent_child"})
    assert split.json()["count"] == 4
    segments = client.get(f"/api/v1/documents/{doc_id}/segments").json()
    edited = client.put(f"/api/v1/documents/{doc_id}/segments/{segments[1]['id']}", json={"text": "updated"})
    assert edited.status_code == 200
