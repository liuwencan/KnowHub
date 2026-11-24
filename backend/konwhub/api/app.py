from fastapi import FastAPI

from konwhub.api.v1.router import router
from konwhub.api.v1.documents import router as document_router
from konwhub.api.v1.qa_cache import router as qa_cache_router
from konwhub.application.auth import AccountDirectory, SqlAccountAuthenticator
from konwhub.application.chat import ConversationStore
from konwhub.application.document_store import DocumentStore
from konwhub.application.qa_cache import QaCacheService
from konwhub.core.logging import configure_logging
from konwhub.core.settings import get_settings
from konwhub.infrastructure.cache.redis_sessions import RedisSessionStore
from konwhub.infrastructure.cache.sessions import SessionStore
from konwhub.infrastructure.persistence.database import make_engine


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.state.settings = settings
    if settings.redis_url:
        from redis import Redis

        app.state.sessions = RedisSessionStore(Redis.from_url(settings.redis_url), settings.session_ttl_seconds)
    else:
        app.state.sessions = SessionStore(settings.session_ttl_seconds)
    app.state.database_engine = make_engine(settings.database_url)
    app.state.accounts = SqlAccountAuthenticator(app.state.database_engine) if app.state.database_engine else AccountDirectory()
    app.state.documents = DocumentStore()
    app.state.qa_cache = QaCacheService()
    app.state.conversations = ConversationStore()
    app.state.feedback = {}
    app.state.health_probes = {}
    if app.state.database_engine:
        from sqlalchemy import text

        def check_sql() -> bool:
            with app.state.database_engine.connect() as connection:
                return connection.execute(text("SELECT 1")).scalar_one() == 1

        app.state.health_probes["read_only_sql"] = check_sql
    if settings.redis_url:
        app.state.health_probes["redis"] = lambda: app.state.sessions.client.ping()
    app.include_router(router, prefix=settings.api_prefix)
    app.include_router(document_router, prefix=settings.api_prefix)
    app.include_router(qa_cache_router, prefix=settings.api_prefix)
    return app
