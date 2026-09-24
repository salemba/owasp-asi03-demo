from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import PaymentMethodORM, RefundORM, RefundStatus
from shopsphere.mcp_servers.payments.domain.ports import PaymentsRepository


class SqlPaymentsRepository(PaymentsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def request_refund(
        self,
        *,
        order_id: UUID,
        customer_id: UUID,
        amount: str,
        currency: str,
        destination_payment_method_id: UUID,
        idempotency_key: str,
        requested_by: str,
    ) -> RefundORM:
        existing_stmt = select(RefundORM).where(RefundORM.idempotency_key == idempotency_key)
        existing_result = await self._session.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            return existing

        refund = RefundORM(
            id=uuid4(),
            order_id=order_id,
            customer_id=customer_id,
            amount=Decimal(amount),
            currency=currency,
            destination_payment_method_id=destination_payment_method_id,
            status=RefundStatus.PENDING,
            idempotency_key=idempotency_key,
            requested_by=requested_by,
        )
        self._session.add(refund)
        await self._session.flush()
        return refund

    async def list_payment_methods(self, customer_id: UUID) -> list[PaymentMethodORM]:
        stmt = (
            select(PaymentMethodORM)
            .where(PaymentMethodORM.customer_id == customer_id)
            .order_by(PaymentMethodORM.masked_ref.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
