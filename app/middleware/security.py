import hmac
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

PROBLEM = "application/problem+json"


def _problem_response(status_code: int, title: str, detail: str) -> Response:
    """Возвращает RFC 7807-совместимый ответ."""
    body = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    return Response(
        content=json.dumps(body),
        status_code=status_code,
        media_type=PROBLEM,
    )


class ApiKeyGateMiddleware(BaseHTTPMiddleware):
    """
    Требует X-API-Key для модифицирующих запросов, если ключ задан.
    Ключ берётся из request.app.state.API_EDGE_KEY или окружения API_EDGE_KEY.
    OPTIONS/GET пропускаются.
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        cfg_key = getattr(request.app.state, "API_EDGE_KEY", None) or os.getenv("API_EDGE_KEY")

        # Пропускаем GET, OPTIONS и если ключ не задан
        if not cfg_key or request.method not in self.WRITE_METHODS:
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        sent = request.headers.get("x-api-key")
        ok = sent is not None and hmac.compare_digest(sent, cfg_key)
        if not ok:
            resp = _problem_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Missing or invalid X-API-Key.",
            )
            resp.headers["WWW-Authenticate"] = "ApiKey"
            return resp

        return await call_next(request)


class HSTSMiddleware(BaseHTTPMiddleware):
    """Добавляет Strict-Transport-Security."""

    def __init__(
        self,
        app: Any,
        max_age: int | None = None,
        include_subdomains: bool = True,
        preload: bool = False,
    ) -> None:
        super().__init__(app)
        self.max_age = max_age or int(os.getenv("HSTS_MAX_AGE", "15552000"))  # ~180 дней
        self.include_subdomains = include_subdomains
        self.preload = preload

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        parts = [f"max-age={self.max_age}"]
        if self.include_subdomains:
            parts.append("includeSubDomains")
        if self.preload:
            parts.append("preload")
        response.headers["Strict-Transport-Security"] = "; ".join(parts)
        return response
