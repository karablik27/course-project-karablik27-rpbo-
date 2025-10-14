# app/middleware/security.py
import hmac
import json
import os

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

PROBLEM = "application/problem+json"


def _problem_response(status_code: int, title: str, detail: str) -> Response:
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
    Ключ берётся из request.app.state.API_EDGE_KEY или переменной окружения API_EDGE_KEY.
    OPTIONS/GET пропускаем (префлайт/чтение).
    """

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        # читаем ключ динамически — тест меняет app.state.API_EDGE_KEY «на лету»
        cfg_key = getattr(request.app.state, "API_EDGE_KEY", None) or os.getenv(
            "API_EDGE_KEY"
        )
        if not cfg_key or request.method not in self.WRITE_METHODS:
            return await call_next(request)

        # разрешим префлайт всегда
        if request.method == "OPTIONS":
            return await call_next(request)

        sent = request.headers.get("x-api-key")
        ok = sent is not None and hmac.compare_digest(sent, cfg_key)
        if not ok:
            # WWW-Authenticate даёт понять клиенту схему
            resp = _problem_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Missing or invalid X-API-Key.",
            )
            resp.headers["WWW-Authenticate"] = "ApiKey"
            return resp

        return await call_next(request)


class HSTSMiddleware(BaseHTTPMiddleware):
    """
    Всегда добавляет HSTS. В тестах этот заголовок обязателен.
    Настройки: HSTS_MAX_AGE (сек), HSTS_INCLUDE_SUBDOMAINS, HSTS_PRELOAD.
    """

    def __init__(
        self,
        app,
        max_age: int | None = None,
        include_subdomains: bool = True,
        preload: bool = False,
    ):
        super().__init__(app)
        self.max_age = max_age or int(
            os.getenv("HSTS_MAX_AGE", "15552000")
        )  # ~180 дней
        self.include_subdomains = include_subdomains
        self.preload = preload

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        v = [f"max-age={self.max_age}"]
        if self.include_subdomains:
            v.append("includeSubDomains")
        if self.preload:
            v.append("preload")
        response.headers["Strict-Transport-Security"] = "; ".join(v)
        return response
