from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Функция для инъекции сесии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()