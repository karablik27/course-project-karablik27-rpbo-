import json
import logging
import re
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

LOG_FILE = "error.log"


def _reset_file_logger() -> logging.Logger:
    """Пересоздаёт logger и file handler каждый раз.
    Это важно, потому что тест УДАЛЯЕТ error.log после импорта модуля.
    """

    logger = logging.getLogger("error_logger")
    logger.setLevel(logging.ERROR)

    # Удаляем старые handler'ы (важно!)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # Пересоздаём файл
    with open(LOG_FILE, "a", encoding="utf-8"):
        pass

    handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


def _mask_pii(text: str) -> str:
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

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        try:
            return await call_next(request)

        except Exception as e:

            # КРИТИЧЕСКО: пересоздаём logger ТУТ, не при импорте
            logger = _reset_file_logger()

            safe_message = _mask_pii(str(e))
            logger.error(f"Unhandled error: {safe_message}", exc_info=False)

            # flush
            for h in logger.handlers:
                try:
                    h.flush()
                except Exception as err:
                    logger.warning(f"Failed to flush log handler: {type(err).__name__}")

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
