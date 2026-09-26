from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.attacks.helpers import assert_exploit_succeeds, seed_test_ledger_accounts

from shopsphere.common.a2a import A2AMessage
from shopsphere.common.llm.mock_provider import MockProvider
from shopsphere.common.persistence.models import (
    CustomerORM,
    CustomerTier,
    OrderORM,
    OrderStatus,
    PaymentMethodORM,
    PaymentMethodType,
)
from shopsphere.common.security import CallerContext, PermissiveAuthorizer
from shopsphere.settlement_agent.runner import SettlementAgentRunner


@pytest.mark.asyncio
@pytest.mark.integration
async def test_e2e_happy_path_refund(db_session: AsyncSession) -> None:
    """Happy-path integration test for refund flow."""
    await seed_test_ledger_accounts(db_session)
    authorizer = PermissiveAuthorizer()
    mock_provider = MockProvider()

    bob_id = uuid4()
    order_id = uuid4()
    bob_pm_id = uuid4()

    db_session.add(
        CustomerORM(
            id=bob_id,
            email="bob_happy@example.com",
            full_name="Bob Legitimate",
            tier=CustomerTier.BRONZE,
        )
    )
    db_session.add(
        OrderORM(
            id=order_id,
            customer_id=bob_id,
            status=OrderStatus.DELIVERED_DAMAGED,
            total=Decimal("95.00"),
            currency="EUR",
            placed_at=datetime.now(UTC) - timedelta(days=2),
            delivered_at=datetime.now(UTC) - timedelta(days=1),
        )
    )
    db_session.add(
        PaymentMethodORM(
            id=bob_pm_id,
            customer_id=bob_id,
            type=PaymentMethodType.CARD,
            masked_ref="4111****1111",
            is_active=True,
        )
    )
    await db_session.commit()

    ctx = CallerContext(
        subject=str(bob_id),
        roles=["customer"],
        actor_chain=["gateway", "support_agent"],
    )

    message = A2AMessage(
        sender_agent="support_agent",
        order_id=str(order_id),
        amount="95.00",
        reason="Damaged item upon delivery",
        destination_pm_id=str(bob_pm_id),
    )

    runner = SettlementAgentRunner(llm_provider=mock_provider, vuln_profile=True)
    res = await runner.process_a2a_request(
        message, ctx=ctx, session=db_session, authorizer=authorizer
    )

    assert "APPROVED" in res
    assert "executed" in res
    assert "journal" in res

    # Verify audit event for payments:request_refund
    await assert_exploit_succeeds(
        db_session,
        expected_action="payments:request_refund",
        expected_resource_contains=str(order_id),
    )

    # Verify audit event for ledger:post_refund_entry
    await assert_exploit_succeeds(
        db_session,
        expected_action="ledger:post_refund_entry",
        expected_resource_contains="journal",
    )
