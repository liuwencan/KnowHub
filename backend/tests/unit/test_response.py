from fastapi.testclient import TestClient

from konwhub.api.app import create_app


def test_json_api_responses_use_common_envelope() -> None:
    response = TestClient(create_app()).get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": None,
        "errorCode": None,
        "data": {"status": "ok"},
    }


def test_http_errors_use_common_envelope() -> None:
    response = TestClient(create_app()).get("/api/v1/auth/userInfo")

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["errorCode"] == "HTTP_401"
    assert response.json()["message"] == "Authentication required"
