import json
import logging
import os
import re
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

# Путь к файлу логов
if os.environ.get("ENV") == "prod":
    LOG_DIR = "/app/logs"
    LOG_FILE = f"{LOG_DIR}/error.log"
else:
    LOG_DIR = "."
    LOG_FILE = "error.log"


def _ensure_logger() -> logging.Logger:
    """
    Создаёт FileLogger и ГАРАНТИРУЕТ, что error.log будет создан.
    Вызываем при КАЖДОЙ ошибке, иначе тест удаляет файл и логгер пишет в пустоту.
    """
    logger = logging.getLogger("error_logger")
    logger.setLevel(logging.ERROR)

    # убираем старые хендлеры → детерминированное поведение
    for h in list(logger.handlers):
        logger.removeHandler(h)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        # всегда пересоздаём файл, если он удалён тестом
        with open(LOG_FILE, "a", encoding="utf-8"):
            pass

        handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")

    except Exception:
        # fallback если нет прав (docker rootless)
        handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    return logger


def _mask_pii(text: str) -> str:
    """Маскирует email и пароли."""
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
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)

        except Exception as e:
            # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ:
            # ВСЕГДА пересоздаём логгер → тест гарантированно получит error.log
            log = _ensure_logger()

            safe = _mask_pii(str(e))
            log.error(f"Unhandled error: {safe}", exc_info=False)

            # flush без pass
            for h in log.handlers:
                try:
                    h.flush()
                except Exception as err:
                    log.warning(f"Flush failed: {type(err).__name__}")

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
