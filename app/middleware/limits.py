from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        body = await request.body()
        if len(body) > MAX_BODY_SIZE:
            return Response(
                content="Payload Too Large",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        response = await call_next(request)
        return response
