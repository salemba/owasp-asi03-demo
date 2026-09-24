from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.crm.tools import (
    CreateTicketInput,
    GetCustomerInput,
    GetRefundHistoryInput,
    create_ticket_tool,
    get_customer_tool,
    get_refund_history_tool,
)


def build_mcp_server(runtime: RuntimeContainer) -> MCPServer:
    server = MCPServer("shopsphere-crm")

    @server.tool(description="Get a customer profile by customer id.")
    async def get_customer(
        customer_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object] | None:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await get_customer_tool(
                GetCustomerInput(customer_id=customer_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json") if result else None

    @server.tool(description="Create a support ticket for a customer.")
    async def create_ticket(  # noqa: PLR0917
        customer_id: str,
        subject_text: str,
        body: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object] | None:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await create_ticket_tool(
                CreateTicketInput(customer_id=customer_id, subject=subject_text, body=body),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json") if result else None

    @server.tool(description="Get refund history for one customer id.")
    async def get_refund_history(
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
            results = await get_refund_history_tool(
                GetRefundHistoryInput(customer_id=customer_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return [item.model_dump(mode="json") for item in results]

    return server
