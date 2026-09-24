from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.dependencies import get_db_session, get_runtime
from shopsphere.common.health import create_health_router
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext, get_caller_context
from shopsphere.mcp_servers.payments.tools import (
    ListPaymentMethodsInput,
    PaymentMethodOutput,
    RefundOutput,
    RequestRefundInput,
    list_payment_methods_tool,
    request_refund_tool,
)

router = APIRouter()
router.include_router(create_health_router("mcp_payments"))


@router.post("/tools/request_refund")
async def request_refund(
    payload: RequestRefundInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> RefundOutput | None:
    return await request_refund_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )


@router.post("/tools/list_payment_methods")
async def list_payment_methods(
    payload: ListPaymentMethodsInput,
    ctx: CallerContext = Depends(get_caller_context),
    runtime: RuntimeContainer = Depends(get_runtime),
    session: AsyncSession = Depends(get_db_session),
) -> list[PaymentMethodOutput]:
    return await list_payment_methods_tool(
        payload, ctx=ctx, authorizer=runtime.authorizer, session=session
    )
