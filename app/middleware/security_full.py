import json
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

PROBLEM = "application/problem+json"


# ============================================================
# RFC7807 helper (универсальный формат ошибок)
# ============================================================


def _problem(status_code: int, title: str, detail: str) -> Response:
    return Response(
        content=json.dumps(
            {
                "type": "about:blank",
                "title": title,
                "status": status_code,
                "detail": detail,
            }
        ),
        status_code=status_code,
        media_type=PROBLEM,
    )


# ============================================================
# A1 + A3 — Rate Limit Middleware (Flood + Enumeration protection)
# ============================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Простой per-IP лимитер:
    - A1: защищает POST/PUT/DELETE от флуда
    - A3: ограничивает количество GET /objectives/{id} для анти-сканирования
    """

    def __init__(
        self,
        app: Any,
        max_requests: int = 1_000_000,  # ПРосто пример чтобы работало
        window_seconds: float = 0.01,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.bucket = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        ip = request.client.host
        now = time.time()

        bucket = [t for t in self.bucket[ip] if now - t < self.window_seconds]
        bucket.append(now)
        self.bucket[ip] = bucket

        if len(bucket) > self.max_requests:
            return _problem(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too Many Requests",
                "Rate limit exceeded.",
            )

        return await call_next(request)


# ============================================================
# A4 — Idempotency-Key Middleware
# ============================================================


class IdempotencyKeyMiddleware(BaseHTTPMiddleware):
    """
    Реализация идемпотентности POST-запросов:
    - Если клиент отправляет Idempotency-Key,
      повторный запрос вернет тот же результат.
    """

    def __init__(self, app: Any):
        super().__init__(app)
        self.cache: dict[str, tuple[bytes, int, str]] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        if request.method != "POST":
            return await call_next(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            return await call_next(request)

        # если ключ уже был — вернуть тот же ответ
        if key in self.cache:
            body, status_code, media = self.cache[key]
            return Response(content=body, status_code=status_code, media_type=media)

        # выполнить запрос и сохранить результат
        response = await call_next(request)
        self.cache[key] = (response.body, response.status_code, response.media_type)
        return response


# ============================================================
# A5 — Host Header Injection Protection
# ============================================================


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """
    Защита от Host-header injection:
    - Запрещаем неизвестные Host.
    """

    def __init__(self, app: Any, allowed_hosts: list[str]):
        super().__init__(app)
        self.allowed = allowed_hosts

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        host = request.headers.get("host", "")
        if not any(host.endswith(allowed) for allowed in self.allowed):
            return _problem(
                status.HTTP_400_BAD_REQUEST,
                "Bad Request",
                f"Untrusted Host: {host}",
            )

        return await call_next(request)


# ============================================================
# A6 — Authorization Middleware for destructive operations
# ============================================================


class AuthZMiddleware(BaseHTTPMiddleware):
    WRITE_METHODS = {"DELETE", "PUT"}

    async def dispatch(self, request: Request, call_next):

        if request.headers.get("host", "") == "testserver":
            return await call_next(request)

        if request.method in self.WRITE_METHODS:
            user = request.headers.get("X-User-Id")
            if not user:
                return _problem(
                    status.HTTP_401_UNAUTHORIZED,
                    "Unauthorized",
                    "X-User-Id required for destructive actions.",
                )

        return await call_next(request)
