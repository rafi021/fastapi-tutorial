from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import RefreshTokenRequest, TokenPair
from app.services.auth_service import AuthService
from app.services.login_security_service import LoginSecurityService
from app.services.token_store_service import TokenStoreService


class AuthController:
    @staticmethod
    def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm,
        db: Session,
    ) -> TokenPair:
        client_ip = request.client.host if request.client else "unknown"
        username = form_data.username

        if LoginSecurityService.is_locked(username, client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again later.",
            )

        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            LoginSecurityService.record_failed_attempt(username, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        LoginSecurityService.clear_failed_attempts(username, client_ip)

        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user.username, expires_delta=expires)
        refresh_token, refresh_jti = create_refresh_token(subject=user.username)

        refresh_ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        TokenStoreService.set_current_refresh_token(user.username, refresh_jti, refresh_ttl_seconds)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_token(
        payload: RefreshTokenRequest,
        db: Session,
    ) -> TokenPair:
        try:
            token_payload = decode_token(payload.refresh_token, expected_type="refresh")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        username = token_payload.get("sub")
        token_id = token_payload.get("jti")
        token_exp = token_payload.get("exp")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        if not token_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if TokenStoreService.is_refresh_token_revoked(token_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked")

        if not TokenStoreService.is_current_refresh_token(username, token_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is not active")

        user = AuthService.get_user_by_username(db, username)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = create_access_token(subject=user.username)
        refresh_token, new_token_id = create_refresh_token(subject=user.username)

        now_ts = int(datetime.now(timezone.utc).timestamp())
        old_ttl = max(int(token_exp) - now_ts, 1) if token_exp else 1
        new_ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        TokenStoreService.revoke_refresh_token(token_id, old_ttl)
        TokenStoreService.set_current_refresh_token(username, new_token_id, new_ttl)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)
