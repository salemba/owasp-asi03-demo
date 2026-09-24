from __future__ import annotations

from decimal import Decimal

import pytest

from shopsphere.mcp_servers.ledger.adapters.repositories import is_balanced_postings


@pytest.mark.unit
def test_balanced_postings_invariant_true_when_equal() -> None:
    assert is_balanced_postings(Decimal("5.00"), Decimal("5.00"))


@pytest.mark.unit
def test_balanced_postings_invariant_false_when_different() -> None:
    assert not is_balanced_postings(Decimal("5.00"), Decimal("4.99"))
