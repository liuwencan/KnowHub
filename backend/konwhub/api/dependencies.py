from fastapi import Depends, Header, HTTPException, Request

from konwhub.application.auth_service import AuthService
from konwhub.infrastructure.cache.sessions import Session, SessionStore


def auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def session_store(request: Request) -> SessionStore:
    return request.app.state.sessions


def current_session(request: Request, satoken: str | None = Header(default=None)) -> Session:
    token = satoken or request.cookies.get(request.app.state.settings.session_cookie_name)
    session = request.app.state.sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session


def require_staff(session: Session = Depends(current_session)) -> Session:
    if session is None or session.role != "staff":
        raise HTTPException(status_code=403, detail="Staff role required")
    return session


def require_permission(permission: str):
    def dependency(session: Session = Depends(current_session)) -> Session:
        if session is None or permission not in session.permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return session
    return dependency
