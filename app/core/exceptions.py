import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx_var, trace_id_ctx_var

logger = logging.getLogger(__name__)


def _error_payload(
    code: str,
    message: str,
    request_id: str,
    trace_id: str,
    details: object | None = None,
) -> dict:
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "request_id": request_id,
        "trace_id": trace_id,
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = request_id_ctx_var.get()
        trace_id = trace_id_ctx_var.get()
        code = f"HTTP_{exc.status_code}"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code=code,
                message=str(exc.detail),
                request_id=request_id,
                trace_id=trace_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = request_id_ctx_var.get()
        trace_id = trace_id_ctx_var.get()
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                request_id=request_id,
                trace_id=trace_id,
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = request_id_ctx_var.get()
        trace_id = trace_id_ctx_var.get()
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                code="INTERNAL_SERVER_ERROR",
                message="Unexpected server error",
                request_id=request_id,
                trace_id=trace_id,
            ),
        )
