from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.persistence.models import AuditEventORM
from shopsphere.common.security.authz import Decision
from shopsphere.common.security.context import CallerContext


async def write_audit_event(
    session: AsyncSession,
    *,
    ctx: CallerContext,
    action: str,
    resource: str,
    decision: Decision,
    trace_id: str | None,
    event_id: UUID | None = None,
) -> None:
    session.add(
        AuditEventORM(
            id=event_id or uuid4(),
            actor_subject=ctx.subject,
            actor_chain=ctx.actor_chain,
            action=action,
            resource=resource,
            decision="ALLOW" if decision.allowed else "DENY",
            reason=decision.reason,
            trace_id=trace_id,
        )
    )
