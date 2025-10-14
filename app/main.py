# app/main.py
import logging
import os

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.middleware.errors import ExceptionLoggingMiddleware
from app.middleware.limits import BodySizeLimitMiddleware
from app.middleware.security import ApiKeyGateMiddleware, HSTSMiddleware

from .db import Base, engine
from .routers import key_results, objectives

# === Инициализация БД (создаст таблицы, если их нет) ===
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.2.0")

# --------------------------------------------------------------------------------------
# 1) CORS — СНАЧАЛА! (чтобы корректно обрабатывать preflight OPTIONS)
#    Источники читаем из env ALLOWED_ORIGINS (через запятую), по умолчанию — локальный фронт
# --------------------------------------------------------------------------------------
_ALLOWED = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _ALLOWED.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# 2) HSTS — всегда добавляем заголовок Strict-Transport-Security
#    (в проде при TLS; в тестах заголовок тоже проверяется)
# --------------------------------------------------------------------------------------
app.add_middleware(HSTSMiddleware)  # max-age по умолчанию ~180 дней

# --------------------------------------------------------------------------------------
# 3) Ограничение размера тела запроса — 413 при >1MB
# --------------------------------------------------------------------------------------
app.add_middleware(BodySizeLimitMiddleware)

# --------------------------------------------------------------------------------------
# 4) API Key Gate — требует X-API-Key для write-методов, если ключ задан
#    Ключ можно задать через: app.state.API_EDGE_KEY = "secret" или env API_EDGE_KEY
# --------------------------------------------------------------------------------------
app.add_middleware(ApiKeyGateMiddleware)

# --------------------------------------------------------------------------------------
# 5) Единый обработчик ошибок — Problem+JSON (RFC7807) без утечки stacktrace клиенту
# --------------------------------------------------------------------------------------
app.add_middleware(ExceptionLoggingMiddleware)

# === Роутеры ===
app.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
app.include_router(key_results.router, prefix="/key_results", tags=["Key Results"])

# === Логирование запросов (access) ===
logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(stream_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response
