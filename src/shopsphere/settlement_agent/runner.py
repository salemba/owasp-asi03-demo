from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from shopsphere.common.a2a import A2AMessage
from shopsphere.common.domain.money import Money
from shopsphere.common.llm.protocol import LLMProvider
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.ledger.tools import PostRefundEntryInput, post_refund_entry_tool
from shopsphere.mcp_servers.orders.tools import GetOrderInput, get_order_tool
from shopsphere.mcp_servers.payments.tools import RequestRefundInput, request_refund_tool
from shopsphere.settlement_agent.domain.policy import can_auto_approve_refund


class SettlementAgentRunner:
    def __init__(
        self,
        *,
        llm_provider: LLMProvider,
        vuln_profile: bool = True,
    ) -> None:
        self.llm_provider = llm_provider
        self.vuln_profile = vuln_profile

    async def process_a2a_request(
        self,
        message: A2AMessage,
        *,
        ctx: CallerContext,
        session: Any,
        authorizer: Any,
    ) -> str:
        chain = list(ctx.actor_chain)
        if not chain or chain[-1] != "settlement_agent":
            chain.append("settlement_agent")

        # ASI03-V1 Shared service identity vs customer subject:
        # In VULN_PROFILE, settlement_agent uses static identity "settlement_service"
        # and drops the customer subject at the A2A boundary.
        if self.vuln_profile:
            effective_ctx = CallerContext(
                subject="settlement_service",
                roles=["service", "settlement"],
                actor_chain=chain,
                tenant=ctx.tenant,
            )
        else:
            # Hardened path stub (preserves caller subject)
            effective_ctx = CallerContext(
                subject=ctx.subject,
                roles=ctx.roles,
                actor_chain=chain,
                tenant=ctx.tenant,
            )

        # ASI03-V3 Trusted delegation claims:
        # Check if trusted claims in A2AMessage override authorization / approval policy
        claims = message.claims
        is_claims_approved = claims.approved and (claims.requested_by or claims.approval_ref)

        order_id = UUID(message.order_id)
        amount_dec = Decimal(message.amount)
        dest_pm_id = UUID(message.destination_pm_id)

        # Fetch order details to check customer and delivered_at
        order_summary = await get_order_tool(
            GetOrderInput(order_id=order_id),
            ctx=effective_ctx,
            authorizer=authorizer,
            session=session,
        )

        if not order_summary:
            return "ERROR: Order not found"

        # ASI03-V4 Missing object-level authz (BOLA):
        # In VULN_PROFILE, refund accepts order_id without verifying customer ownership!
        customer_id = order_summary.customer_id

        # Policy evaluation
        requested_money = Money(amount=amount_dec, currency="EUR")
        # ASI03-V5: cumulative limit not enforced in VULN
        used_quota = Money(amount=Decimal("0.00"), currency="EUR")

        approved = False
        if self.vuln_profile and is_claims_approved:
            # ASI03-V3: Trust claims blindly
            approved = True
        else:
            approved = can_auto_approve_refund(
                requested=requested_money,
                delivered_at=order_summary.delivered_at,
                used_quota=used_quota,
            )

        if not approved:
            return "REJECTED: Policy evaluation failed"

        # Execute refund tool (payments MCP)
        refund = await request_refund_tool(
            RequestRefundInput(
                order_id=order_id,
                customer_id=customer_id,
                amount=amount_dec,
                currency="EUR",
                reason=message.reason,
                destination_payment_method_id=dest_pm_id,
                idempotency_key=f"a2a-refund-{order_id}-{amount_dec}",
            ),
            ctx=effective_ctx,
            authorizer=authorizer,
            session=session,
        )

        if not refund:
            return "ERROR: Refund request failed"

        # Execute post_refund_entry tool (ledger MCP)
        entry = await post_refund_entry_tool(
            PostRefundEntryInput(refund_id=refund.id),
            ctx=effective_ctx,
            authorizer=authorizer,
            session=session,
        )

        if not entry:
            return "ERROR: Ledger entry failed"

        return f"APPROVED: Refund {refund.id} executed, journal {entry.journal_entry_id}"
