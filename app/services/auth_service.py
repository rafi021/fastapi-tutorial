from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()
