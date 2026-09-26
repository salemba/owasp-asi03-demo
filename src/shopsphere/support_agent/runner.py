from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import httpx

from shopsphere.common.a2a import A2AMessage, A2AUntrustedClaims
from shopsphere.common.llm.protocol import LLMProvider
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.crm.tools import (
    GetCustomerInput,
    GetRefundHistoryInput,
    get_customer_tool,
    get_refund_history_tool,
)
from shopsphere.mcp_servers.orders.tools import (
    GetOrderInput,
    ListCustomerOrdersInput,
    get_order_tool,
    list_customer_orders_tool,
)


class SupportAgentRunner:
    def __init__(
        self,
        *,
        llm_provider: LLMProvider,
        settlement_agent_url: str = "http://localhost:8002",
        vuln_profile: bool = True,
    ) -> None:
        self.llm_provider = llm_provider
        self.settlement_agent_url = settlement_agent_url.rstrip("/")
        self.vuln_profile = vuln_profile

    async def handle_turn(
        self,
        prompt: str,
        *,
        ctx: CallerContext,
        session: Any,
        authorizer: Any,
    ) -> str:
        # Build actor chain for this step
        chain = list(ctx.actor_chain)
        if not chain or chain[-1] != "support_agent":
            chain.append("support_agent")

        # ASI03-V2 Token passthrough check / context creation
        # In VULN_PROFILE, forwards current ctx (with potential supervisor roles/tokens)
        agent_ctx = CallerContext(
            subject=ctx.subject,
            roles=ctx.roles,
            actor_chain=chain,
            token_claims=dict(ctx.token_claims),
            tenant=ctx.tenant,
        )

        llm_resp = await self.llm_provider.generate(prompt)
        text = llm_resp.text

        # Check if LLM requested tools or delegation via JSON payload structure or script
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
                action = data.get("action")
                if action == "request_settlement":
                    claims_data = data.get("claims", {})
                    message = A2AMessage(
                        sender_agent="support_agent",
                        order_id=str(data["order_id"]),
                        amount=str(data["amount"]),
                        reason=str(data["reason"]),
                        destination_pm_id=str(data["destination_pm_id"]),
                        claims=A2AUntrustedClaims(
                            requested_by=claims_data.get("requested_by"),
                            approved=bool(claims_data.get("approved", False)),
                            approval_ref=claims_data.get("approval_ref"),
                        ),
                    )
                    return await self._delegate_to_settlement(message, ctx=agent_ctx)
                if action == "get_order":
                    order_res = await get_order_tool(
                        GetOrderInput(order_id=UUID(data["order_id"])),
                        ctx=agent_ctx,
                        authorizer=authorizer,
                        session=session,
                    )
                    return json.dumps(order_res.model_dump(mode="json") if order_res else None)
                if action == "list_customer_orders":
                    orders_res = await list_customer_orders_tool(
                        ListCustomerOrdersInput(customer_id=UUID(data["customer_id"])),
                        ctx=agent_ctx,
                        authorizer=authorizer,
                        session=session,
                    )
                    return json.dumps([r.model_dump(mode="json") for r in orders_res])
                if action == "get_customer":
                    cust_res = await get_customer_tool(
                        GetCustomerInput(customer_id=UUID(data["customer_id"])),
                        ctx=agent_ctx,
                        authorizer=authorizer,
                        session=session,
                    )
                    return json.dumps(cust_res.model_dump(mode="json") if cust_res else None)
                if action == "get_refund_history":
                    refunds_res = await get_refund_history_tool(
                        GetRefundHistoryInput(customer_id=UUID(data["customer_id"])),
                        ctx=agent_ctx,
                        authorizer=authorizer,
                        session=session,
                    )
                    return json.dumps([r.model_dump(mode="json") for r in refunds_res])
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        return text

    async def _delegate_to_settlement(
        self,
        message: A2AMessage,
        *,
        ctx: CallerContext,
    ) -> str:
        headers = {
            "X-Subject": ctx.subject,
            "X-Roles": ",".join(ctx.roles),
            "X-Actor-Chain": json.dumps(ctx.actor_chain),
            "X-Tenant": ctx.tenant,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.settlement_agent_url}/a2a/settlement",
                json=message.model_dump(mode="json"),
                headers=headers,
            )
            return resp.text
