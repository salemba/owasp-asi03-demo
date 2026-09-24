from __future__ import annotations

from decimal import Decimal

import pytest

from shopsphere.common.domain.models import LedgerEntry, OrderLine


@pytest.mark.unit
def test_order_line_uses_decimal_prices() -> None:
    line = OrderLine(sku="sku-1", quantity=2, unit_price=Decimal("10.50"), currency="USD")
    assert isinstance(line.unit_price, Decimal)


@pytest.mark.unit
def test_ledger_entry_uses_decimal_amount() -> None:
    entry = LedgerEntry(account="refunds", side="debit", amount=Decimal("15.00"), currency="USD")
    assert isinstance(entry.amount, Decimal)
