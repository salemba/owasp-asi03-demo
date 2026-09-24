from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.audit import write_audit_event
from shopsphere.common.security import Authorizer, CallerContext
from shopsphere.mcp_servers.orders.adapters.repositories import SqlOrdersRepository


class OrderSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    customer_id: UUID
    status: str
    total: Decimal
    currency: str
    placed_at: datetime
    delivered_at: datetime | None


class GetOrderInput(BaseModel):
    order_id: UUID


class ListCustomerOrdersInput(BaseModel):
    customer_id: UUID


class GetOrderStatusInput(BaseModel):
    order_id: UUID


class OrderStatusOutput(BaseModel):
    order_id: UUID
    status: str | None


async def get_order_tool(
    payload: GetOrderInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> OrderSummary | None:
    """Return full order details by order ID."""
    decision = await authorizer.authorize(ctx, "orders:get_order", f"orders/{payload.order_id}")
    await write_audit_event(
        session,
        ctx=ctx,
        action="orders:get_order",
        resource=f"orders/{payload.order_id}",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return None

    repository = SqlOrdersRepository(session)
    order = await repository.get_order(payload.order_id)
    await session.commit()
    if order is None:
        return None
    return OrderSummary(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status.value,
        total=order.total,
        currency=order.currency,
        placed_at=order.placed_at,
        delivered_at=order.delivered_at,
    )


async def list_customer_orders_tool(
    payload: ListCustomerOrdersInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> list[OrderSummary]:
    """List all known orders for a customer."""
    decision = await authorizer.authorize(
        ctx,
        "orders:list_customer_orders",
        f"customers/{payload.customer_id}/orders",
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="orders:list_customer_orders",
        resource=f"customers/{payload.customer_id}/orders",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return []

    repository = SqlOrdersRepository(session)
    orders = await repository.list_customer_orders(payload.customer_id)
    await session.commit()
    return [
        OrderSummary(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            total=order.total,
            currency=order.currency,
            placed_at=order.placed_at,
            delivered_at=order.delivered_at,
        )
        for order in orders
    ]


async def get_order_status_tool(
    payload: GetOrderStatusInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> OrderStatusOutput:
    """Return the order status enum for a given order."""
    decision = await authorizer.authorize(
        ctx, "orders:get_order_status", f"orders/{payload.order_id}/status"
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="orders:get_order_status",
        resource=f"orders/{payload.order_id}/status",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return OrderStatusOutput(order_id=payload.order_id, status=None)

    repository = SqlOrdersRepository(session)
    status = await repository.get_order_status(payload.order_id)
    await session.commit()
    return OrderStatusOutput(order_id=payload.order_id, status=status.value if status else None)
