import json
import logging
import os
import re
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

if os.environ.get("ENV") == "prod":
    LOG_DIR = "/app/logs"
    LOG_FILE = f"{LOG_DIR}/error.log"
else:
    LOG_DIR = "."
    LOG_FILE = "error.log"


def _ensure_logger() -> logging.Logger:
    """Создаёт FileLogger для error.log (требование тестов P06 C3★★)."""

    logger = logging.getLogger("error_logger")
    logger.setLevel(logging.ERROR)

    for h in list(logger.handlers):
        logger.removeHandler(h)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "a", encoding="utf-8"):
                pass

        handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    except Exception:
        handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = _ensure_logger()


def _mask_pii(text: str) -> str:
    """Маскировка email и паролей."""
    text = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "[email]",
        text,
    )

    text = re.sub(
        r"(?i)(password|token|secret)\s*[:=]\s*['\"]?([^'\"\s]+)['\"]?",
        r"\1:[MASKED]",
        text,
    )

    return text


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """Централизованная обработка ошибок (RFC7807) + маскирование PII."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)

        except Exception as e:
            safe_message = _mask_pii(str(e))

            logger.error(f"Unhandled error: {safe_message}", exc_info=False)

            for h in logger.handlers:
                try:
                    h.flush()
                except Exception as flush_err:
                    logger.warning(f"Failed to flush log handler: {type(flush_err).__name__}")

            problem = {
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred.",
            }

            return Response(
                content=json.dumps(problem),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/problem+json",
            )
