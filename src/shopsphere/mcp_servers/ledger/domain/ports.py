from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID


class LedgerRepository(Protocol):
    async def post_refund_entry(self, refund_id: UUID) -> UUID: ...

    async def get_customer_balance(self, customer_id: UUID) -> Decimal: ...
