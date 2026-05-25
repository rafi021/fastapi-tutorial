from fastapi import APIRouter

from app.controllers.auth_controller import AuthController
from app.schemas.auth import TokenPair

router = APIRouter(prefix="/auth", tags=["Auth"])

router.post("/token", response_model=TokenPair)(AuthController.login)
router.post("/refresh", response_model=TokenPair)(AuthController.refresh_token)
