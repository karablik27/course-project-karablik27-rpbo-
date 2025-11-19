# app/main.py
import logging
import os
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.db import SessionLocal
from app.middleware.errors import ExceptionLoggingMiddleware
from app.middleware.limits import BodySizeLimitMiddleware
from app.middleware.security import ApiKeyGateMiddleware, HSTSMiddleware
from app.models import ObjectiveDB

from .db import Base, engine
from .routers import key_results, objectives, upload

# === Инициализация БД (создаст таблицы, если их нет) ===
Base.metadata.create_all(bind=engine)

# === CI seed: создаём одну запись для тестов ===
if os.getenv("ENV") == "ci":

    with SessionLocal() as db:
        if not db.query(ObjectiveDB).filter_by(id=1).first():
            db.add(
                ObjectiveDB(
                    id=1,
                    title="Seed objective for CI",
                    description="Automatically created to satisfy error_rate test",
                )
            )
            db.commit()
            print("[CI] Seeded Objective(id=1)")

app = FastAPI(title="SecDev Course App", version="0.2.1")


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}


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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# 2) HSTS — всегда добавляем заголовок Strict-Transport-Security
#    (в проде при TLS; в тестах заголовок тоже проверяется)
# --------------------------------------------------------------------------------------
# Параметры HSTS читаются внутри HSTSMiddleware из env:
# HSTS_MAX_AGE, HSTS_INCLUDE_SUBDOMAINS, HSTS_PRELOAD
app.add_middleware(HSTSMiddleware)  # max-age по умолчанию ~180 дней

# --------------------------------------------------------------------------------------
# 3) Ограничение размера тела запроса — 413 при >1MB
#     Включаем через флаг BODY_LIMIT_ENABLED (по умолчанию включено).
# --------------------------------------------------------------------------------------
if os.getenv("BODY_LIMIT_ENABLED", "1") == "1":
    app.add_middleware(BodySizeLimitMiddleware)

# --------------------------------------------------------------------------------------
# 4) API Key Gate — требует X-API-Key для write-методов, если ключ задан
#    Ключ можно задать через: app.state.API_EDGE_KEY = "secret" или env API_EDGE_KEY
#    Если ключа нет — middleware пропускает запросы (режим выключен).
# --------------------------------------------------------------------------------------
app.add_middleware(ApiKeyGateMiddleware)

# --------------------------------------------------------------------------------------
# 5) Единый обработчик ошибок — Problem+JSON (RFC7807) без утечки stacktrace клиенту
#    Включаем через флаг RFC7807_ENABLED (по умолчанию включено).
# --------------------------------------------------------------------------------------
if os.getenv("RFC7807_ENABLED", "1") == "1":
    app.add_middleware(ExceptionLoggingMiddleware)

# === Роутеры ===
app.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
app.include_router(key_results.router, prefix="/key_results", tags=["Key Results"])
app.include_router(upload.router, prefix="/files", tags=["Files"])

# === Логирование запросов (access) ===
logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Логирование всех запросов с кодами ответа."""
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# --------------------------------------------------------------------------------------
# 6) Пилот для ADR-004: проверка наличия response_model на публичных эндпоинтах
#    Управляется флагом RESPONSE_MODEL_POLICY ∈ {off, warn, enforce} (по умолчанию: warn)
#    - warn: логируем предупреждения, но не падаем
#    - enforce: выбрасываем исключение при старте, если нашли ручки без response_model
# --------------------------------------------------------------------------------------


def _check_response_models(app: FastAPI, policy: str = "warn") -> None:
    if policy not in {"off", "warn", "enforce"}:
        policy = "warn"

    if policy == "off":
        return

    # Сервисные пути, которые не проверяем
    skip_paths: set[str] = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
    bad = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in skip_paths:
            continue
        # Проверяем только основные HTTP-методы
        if not set(route.methods or set()).intersection({"GET", "POST", "PUT", "PATCH", "DELETE"}):
            continue
        # Если нет response_model — фиксируем
        if route.response_model is None:
            bad.append((route.path, sorted(route.methods)))

    if bad:
        msg = f"Endpoints without response_model: {bad}"
        if policy == "enforce":
            # Прервём запуск приложения
            raise RuntimeError(msg)
        else:
            logging.getLogger("access").warning(msg)


# Выполним проверку при старте приложения
@app.on_event("startup")
async def enforce_response_models_startup() -> None:
    policy = os.getenv("RESPONSE_MODEL_POLICY", "warn").lower()
    _check_response_models(app, policy)
