from __future__ import annotations

from decimal import Decimal

from mcp.server.mcpserver import MCPServer

from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.payments.tools import (
    ListPaymentMethodsInput,
    RequestRefundInput,
    list_payment_methods_tool,
    request_refund_tool,
)


def build_mcp_server(runtime: RuntimeContainer) -> MCPServer:
    server = MCPServer("shopsphere-payments")

    @server.tool(description="Create an idempotent refund request for an order.")
    async def request_refund(  # noqa: PLR0917
        order_id: str,
        customer_id: str,
        amount: str,
        reason: str,
        destination_payment_method_id: str,
        idempotency_key: str,
        currency: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object] | None:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await request_refund_tool(
                RequestRefundInput(
                    order_id=order_id,
                    customer_id=customer_id,
                    amount=Decimal(amount),
                    reason=reason,
                    destination_payment_method_id=destination_payment_method_id,
                    idempotency_key=idempotency_key,
                    currency=currency,
                ),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json") if result else None

    @server.tool(description="List payment methods for a customer.")
    async def list_payment_methods(
        customer_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> list[dict[str, object]]:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await list_payment_methods_tool(
                ListPaymentMethodsInput(customer_id=customer_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return [item.model_dump(mode="json") for item in result]

    return server
