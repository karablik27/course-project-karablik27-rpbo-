import json
import logging
import os
import re
import tempfile

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

if os.environ.get("ENV_DEV") in ("ci", "dev"):
    TMP_DIR = tempfile.gettempdir()
    LOG_FILE = f"{TMP_DIR}/error.log"
else:
    LOG_DIR = "/app/logs" if os.environ.get("ENV") == "prod" else "."
    LOG_FILE = f"{LOG_DIR}/error.log"


def _create_logger() -> logging.Logger:
    """Always creates a fresh logger and ensures file exists."""
    logger = logging.getLogger("error_logger")
    logger.setLevel(logging.ERROR)

    for h in list(logger.handlers):
        logger.removeHandler(h)

    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        with open(LOG_FILE, "a", encoding="utf-8"):
            pass

        handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")

    except Exception:
        handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


def _mask_pii(text: str) -> str:
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", text)
    text = re.sub(
        r"(?i)(password|token|secret)\s*[:=]\s*['\"]?([^'\"\s]+)['\"]?", r"\1:[MASKED]", text
    )
    return text


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger = _create_logger()

            msg = _mask_pii(str(e))
            logger.error(f"Unhandled error: {msg}", exc_info=False)

            for h in logger.handlers:
                try:
                    h.flush()
                except Exception as flush_err:
                    logger.warning(f"Failed to flush log handler: {type(flush_err).__name__}")

            return Response(
                content=json.dumps(
                    {
                        "type": "about:blank",
                        "title": "Internal Server Error",
                        "status": 500,
                        "detail": "An unexpected error occurred.",
                    }
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/problem+json",
            )
