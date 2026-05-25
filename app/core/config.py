from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Araf E-commerce API"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    APP_ENV: str = "development"

    DATABASE_URL: str = "mysql+pymysql://root:lerd@127.0.0.1/araf_ecommerce"
    SECRET_KEY: str = "change-this-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"
    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_REQUEST_SIZE_BYTES: int = 1048576

    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    OTEL_ENABLED: bool = True
    OTEL_SERVICE_NAME: str = "araf-ecommerce-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_EXPORTER_OTLP_INSECURE: bool = True

    RATE_LIMIT_PER_MINUTE: int = 60
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672//"

    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
