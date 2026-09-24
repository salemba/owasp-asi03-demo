from __future__ import annotations

from typing import Protocol
from uuid import UUID

from shopsphere.common.persistence.models import PaymentMethodORM, RefundORM


class PaymentsRepository(Protocol):
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
    ) -> RefundORM: ...

    async def list_payment_methods(self, customer_id: UUID) -> list[PaymentMethodORM]: ...
