from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.audit import write_audit_event
from shopsphere.common.security import Authorizer, CallerContext
from shopsphere.mcp_servers.payments.adapters.repositories import SqlPaymentsRepository


class RequestRefundInput(BaseModel):
    order_id: UUID
    customer_id: UUID
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)
    reason: str
    destination_payment_method_id: UUID
    idempotency_key: str


class RefundOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    order_id: UUID
    customer_id: UUID
    amount: Decimal
    currency: str
    destination_payment_method_id: UUID
    status: str
    requested_by: str
    created_at: datetime


class ListPaymentMethodsInput(BaseModel):
    customer_id: UUID


class PaymentMethodOutput(BaseModel):
    id: UUID
    customer_id: UUID
    type: str
    masked_ref: str
    is_active: bool


async def request_refund_tool(
    payload: RequestRefundInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> RefundOutput | None:
    """Create an idempotent refund request in pending state."""
    decision = await authorizer.authorize(
        ctx, "payments:request_refund", f"orders/{payload.order_id}/refunds"
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="payments:request_refund",
        resource=f"orders/{payload.order_id}/refunds",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return None

    repository = SqlPaymentsRepository(session)
    refund = await repository.request_refund(
        order_id=payload.order_id,
        customer_id=payload.customer_id,
        amount=str(payload.amount),
        currency=payload.currency.upper(),
        destination_payment_method_id=payload.destination_payment_method_id,
        idempotency_key=payload.idempotency_key,
        requested_by=ctx.subject,
    )
    await session.commit()
    return RefundOutput(
        id=refund.id,
        order_id=refund.order_id,
        customer_id=refund.customer_id,
        amount=refund.amount,
        currency=refund.currency,
        destination_payment_method_id=refund.destination_payment_method_id,
        status=refund.status.value,
        requested_by=refund.requested_by,
        created_at=refund.created_at,
    )


async def list_payment_methods_tool(
    payload: ListPaymentMethodsInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> list[PaymentMethodOutput]:
    """List saved payment methods for a customer."""
    decision = await authorizer.authorize(
        ctx,
        "payments:list_payment_methods",
        f"customers/{payload.customer_id}/payment-methods",
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="payments:list_payment_methods",
        resource=f"customers/{payload.customer_id}/payment-methods",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return []

    repository = SqlPaymentsRepository(session)
    methods = await repository.list_payment_methods(payload.customer_id)
    await session.commit()
    return [
        PaymentMethodOutput(
            id=method.id,
            customer_id=method.customer_id,
            type=method.type.value,
            masked_ref=method.masked_ref,
            is_active=method.is_active,
        )
        for method in methods
    ]
