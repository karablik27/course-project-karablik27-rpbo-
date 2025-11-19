import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

env = os.environ.get("ENV", "local").lower()


if env == "prod":
    sqlite_path = Path("/data/db/okr.db")

elif env == "ci":
    sqlite_path = Path("./ci-test.db")

else:
    sqlite_path = Path("./okr.db")


sqlite_path.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{sqlite_path}"


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
