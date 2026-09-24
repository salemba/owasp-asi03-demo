from __future__ import annotations

from typing import Protocol
from uuid import UUID

from shopsphere.common.persistence.models import OrderORM, OrderStatus


class OrdersRepository(Protocol):
    async def get_order(self, order_id: UUID) -> OrderORM | None: ...

    async def list_customer_orders(self, customer_id: UUID) -> list[OrderORM]: ...

    async def get_order_status(self, order_id: UUID) -> OrderStatus | None: ...
