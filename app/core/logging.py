import contextvars
import json
import logging
from datetime import datetime, timezone

from app.core.config import settings

request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
user_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="anonymous")


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get()
        record.user_id = user_id_ctx_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "user_id": getattr(record, "user_id", "anonymous"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.addFilter(RequestContextFilter())
    handler.setFormatter(JsonFormatter())

    root_logger.setLevel(settings.LOG_LEVEL.upper())
    root_logger.addHandler(handler)
