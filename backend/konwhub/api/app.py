from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from konwhub.api.v1.router import router
from konwhub.application.auth_service import AuthService
from konwhub.application.chat import ConversationStore
from konwhub.application.document_store import DocumentStore
from konwhub.application.qa_cache import QaCacheService
from konwhub.application.organization import OrganizationService
from konwhub.core.logging import configure_logging
from konwhub.core.settings import get_settings
from konwhub.infrastructure.cache.redis_sessions import RedisSessionStore
from konwhub.infrastructure.cache.sessions import SessionStore
from konwhub.infrastructure.auth import AccountDirectory, SqlAccountAuthenticator
from konwhub.infrastructure.persistence.database import make_engine, make_session_factory
from konwhub.api.response import (
    envelope_json_response,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.add_middleware(BaseHTTPMiddleware, dispatch=envelope_json_response)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.state.settings = settings
    if settings.redis_url:
        try:
            from redis import Redis
            app.state.sessions = RedisSessionStore(Redis.from_url(settings.redis_url), settings.session_ttl_seconds)
        except ImportError:
            app.state.sessions = SessionStore(settings.session_ttl_seconds)
    else:
        app.state.sessions = SessionStore(settings.session_ttl_seconds)
    # 构建数据库引擎: 类似于Java的DataSource
    app.state.database_engine = make_engine(settings.database_url)
    app.state.db_session_factory = make_session_factory(app.state.database_engine)
    app.state.organization = OrganizationService(app.state.db_session_factory) if app.state.db_session_factory else None
    app.state.accounts = SqlAccountAuthenticator(app.state.database_engine, app.state.db_session_factory) if app.state.database_engine else AccountDirectory()
    app.state.auth_service = AuthService(app.state.accounts, app.state.sessions, settings)


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
    if settings.redis_url and hasattr(app.state.sessions, "client"):
        app.state.health_probes["redis"] = lambda: app.state.sessions.client.ping()
    app.include_router(router, prefix=settings.api_prefix)
    return app
