from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import OrderORM, OrderStatus
from shopsphere.mcp_servers.orders.domain.ports import OrdersRepository


class SqlOrdersRepository(OrdersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_order(self, order_id: UUID) -> OrderORM | None:
        return await self._session.get(OrderORM, order_id)

    async def list_customer_orders(self, customer_id: UUID) -> list[OrderORM]:
        stmt = (
            select(OrderORM)
            .where(OrderORM.customer_id == customer_id)
            .order_by(OrderORM.placed_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_order_status(self, order_id: UUID) -> OrderStatus | None:
        order = await self._session.get(OrderORM, order_id)
        return order.status if order else None
