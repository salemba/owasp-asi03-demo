from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.dependencies import get_db_session, get_runtime
from shopsphere.common.health import create_health_router
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext, get_caller_context
from shopsphere.mcp_servers.orders.tools import (
    GetOrderInput,
    GetOrderStatusInput,
    ListCustomerOrdersInput,
    OrderStatusOutput,
    OrderSummary,
    get_order_status_tool,
    get_order_tool,
    list_customer_orders_tool,
)

router = APIRouter()
router.include_router(create_health_router("mcp_orders"))


@router.post("/tools/get_order")
async def get_order(
    payload: GetOrderInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> OrderSummary | None:
    return await get_order_tool(payload, ctx=ctx, authorizer=runtime.authorizer, session=session)


@router.post("/tools/list_customer_orders")
async def list_customer_orders(
    payload: ListCustomerOrdersInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> list[OrderSummary]:
    return await list_customer_orders_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )


@router.post("/tools/get_order_status")
async def get_order_status(
    payload: GetOrderStatusInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> OrderStatusOutput:
    return await get_order_status_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )
