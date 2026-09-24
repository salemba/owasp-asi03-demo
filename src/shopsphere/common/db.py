from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from shopsphere.common.config import AppSettings
from shopsphere.common.telemetry import instrument_sqlalchemy_engine


def create_engine(settings: AppSettings) -> AsyncEngine:
    engine = create_async_engine(settings.database_dsn, pool_pre_ping=True, poolclass=NullPool)
    instrument_sqlalchemy_engine(engine)
    return engine


def create_session_factory(settings: AppSettings) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=create_engine(settings), expire_on_commit=False)
