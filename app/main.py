from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.cache.redis_client import redis_client
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.rate_limit import limiter, rate_limit_handler
from app.core.startup_checks import run_startup_checks
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.metrics import MetricsMiddleware
from app.routes.auth_routes import router as auth_router
from app.routes.category_routes import router as category_router
from app.workers.celery_app import celery_app

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    app.state.redis_client = redis_client
    app.state.celery_app = celery_app
    app.state.redis_ready = False
    app.state.rabbitmq_ready = False

    try:
        run_startup_checks()
        init_db(db)

        try:
            redis_client.ping()
            app.state.redis_ready = True
        except Exception as exc:
            logger.warning("Redis startup check failed: %s", exc)

        try:
            with celery_app.connection_for_read() as connection:
                connection.ensure_connection(max_retries=1)
            app.state.rabbitmq_ready = True
        except Exception as exc:
            logger.warning("RabbitMQ startup check failed: %s", exc)

        yield
    finally:
        try:
            close = getattr(redis_client, "close", None)
            if callable(close):
                close()
            else:
                redis_client.connection_pool.disconnect()
        except Exception as exc:
            logger.warning("Redis shutdown cleanup failed: %s", exc)

        try:
            celery_app.close()
        except Exception as exc:
            logger.warning("Celery shutdown cleanup failed: %s", exc)

        db.close()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

    register_exception_handlers(app)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(category_router, prefix=settings.API_PREFIX)

    @app.get("/health", tags=["Health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics", tags=["Health"])
    def metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/health/dependencies", tags=["Health"])
    def health_dependencies(request: Request) -> JSONResponse:
        redis_ready = False
        rabbitmq_ready = False

        try:
            request.app.state.redis_client.ping()
            redis_ready = True
        except Exception as exc:
            logger.warning("Redis live check failed: %s", exc)

        try:
            with request.app.state.celery_app.connection_for_read() as connection:
                connection.ensure_connection(max_retries=1)
            rabbitmq_ready = True
        except Exception as exc:
            logger.warning("RabbitMQ live check failed: %s", exc)

        request.app.state.redis_ready = redis_ready
        request.app.state.rabbitmq_ready = rabbitmq_ready

        overall = "ok" if redis_ready and rabbitmq_ready else "degraded"
        status_code = 200 if overall == "ok" else 503

        return JSONResponse(
            status_code=status_code,
            content={
                "status": overall,
                "dependencies": {
                    "redis": {"ready": redis_ready},
                    "rabbitmq": {"ready": rabbitmq_ready},
                },
            },
        )

    return app


app = create_app()
