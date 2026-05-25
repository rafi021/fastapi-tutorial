from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


def init_db(db: Session) -> None:
    admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
    if admin:
        return

    db.add(
        User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
    )
    db.commit()
