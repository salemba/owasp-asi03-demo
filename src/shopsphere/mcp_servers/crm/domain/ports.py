from __future__ import annotations

from typing import Protocol
from uuid import UUID

from shopsphere.common.persistence.models import CRMSupportTicketORM, CustomerORM, RefundORM


class CRMRepository(Protocol):
    async def get_customer(self, customer_id: UUID) -> CustomerORM | None: ...

    async def create_ticket(
        self, customer_id: UUID, subject: str, body: str
    ) -> CRMSupportTicketORM: ...

    async def get_refund_history(self, customer_id: UUID) -> list[RefundORM]: ...
