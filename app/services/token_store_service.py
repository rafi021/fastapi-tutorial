import hashlib
import time
from typing import Any

from app.cache.redis_client import redis_client


class TokenStoreService:
    _fallback_store: dict[str, tuple[str, int]] = {}

    @staticmethod
    def _hash_token_id(token_id: str) -> str:
        return hashlib.sha256(token_id.encode("utf-8")).hexdigest()

    @staticmethod
    def _set_key(key: str, value: str, ttl_seconds: int) -> None:
        expires_at = int(time.time()) + max(ttl_seconds, 1)
        TokenStoreService._fallback_store[key] = (value, expires_at)

    @staticmethod
    def _get_key(key: str) -> str | None:
        item = TokenStoreService._fallback_store.get(key)
        if not item:
            return None
        value, expires_at = item
        if int(time.time()) >= expires_at:
            TokenStoreService._fallback_store.pop(key, None)
            return None
        return value

    @staticmethod
    def set_current_refresh_token(username: str, token_id: str, ttl_seconds: int) -> None:
        key = f"refresh:current:{username}"
        value = TokenStoreService._hash_token_id(token_id)
        try:
            redis_client.setex(key, ttl_seconds, value)
        except Exception:
            TokenStoreService._set_key(key, value, ttl_seconds)

    @staticmethod
    def is_current_refresh_token(username: str, token_id: str) -> bool:
        key = f"refresh:current:{username}"
        expected = TokenStoreService._hash_token_id(token_id)
        try:
            value: Any = redis_client.get(key)
            return value == expected
        except Exception:
            return TokenStoreService._get_key(key) == expected

    @staticmethod
    def revoke_refresh_token(token_id: str, ttl_seconds: int) -> None:
        key = f"refresh:revoked:{TokenStoreService._hash_token_id(token_id)}"
        try:
            redis_client.setex(key, ttl_seconds, "1")
        except Exception:
            TokenStoreService._set_key(key, "1", ttl_seconds)

    @staticmethod
    def is_refresh_token_revoked(token_id: str) -> bool:
        key = f"refresh:revoked:{TokenStoreService._hash_token_id(token_id)}"
        try:
            value: Any = redis_client.get(key)
            return value is not None
        except Exception:
            return TokenStoreService._get_key(key) is not None
