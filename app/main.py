from fastapi import FastAPI

from .db import Base, engine
from .routers import key_results, objectives

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecDev Course App", version="0.2.0")

# Подключаем роутеры
app.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
app.include_router(key_results.router, prefix="/key_results", tags=["Key Results"])
