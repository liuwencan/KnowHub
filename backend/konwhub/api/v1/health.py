from fastapi import APIRouter, Request

from konwhub.infrastructure.health import dependency_health, readiness_status

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness(request: Request) -> dict[str, object]:
    checks = dependency_health(request.app.state.settings, request.app.state.health_probes)
    return {"status": readiness_status(checks), "dependencies": checks}
