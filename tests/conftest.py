from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shopsphere.common.config import AppSettings
from shopsphere.common.db import create_engine
from shopsphere.common.persistence.base import Base


def pytest_configure() -> None:
    defaults = {
        "SHOPSPHERE_DATABASE_PASSWORD": "test-password",
        "SHOPSPHERE_OPENAI_API_KEY": "test-openai",
        "SHOPSPHERE_ANTHROPIC_API_KEY": "test-anthropic",
        "SHOPSPHERE_GATEWAY_SUPPORT_AGENT_URL": "http://support-agent:8000",
        "SHOPSPHERE_SUPPORT_AGENT_SETTLEMENT_AGENT_URL": "http://settlement-agent:8000",
        "SHOPSPHERE_SETTLEMENT_AGENT_LEDGER_URL": "http://mcp-ledger:8000",
        "SHOPSPHERE_KEYCLOAK_ISSUER_URL": "http://keycloak:8080/realms/shopsphere",
        "SHOPSPHERE_KEYCLOAK_CLIENT_ID": "gateway",
        "SHOPSPHERE_KEYCLOAK_CLIENT_SECRET": "test-secret",
        "SHOPSPHERE_TELEMETRY_ENABLED": "false",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    settings = AppSettings(database_host="localhost")
    engine = create_engine(settings)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    except Exception:
        # Fallback to SQLite in-memory with attached schemas if PostgreSQL fails on Windows
        await engine.dispose()
        sqlite_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

        @event.listens_for(sqlite_engine.sync_engine, "connect")
        def attach_schemas(dbapi_conn: Any, record: Any) -> None:
            for schema in ["crm", "orders", "payments", "ledger", "audit"]:
                dbapi_conn.execute(f'ATTACH DATABASE ":memory:" AS {schema}')

        async with sqlite_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield sqlite_engine
        await sqlite_engine.dispose()
    else:
        await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
