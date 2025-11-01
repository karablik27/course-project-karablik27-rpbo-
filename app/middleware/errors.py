import json
import logging
import os
import re
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

LOG_FILE = "error.log"


def _ensure_logger() -> logging.Logger:
    """Гарантированно создаёт FileHandler, даже если pytest перехватывает logging."""
    logger = logging.getLogger("error_logger")
    logger.setLevel(logging.ERROR)

    # Удаляем все старые хендлеры (pytest может их подменять)
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # Гарантируем наличие файла
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    open(LOG_FILE, "a").close()

    handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8", delay=False)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = _ensure_logger()


def _mask_pii(text: str) -> str:
    """Маскирует возможные PII (email, токены, пароли) в строке."""
    # Маскируем email
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", text)

    # Маскируем password / token / secret, независимо от формата (= или :)
    text = re.sub(
        r"(?i)(password|token|secret)\s*[:=]\s*['\"]?[^'\"]+['\"]?",
        r"\1:[MASKED]",
        text,
    )

    return text


class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    """★★ C3 — централизованная обработка ошибок с маскированием PII."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Пересоздаём логгер на случай, если файл удалили
            if not os.path.exists(LOG_FILE):
                open(LOG_FILE, "w").close()

            safe_message = _mask_pii(str(e))
            log = _ensure_logger()
            log.error(f"Unhandled error: {safe_message}", exc_info=False)

            # Принудительно сбрасываем на диск
            for h in log.handlers:
                try:
                    h.flush()
                except Exception as flush_err:
                    # Безопасное логирование ошибки, без утечки деталей
                    log.warning(f"Failed to flush log handler: {type(flush_err).__name__}")

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
