"""统一 HTTP 响应封装及异常响应处理。

业务路由继续返回业务对象，应用边界负责把 JSON 响应转换为稳定的
``success/message/errorCode/data`` 契约。流式响应不经过该封装。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response as FastAPIResponse
from konwhub.schemas.api import Response

logger = logging.getLogger(__name__)


def _json_response(payload: Response[Any], status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload.model_dump(by_alias=True, exclude_none=False)),
    )


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """将 FastAPI HTTPException 转成统一错误响应。"""

    detail = exc.detail
    message = detail if isinstance(detail, str) else "请求处理失败"
    data = None if isinstance(detail, str) else detail
    return _json_response(Response.fail(message, f"HTTP_{exc.status_code}", data), exc.status_code)


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """将请求参数校验错误转成统一错误响应。"""

    return _json_response(Response.fail("请求参数校验失败", "VALIDATION_ERROR", exc.errors()), 422)


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """避免把服务端堆栈泄漏给客户端，同时保留服务端日志上下文。"""

    logger.exception("未处理的 API 异常", exc_info=exc)
    return _json_response(Response.fail("服务器内部错误", "INTERNAL_ERROR"), 500)


async def envelope_json_response(request: Request, call_next) -> FastAPIResponse:
    """封装 JSON 响应，跳过 SSE、文件和已经封装的响应。"""

    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type or response.status_code == 204:
        return response

    body = b"".join([chunk async for chunk in response.body_iterator])

    async def restore_body() -> Any:
        yield body

    response.body_iterator = restore_body()

    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return response

    if isinstance(payload, dict) and {"success", "message", "errorCode", "data"}.issubset(payload):
        return response

    if response.status_code >= 400:
        detail = payload.get("detail") if isinstance(payload, dict) else payload
        message = detail if isinstance(detail, str) else "请求处理失败"
        data = None if isinstance(detail, str) else detail
        wrapped = Response.fail(message, f"HTTP_{response.status_code}", data)
    else:
        wrapped = Response.success_response(payload)

    encoded = json.dumps(wrapped.model_dump(by_alias=True, exclude_none=False), ensure_ascii=False).encode("utf-8")
    async def wrapped_body() -> Any:
        yield encoded

    response.body_iterator = wrapped_body()
    response.headers["content-length"] = str(len(encoded))
    return response
