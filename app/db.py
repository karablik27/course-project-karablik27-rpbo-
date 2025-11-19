import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

env = os.environ.get("ENV", "dev").lower()

database_url = os.environ.get("DATABASE_URL")

if database_url:
    DATABASE_URL = database_url
else:
    if env == "prod":
        sqlite_path = Path("data/prod.db")
    elif env == "ci":
        sqlite_path = Path("data/ci.db")
    else:
        sqlite_path = Path("data/dev.db")

    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{sqlite_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
