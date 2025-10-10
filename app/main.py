import logging

from fastapi import FastAPI, Request

from app.middleware.errors import ExceptionLoggingMiddleware
from app.middleware.limits import BodySizeLimitMiddleware

from .db import Base, engine
from .routers import key_results, objectives

# === Создание таблиц ===
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.2.0")

# === Middleware ===
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(ExceptionLoggingMiddleware)

# === Роутеры ===
app.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
app.include_router(key_results.router, prefix="/key_results", tags=["Key Results"])

# === Логирование запросов ===
logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response
