from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import AuditEventORM, LedgerAccountORM
from shopsphere.common.seed import deterministic_uuid


async def seed_test_ledger_accounts(session: AsyncSession) -> None:
    """Ensure CASH and REFUND_LIABILITY ledger accounts exist in the test DB session."""
    cash_id = deterministic_uuid("ledger_account::cash")
    refund_liab_id = deterministic_uuid("ledger_account::refund_liability")

    cash_acc = await session.get(LedgerAccountORM, cash_id)
    if not cash_acc:
        session.add(
            LedgerAccountORM(
                id=cash_id,
                code="CASH",
                name="Cash",
                currency="EUR",
            )
        )

    refund_acc = await session.get(LedgerAccountORM, refund_liab_id)
    if not refund_acc:
        session.add(
            LedgerAccountORM(
                id=refund_liab_id,
                code="REFUND_LIABILITY",
                name="Refund Liability",
                currency="EUR",
            )
        )
    await session.commit()


async def assert_exploit_succeeds(
    session: AsyncSession,
    *,
    expected_action: str,
    expected_resource_contains: str,
    expected_actor_subject: str | None = None,
    expected_actor_chain: list[str] | None = None,
) -> AuditEventORM:
    """Assertion helper verifying that an exploit succeeded by checking audit trail."""
    stmt = select(AuditEventORM).where(
        AuditEventORM.action == expected_action,
        AuditEventORM.decision == "ALLOW",
    )
    result = await session.execute(stmt)
    events = result.scalars().all()

    matching_event: AuditEventORM | None = None
    for event in events:
        if expected_resource_contains in event.resource:
            if expected_actor_subject and event.actor_subject != expected_actor_subject:
                continue
            matching_event = event
            break

    assert matching_event is not None, (
        f"Exploit failed: No ALLOW audit event found for action='{expected_action}' "
        f"containing resource='{expected_resource_contains}'."
    )

    if expected_actor_chain is not None:
        assert matching_event.actor_chain == expected_actor_chain, (
            f"Actor chain mismatch: expected {expected_actor_chain}, "
            f"got {matching_event.actor_chain}"
        )

    return matching_event
