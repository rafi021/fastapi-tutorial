import asyncio
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import request_id_ctx_var, user_id_ctx_var


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_token = request_id_ctx_var.set(request_id)
        user_id_token = user_id_ctx_var.set("anonymous")
        request.state.request_id = request_id

        try:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > settings.MAX_REQUEST_SIZE_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "success": False,
                        "error": {
                            "code": "PAYLOAD_TOO_LARGE",
                            "message": "Request payload exceeds the allowed size",
                        },
                        "request_id": request_id,
                    },
                )

            response: Response = await asyncio.wait_for(
                call_next(request), timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": {
                        "code": "REQUEST_TIMEOUT",
                        "message": "Request processing timed out",
                    },
                    "request_id": request_id,
                },
            )
        finally:
            request_id_ctx_var.reset(request_id_token)
            user_id_ctx_var.reset(user_id_token)
