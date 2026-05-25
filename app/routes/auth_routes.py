from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.auth import RefreshTokenRequest
from app.schemas.auth import TokenPair

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenPair)
@limiter.limit("10/minute")
def login(
	request: Request,
	form_data: OAuth2PasswordRequestForm = Depends(),
	db: Session = Depends(get_db),
) -> TokenPair:
	return AuthController.login(request=request, form_data=form_data, db=db)


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("20/minute")
def refresh(
	request: Request,
	payload: RefreshTokenRequest,
	db: Session = Depends(get_db),
) -> TokenPair:
	return AuthController.refresh_token(payload=payload, db=db)
