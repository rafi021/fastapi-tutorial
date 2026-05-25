from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.schemas.auth import RefreshTokenRequest, TokenPair
from app.services.auth_service import AuthService


class AuthController:
    @staticmethod
    def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
    ) -> TokenPair:
        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user.username, expires_delta=expires)
        refresh_token = create_refresh_token(subject=user.username)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_token(
        payload: RefreshTokenRequest,
        db: Session = Depends(get_db),
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
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = AuthService.get_user_by_username(db, username)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = create_access_token(subject=user.username)
        refresh_token = create_refresh_token(subject=user.username)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
