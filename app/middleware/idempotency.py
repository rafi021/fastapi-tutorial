import json
import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.cache.redis_client import redis_client


class IdempotencyMiddleware(BaseHTTPMiddleware):
    _fallback_store: dict[str, tuple[str, int]] = {}
    _ttl_seconds = 24 * 60 * 60

    @staticmethod
    def _build_cache_key(request: Request, key: str) -> str:
        user_id = getattr(request.state, "user_id", "anonymous")
        return f"idempotency:{request.method}:{request.url.path}:{user_id}:{key}"

    @staticmethod
    def _set_fallback(key: str, value: str) -> None:
        expires_at = int(time.time()) + IdempotencyMiddleware._ttl_seconds
        IdempotencyMiddleware._fallback_store[key] = (value, expires_at)

    @staticmethod
    def _get_fallback(key: str) -> str | None:
        item = IdempotencyMiddleware._fallback_store.get(key)
        if not item:
            return None
        value, expires_at = item
        if int(time.time()) >= expires_at:
            IdempotencyMiddleware._fallback_store.pop(key, None)
            return None
        return value

    async def dispatch(self, request: Request, call_next):
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        cache_key = self._build_cache_key(request, idempotency_key)

        cached_payload = None
        try:
            cached_payload = redis_client.get(cache_key)
        except Exception:
            cached_payload = self._get_fallback(cache_key)

        if cached_payload:
            data = json.loads(cached_payload)
            return JSONResponse(status_code=data["status_code"], content=data["body"])

        response = await call_next(request)

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        replay_response = Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        if response.status_code < 500 and response.media_type == "application/json":
            try:
                payload = json.dumps(
                    {
                        "status_code": response.status_code,
                        "body": json.loads(body.decode("utf-8")),
                    }
                )
                try:
                    redis_client.setex(cache_key, self._ttl_seconds, payload)
                except Exception:
                    self._set_fallback(cache_key, payload)
            except Exception:
                pass

        return replay_response
