from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.runtime import RuntimeContainer


def get_runtime(request: Request) -> RuntimeContainer:
    return cast(RuntimeContainer, request.app.state.runtime)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    runtime: RuntimeContainer = request.app.state.runtime
    async with runtime.session_factory() as session:
        yield session
