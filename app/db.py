import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# === Определение среды ===
env = os.environ.get("ENV", "dev").lower()

# === 1. DATABASE_URL имеет приоритет ===
database_url = os.environ.get("DATABASE_URL")

if database_url:
    DATABASE_URL = database_url

else:
    # === 2. Fallback: подбираем путь вручную ===

    if env == "prod":
        # На Render NELZYA писать в /data — используем корень проекта
        sqlite_path = Path("okr.db")

    elif env == "ci":
        # GitHub CI — тесты ожидают data/ci-test.db
        sqlite_path = Path("data/ci-test.db")

    else:
        # Локальная разработка
        sqlite_path = Path("okr.db")

    # Создаём папки, если нужно
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    DATABASE_URL = f"sqlite:///{sqlite_path}"

# === Создание движка SQLAlchemy ===
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
