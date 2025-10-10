from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

MAX_BODY_SIZE = 1 * 1024 * 1024


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        if len(body) > MAX_BODY_SIZE:
            return Response(
                content="Payload Too Large",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        return await call_next(request)
