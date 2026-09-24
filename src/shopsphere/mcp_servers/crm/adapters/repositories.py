from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import CRMSupportTicketORM, CustomerORM, RefundORM
from shopsphere.mcp_servers.crm.domain.ports import CRMRepository


class SqlCRMRepository(CRMRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_customer(self, customer_id: UUID) -> CustomerORM | None:
        return await self._session.get(CustomerORM, customer_id)

    async def create_ticket(
        self, customer_id: UUID, subject: str, body: str
    ) -> CRMSupportTicketORM:
        ticket = CRMSupportTicketORM(
            id=uuid4(), customer_id=customer_id, subject=subject, body=body
        )
        self._session.add(ticket)
        await self._session.flush()
        return ticket

    async def get_refund_history(self, customer_id: UUID) -> list[RefundORM]:
        stmt = (
            select(RefundORM)
            .where(RefundORM.customer_id == customer_id)
            .order_by(RefundORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
