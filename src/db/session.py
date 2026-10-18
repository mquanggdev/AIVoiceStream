from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    database_url = settings.database_url
    is_sqlite = database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(
        database_url, pool_pre_ping=True, connect_args=connect_args, echo=settings.sqlalchemy_echo
    )
    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with get_session_factory()() as session:
        yield session


def init_database() -> None:
    from src.db.base import Base
    from src.models import entities  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
