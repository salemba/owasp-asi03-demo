from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import (
    JournalEntryORM,
    LedgerAccountORM,
    LedgerSide,
    PostingORM,
    RefundORM,
)
from shopsphere.mcp_servers.ledger.domain.ports import LedgerRepository


def is_balanced_postings(debit_amount: Decimal, credit_amount: Decimal) -> bool:
    return debit_amount == credit_amount


class SqlLedgerRepository(LedgerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def post_refund_entry(self, refund_id: UUID) -> UUID:
        refund = await self._session.get(RefundORM, refund_id)
        if refund is None:
            raise ValueError("refund not found")

        accounts_stmt = select(LedgerAccountORM).where(
            LedgerAccountORM.code.in_(["CASH", "REFUND_LIABILITY"])
        )
        accounts_result = await self._session.execute(accounts_stmt)
        accounts = {account.code: account for account in accounts_result.scalars().all()}
        if "CASH" not in accounts or "REFUND_LIABILITY" not in accounts:
            raise ValueError("required ledger accounts are missing")

        entry_id = uuid4()
        self._session.add(
            JournalEntryORM(
                id=entry_id, reference_id=refund.id, description=f"Refund journal for {refund.id}"
            )
        )

        debit_amount = refund.amount
        credit_amount = refund.amount
        if not is_balanced_postings(debit_amount, credit_amount):
            raise ValueError("double-entry invariant violated")

        self._session.add_all(
            [
                PostingORM(
                    id=uuid4(),
                    entry_id=entry_id,
                    account_id=accounts["REFUND_LIABILITY"].id,
                    customer_id=refund.customer_id,
                    side=LedgerSide.DEBIT,
                    amount=debit_amount,
                    currency=refund.currency,
                ),
                PostingORM(
                    id=uuid4(),
                    entry_id=entry_id,
                    account_id=accounts["CASH"].id,
                    customer_id=refund.customer_id,
                    side=LedgerSide.CREDIT,
                    amount=credit_amount,
                    currency=refund.currency,
                ),
            ]
        )
        await self._session.flush()
        return entry_id

    async def get_customer_balance(self, customer_id: UUID) -> Decimal:
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (PostingORM.side == LedgerSide.DEBIT, PostingORM.amount),
                        else_=-PostingORM.amount,
                    )
                ),
                0,
            )
        ).where(PostingORM.customer_id == customer_id)
        result = await self._session.execute(stmt)
        return Decimal(result.scalar_one())
