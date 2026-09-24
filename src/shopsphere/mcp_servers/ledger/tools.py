from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.audit import write_audit_event
from shopsphere.common.security import Authorizer, CallerContext
from shopsphere.mcp_servers.ledger.adapters.repositories import SqlLedgerRepository


class PostRefundEntryInput(BaseModel):
    refund_id: UUID


class PostRefundEntryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refund_id: UUID
    journal_entry_id: UUID


class GetCustomerBalanceInput(BaseModel):
    customer_id: UUID


class GetCustomerBalanceOutput(BaseModel):
    customer_id: UUID
    balance: Decimal


async def post_refund_entry_tool(
    payload: PostRefundEntryInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> PostRefundEntryOutput | None:
    """Post a balanced double-entry journal for an approved or executed refund."""
    decision = await authorizer.authorize(
        ctx, "ledger:post_refund_entry", f"refunds/{payload.refund_id}/journal"
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="ledger:post_refund_entry",
        resource=f"refunds/{payload.refund_id}/journal",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return None

    repository = SqlLedgerRepository(session)
    entry_id = await repository.post_refund_entry(payload.refund_id)
    await session.commit()
    return PostRefundEntryOutput(refund_id=payload.refund_id, journal_entry_id=entry_id)


async def get_customer_balance_tool(
    payload: GetCustomerBalanceInput,
    *,
    ctx: CallerContext,
    authorizer: Authorizer,
    session: AsyncSession,
) -> GetCustomerBalanceOutput:
    """Return the net customer balance from ledger postings."""
    decision = await authorizer.authorize(
        ctx,
        "ledger:get_customer_balance",
        f"customers/{payload.customer_id}/balance",
    )
    await write_audit_event(
        session,
        ctx=ctx,
        action="ledger:get_customer_balance",
        resource=f"customers/{payload.customer_id}/balance",
        decision=decision,
        trace_id=None,
    )
    if not decision.allowed:
        await session.commit()
        return GetCustomerBalanceOutput(customer_id=payload.customer_id, balance=Decimal("0.00"))

    repository = SqlLedgerRepository(session)
    balance = await repository.get_customer_balance(payload.customer_id)
    await session.commit()
    return GetCustomerBalanceOutput(customer_id=payload.customer_id, balance=balance)
