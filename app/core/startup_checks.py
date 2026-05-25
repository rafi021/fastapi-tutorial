from app.core.config import settings


REQUIRED_PRODUCTION_SETTINGS = [
    "SECRET_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "RABBITMQ_URL",
]


def run_startup_checks() -> None:
    if settings.APP_ENV.lower() != "production":
        return

    missing = []
    for key in REQUIRED_PRODUCTION_SETTINGS:
        value = getattr(settings, key, None)
        if not value:
            missing.append(key)

    if settings.SECRET_KEY == "change-this-secret-key":
        missing.append("SECRET_KEY(custom)")

    if missing:
        raise RuntimeError(f"Missing required production settings: {', '.join(missing)}")
