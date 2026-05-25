import time
from typing import Any

from app.cache.redis_client import redis_client
from app.core.config import settings


class LoginSecurityService:
    _fallback_store: dict[str, tuple[str, int]] = {}

    @staticmethod
    def _set_key(key: str, value: str, ttl_seconds: int) -> None:
        expires_at = int(time.time()) + max(ttl_seconds, 1)
        LoginSecurityService._fallback_store[key] = (value, expires_at)

    @staticmethod
    def _get_key(key: str) -> str | None:
        item = LoginSecurityService._fallback_store.get(key)
        if not item:
            return None
        value, expires_at = item
        if int(time.time()) >= expires_at:
            LoginSecurityService._fallback_store.pop(key, None)
            return None
        return value

    @staticmethod
    def _delete_key(key: str) -> None:
        LoginSecurityService._fallback_store.pop(key, None)

    @staticmethod
    def _key(username: str, client_ip: str, suffix: str) -> str:
        return f"auth:{suffix}:{username}:{client_ip}"

    @staticmethod
    def is_locked(username: str, client_ip: str) -> bool:
        lock_key = LoginSecurityService._key(username, client_ip, "lock")
        try:
            return redis_client.get(lock_key) is not None
        except Exception:
            return LoginSecurityService._get_key(lock_key) is not None

    @staticmethod
    def record_failed_attempt(username: str, client_ip: str) -> None:
        fail_key = LoginSecurityService._key(username, client_ip, "fail")
        lock_key = LoginSecurityService._key(username, client_ip, "lock")
        ttl_seconds = settings.LOGIN_LOCK_MINUTES * 60

        try:
            attempts: Any = redis_client.incr(fail_key)
            if attempts == 1:
                redis_client.expire(fail_key, ttl_seconds)
            if int(attempts) >= settings.LOGIN_MAX_ATTEMPTS:
                redis_client.setex(lock_key, ttl_seconds, "1")
        except Exception:
            current = LoginSecurityService._get_key(fail_key)
            attempts = int(current) + 1 if current else 1
            LoginSecurityService._set_key(fail_key, str(attempts), ttl_seconds)
            if attempts >= settings.LOGIN_MAX_ATTEMPTS:
                LoginSecurityService._set_key(lock_key, "1", ttl_seconds)

    @staticmethod
    def clear_failed_attempts(username: str, client_ip: str) -> None:
        fail_key = LoginSecurityService._key(username, client_ip, "fail")
        lock_key = LoginSecurityService._key(username, client_ip, "lock")
        try:
            redis_client.delete(fail_key)
            redis_client.delete(lock_key)
        except Exception:
            LoginSecurityService._delete_key(fail_key)
            LoginSecurityService._delete_key(lock_key)
