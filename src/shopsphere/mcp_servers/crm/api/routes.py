from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.dependencies import get_db_session, get_runtime
from shopsphere.common.health import create_health_router
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext, get_caller_context
from shopsphere.mcp_servers.crm.tools import (
    CreateTicketInput,
    CustomerOutput,
    GetCustomerInput,
    GetRefundHistoryInput,
    RefundHistoryItem,
    TicketOutput,
    create_ticket_tool,
    get_customer_tool,
    get_refund_history_tool,
)

router = APIRouter()
router.include_router(create_health_router("mcp_crm"))


@router.post("/tools/get_customer")
async def get_customer(
    payload: GetCustomerInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> CustomerOutput | None:
    return await get_customer_tool(payload, ctx=ctx, authorizer=runtime.authorizer, session=session)


@router.post("/tools/create_ticket")
async def create_ticket(
    payload: CreateTicketInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> TicketOutput | None:
    return await create_ticket_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )


@router.post("/tools/get_refund_history")
async def get_refund_history(
    payload: GetRefundHistoryInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> list[RefundHistoryItem]:
    return await get_refund_history_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )
