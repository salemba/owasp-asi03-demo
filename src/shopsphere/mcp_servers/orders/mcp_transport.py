from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from shopsphere.common.runtime import RuntimeContainer
from shopsphere.common.security import CallerContext
from shopsphere.mcp_servers.orders.tools import (
    GetOrderInput,
    GetOrderStatusInput,
    ListCustomerOrdersInput,
    get_order_status_tool,
    get_order_tool,
    list_customer_orders_tool,
)


def build_mcp_server(runtime: RuntimeContainer) -> MCPServer:
    server = MCPServer("shopsphere-orders")

    @server.tool(description="Fetch full order details for an order id.")
    async def get_order(
        order_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object] | None:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await get_order_tool(
                GetOrderInput(order_id=order_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json") if result else None

    @server.tool(description="List all orders for a customer id.")
    async def list_customer_orders(
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
            results = await list_customer_orders_tool(
                ListCustomerOrdersInput(customer_id=customer_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return [item.model_dump(mode="json") for item in results]

    @server.tool(description="Get only order status for an order id.")
    async def get_order_status(
        order_id: str,
        subject: str,
        roles: list[str],
        actor_chain: list[str],
        tenant: str,
    ) -> dict[str, object]:
        ctx = CallerContext(
            subject=subject, roles=roles, actor_chain=actor_chain, token_claims={}, tenant=tenant
        )
        async with runtime.session_factory() as session:
            result = await get_order_status_tool(
                GetOrderStatusInput(order_id=order_id),
                ctx=ctx,
                authorizer=runtime.authorizer,
                session=session,
            )
            return result.model_dump(mode="json")

    return server
