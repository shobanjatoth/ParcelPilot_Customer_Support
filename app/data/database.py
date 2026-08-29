# from collections.abc import Generator

# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# from app.config import settings


# class Base(DeclarativeBase):
#     """Base class for all SQLAlchemy ORM models."""


# engine = create_engine(
#     settings.database_url,
#     pool_pre_ping=True,
#     pool_recycle=1800,
# )

# SessionLocal = sessionmaker(
#     bind=engine,
#     class_=Session,
#     autoflush=False,
#     autocommit=False,
# )


# def get_db() -> Generator[Session, None, None]:
#     """FastAPI database session dependency."""
#     db = SessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()













from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


# =========================================================
# Database Engine
# =========================================================

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)


# =========================================================
# Session Factory
# =========================================================

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# =========================================================
# FastAPI Dependency
# =========================================================

def get_db() -> Generator[Session, None, None]:
    """Provide a database session to FastAPI endpoints."""

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
