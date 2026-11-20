"""Consistent API error envelope.

Success: {"success": true,  "message": "...", "data": {...}}
Error:   {"success": false, "message": "...", "code": "SOME_CODE", "errors": {field: msg}}
"""
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str = "ERROR",
        errors: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.code = code
        self.errors = errors or {}
        self.headers = headers


def ok(message: str = "OK", data: Any = None) -> Dict[str, Any]:
    body: Dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return body


def _error_body(message: str, code: str, errors: Optional[Dict[str, str]] = None):
    return {"success": False, "message": message, "code": code, "errors": errors or {}}


_DEFAULT_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
}


def _clean_validation_msg(msg: str) -> str:
    for prefix in ("Value error, ", "Assertion failed, "):
        if msg.startswith(prefix):
            msg = msg[len(prefix):]
    return msg[:1].upper() + msg[1:] if msg else msg


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.message, exc.code, exc.errors),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        errors: Dict[str, str] = {}
        for err in exc.errors():
            loc = [str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")]
            field = loc[-1] if loc else "__root__"
            if field not in errors:
                errors[field] = _clean_validation_msg(err.get("msg", "Invalid value"))
        if "__root__" in errors and len(errors) == 1:
            message = errors["__root__"]
        else:
            message = next(iter(errors.values()), "Please check the highlighted fields.")
        return JSONResponse(status_code=422, content=_error_body(message, "VALIDATION_ERROR", errors))

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(message, _DEFAULT_CODES.get(exc.status_code, "ERROR")),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):  # pragma: no cover
        import logging

        logging.getLogger("intraviewer").exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content=_error_body("Something went wrong. Please try again.", "INTERNAL_ERROR"),
        )
