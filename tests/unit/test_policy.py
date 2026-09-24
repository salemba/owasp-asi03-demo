from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from shopsphere.common.domain.money import Money
from shopsphere.settlement_agent.domain.policy import (
    can_auto_approve_refund,
    is_amount_within_goodwill_quota,
    is_within_refund_window,
)


@pytest.mark.unit
def test_refund_window_allows_recent_delivery() -> None:
    delivered_at = datetime.now(UTC) - timedelta(days=10)
    assert is_within_refund_window(delivered_at=delivered_at)


@pytest.mark.unit
def test_refund_window_rejects_old_delivery() -> None:
    delivered_at = datetime.now(UTC) - timedelta(days=60)
    assert not is_within_refund_window(delivered_at=delivered_at)


@pytest.mark.unit
def test_goodwill_quota_check() -> None:
    requested = Money(amount=Decimal("30.00"), currency="EUR")
    used = Money(amount=Decimal("50.00"), currency="EUR")
    assert is_amount_within_goodwill_quota(requested=requested, used_quota=used)


@pytest.mark.unit
def test_auto_approval_requires_both_predicates() -> None:
    requested = Money(amount=Decimal("20.00"), currency="EUR")
    used = Money(amount=Decimal("10.00"), currency="EUR")
    delivered_at = datetime.now(UTC) - timedelta(days=4)
    assert can_auto_approve_refund(requested=requested, delivered_at=delivered_at, used_quota=used)
