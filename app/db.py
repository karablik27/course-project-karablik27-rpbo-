# app/db.py
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

env = os.environ.get("ENV", "dev")

# === PRODUCTION ===
# Render пробрасывает ENV=prod → DB лежит в контейнерном /data/db/
if env == "prod":
    DATABASE_URL = "sqlite:////data/db/okr.db"

# === DEV + CI ===
# И локально, и в GitHub Actions тесты должны использовать okr.db в корне
else:
    DATABASE_URL = "sqlite:///./okr.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
