from fastapi import APIRouter

from konwhub.api.v1.auth import router as auth_router
from konwhub.api.v1.chat import router as chat_router
from konwhub.api.v1.conversations import router as conversations_router
from konwhub.api.v1.documents import router as documents_router
from konwhub.api.v1.health import router as health_router
from konwhub.api.v1.qa_cache import router as qa_cache_router
from konwhub.api.v1.organization import router as organization_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(conversations_router)
router.include_router(documents_router)
router.include_router(qa_cache_router)
router.include_router(organization_router)
