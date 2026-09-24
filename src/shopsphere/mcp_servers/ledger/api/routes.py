from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.dependencies import get_db_session, get_runtime
from shopsphere.common.health import create_health_router
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext, get_caller_context
from shopsphere.mcp_servers.ledger.tools import (
    GetCustomerBalanceInput,
    GetCustomerBalanceOutput,
    PostRefundEntryInput,
    PostRefundEntryOutput,
    get_customer_balance_tool,
    post_refund_entry_tool,
)

router = APIRouter()
router.include_router(create_health_router("mcp_ledger"))


@router.post("/tools/post_refund_entry")
async def post_refund_entry(
    payload: PostRefundEntryInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> PostRefundEntryOutput | None:
    return await post_refund_entry_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )


@router.post("/tools/get_customer_balance")
async def get_customer_balance(
    payload: GetCustomerBalanceInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> GetCustomerBalanceOutput:
    return await get_customer_balance_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )
