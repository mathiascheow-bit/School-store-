import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session


class Base(DeclarativeBase):
    pass


def _default_database_url() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(base_dir, "school_store.db")
    return f"sqlite:///{sqlite_path}"


def _create_engine():
    database_url = os.getenv("DATABASE_URL", _default_database_url())
    return create_engine(database_url, echo=False, future=True, pool_pre_ping=True)


engine = _create_engine()
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
SessionLocal = scoped_session(SessionFactory)


def get_db_session():
    return SessionLocal


def remove_db_session():
    SessionLocal.remove()
