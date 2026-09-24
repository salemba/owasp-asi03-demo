from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.audit import write_audit_event
from shopsphere.common.security import Authorizer, CallerContext
from shopsphere.mcp_servers.crm.adapters.repositories import SqlCRMRepository


class CustomerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    email: str
    full_name: str
    tier: str
    created_at: datetime


class TicketOutput(BaseModel):
    id: UUID
    customer_id: UUID
    subject: str
    body: str
    created_at: datetime


class RefundHistoryItem(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    currency: str
    status: str
    created_at: datetime


class GetCustomerInput(BaseModel):
    customer_id: UUID


class CreateTicketInput(BaseModel):
    customer_id: UUID
    subject: str
    body: str


class GetRefundHistoryInput(BaseModel):
    customer_id: UUID


async def get_customer_tool(
    payload: GetCustomerInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> CustomerOutput | None:
    """Fetch a CRM customer profile by ID."""
    decision = await authorizer.authorize(
        ctx, "crm:get_customer", f"crm/customers/{payload.customer_id}"
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="crm:get_customer",
        resource=f"crm/customers/{payload.customer_id}",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return None

    repository = SqlCRMRepository(session)
    customer = await repository.get_customer(payload.customer_id)
    await session.commit()
    if customer is None:
        return None
    return CustomerOutput(
        id=customer.id,
        email=customer.email,
        full_name=customer.full_name,
        tier=customer.tier.value,
        created_at=customer.created_at,
    )


async def create_ticket_tool(
    payload: CreateTicketInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> TicketOutput | None:
    """Create a support ticket for a customer."""
    decision = await authorizer.authorize(
        ctx,
        "crm:create_ticket",
        f"crm/customers/{payload.customer_id}/tickets",
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="crm:create_ticket",
        resource=f"crm/customers/{payload.customer_id}/tickets",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return None

    repository = SqlCRMRepository(session)
    ticket = await repository.create_ticket(payload.customer_id, payload.subject, payload.body)
    await session.commit()
    return TicketOutput(
        id=ticket.id,
        customer_id=ticket.customer_id,
        subject=ticket.subject,
        body=ticket.body,
        created_at=ticket.created_at,
    )


async def get_refund_history_tool(
    payload: GetRefundHistoryInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> list[RefundHistoryItem]:
    """List historical refund records for a customer."""
    decision = await authorizer.authorize(
        ctx,
        "crm:get_refund_history",
        f"crm/customers/{payload.customer_id}/refunds",
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="crm:get_refund_history",
        resource=f"crm/customers/{payload.customer_id}/refunds",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return []

    repository = SqlCRMRepository(session)
    refunds = await repository.get_refund_history(payload.customer_id)
    await session.commit()
    return [
        RefundHistoryItem(
            id=refund.id,
            order_id=refund.order_id,
            amount=refund.amount,
            currency=refund.currency,
            status=refund.status.value,
            created_at=refund.created_at,
        )
        for refund in refunds
    ]
