from __future__ import annotations

from decimal import Decimal

import pytest

from shopsphere.common.domain.money import Money


@pytest.mark.unit
def test_money_quantizes_to_two_decimals() -> None:
    money = Money(amount=Decimal("10.999"), currency="eur")
    assert money.amount == Decimal("11.00")
    assert money.currency == "EUR"


@pytest.mark.unit
def test_money_rejects_negative_values() -> None:
    with pytest.raises(ValueError):
        Money(amount=Decimal("-1.00"), currency="EUR")
