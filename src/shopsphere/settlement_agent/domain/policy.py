from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from shopsphere.common.domain.money import Money

GOODWILL_LIMIT_EUR = Decimal("100.00")
MAX_REFUND_WINDOW_DAYS = 30


def is_within_refund_window(*, delivered_at: datetime | None, now: datetime | None = None) -> bool:
    if delivered_at is None:
        return False
    reference_now = now or datetime.now(UTC)
    if delivered_at.tzinfo is None:
        delivered_at = delivered_at.replace(tzinfo=UTC)
    if reference_now.tzinfo is None:
        reference_now = reference_now.replace(tzinfo=UTC)
    return reference_now - delivered_at <= timedelta(days=MAX_REFUND_WINDOW_DAYS)


def is_amount_within_goodwill_quota(*, requested: Money, used_quota: Money) -> bool:
    if requested.currency != "EUR" or used_quota.currency != "EUR":
        return False
    return used_quota.amount + requested.amount <= GOODWILL_LIMIT_EUR


def can_auto_approve_refund(
    *, requested: Money, delivered_at: datetime | None, used_quota: Money
) -> bool:
    return is_within_refund_window(delivered_at=delivered_at) and is_amount_within_goodwill_quota(
        requested=requested,
        used_quota=used_quota,
    )
