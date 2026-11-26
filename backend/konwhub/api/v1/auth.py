import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from konwhub.api.dependencies import auth_service, current_session
from konwhub.application.auth_service import AuthService
from konwhub.schemas.api import Identity, LoginRequest, LoginResponse, StaffLoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, auth: AuthService = Depends(auth_service)) -> LoginResponse:
    logger.info("登录接口开始执行")
    session = auth.login(payload.identifier(), payload.password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(auth.session_cookie_name, session.token, httponly=True)
    return LoginResponse(identity=Identity(user_id=session.principal_id, role="customer"), expires_in=auth.session_ttl_seconds)


@router.post("/staffLogin", response_model=LoginResponse)
def staff_login(payload: StaffLoginRequest, response: Response, auth: AuthService = Depends(auth_service)) -> LoginResponse:
    session = auth.login(payload.identifier(), payload.password, "staff")
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(auth.session_cookie_name, session.token, httponly=True)
    return LoginResponse(identity=Identity(user_id=session.principal_id, role="staff", permissions=set(session.permissions)), expires_in=auth.session_ttl_seconds)


@router.post("/register", response_model=LoginResponse, status_code=201)
def register(payload: RegisterRequest, response: Response, request: Request, auth: AuthService = Depends(auth_service)) -> LoginResponse:
    service = getattr(request.app.state, "organization", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    try:
        user = service.register_user(payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    session = auth.login(user.username, payload.password)
    if session is None:
        raise HTTPException(status_code=500, detail="Unable to create session")
    response.set_cookie(auth.session_cookie_name, session.token, httponly=True)
    return LoginResponse(identity=Identity(user_id=session.principal_id, role=session.role, permissions=set(session.permissions)), expires_in=auth.session_ttl_seconds)


@router.post("/logout")
def logout(response: Response, session=Depends(current_session), auth: AuthService = Depends(auth_service)) -> dict[str, bool]:
    auth.logout(session.token)
    response.delete_cookie(auth.session_cookie_name)
    return {"success": True}


@router.get("/userInfo", response_model=Identity)
def user_info(session=Depends(current_session)) -> Identity:
    return Identity(user_id=session.principal_id, role=session.role, permissions=set(session.permissions))


@router.get("/isLogin")
def is_login(request: Request, auth: AuthService = Depends(auth_service)) -> dict[str, bool]:
    token = request.headers.get("satoken") or request.cookies.get(auth.session_cookie_name)
    return {"isLogin": auth.is_logged_in(token)}
