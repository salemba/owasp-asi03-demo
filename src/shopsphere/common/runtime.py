from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shopsphere.common.config import AppSettings
from shopsphere.common.db import create_session_factory
from shopsphere.common.security import AllowAllAuthorizer, Authorizer


class RuntimeContainer:
    """Shared runtime wiring for FastAPI components."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.session_factory: async_sessionmaker[AsyncSession] = create_session_factory(settings)
        self.authorizer: Authorizer = AllowAllAuthorizer()
