from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.ledger.tools import (
    GetCustomerBalanceInput,
    PostRefundEntryInput,
    get_customer_balance_tool,
    post_refund_entry_tool,
)


def build_mcp_server(runtime: RuntimeContainer) -> MCPServer:
    server = MCPServer("shopsphere-ledger")

    @server.tool(description="Post refund journal entries into the ledger.")
    async def post_refund_entry(
        refund_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object] | None:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await post_refund_entry_tool(
                PostRefundEntryInput(refund_id=refund_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json") if result else None

    @server.tool(description="Get customer net ledger balance.")
    async def get_customer_balance(
        customer_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object]:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await get_customer_balance_tool(
                GetCustomerBalanceInput(customer_id=customer_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json")

    return server
