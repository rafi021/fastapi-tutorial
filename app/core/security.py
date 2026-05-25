from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: Dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    token_id: Optional[str] = None,
) -> tuple[str, str]:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    jti = token_id or uuid.uuid4().hex
    payload: Dict[str, Any] = {"sub": subject, "exp": expire, "type": "refresh", "jti": jti}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), jti


def decode_access_token(token: str) -> Dict[str, Any]:
    return decode_token(token, expected_type="access")


def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            raise ValueError("Invalid token type")
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
