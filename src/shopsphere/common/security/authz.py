from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from shopsphere.common.security.context import CallerContext


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str


class ContextBuilder(Protocol):
    def build_context(self, incoming_ctx: CallerContext, actor_id: str) -> CallerContext:
        """Build outgoing context for downstream call."""


class Authorizer(Protocol):
    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        """Evaluate whether the caller can perform action on resource."""


class AllowAllAuthorizer:
    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        # TODO(step-4): Replace with OPA-backed authorizer.
        _ = (ctx, action, resource)
        return Decision(allowed=True, reason="allow-all-step2")


class PermissiveAuthorizer:
    """Vulnerable authorizer used when VULN_PROFILE=true."""

    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        _ = (ctx, action, resource)
        return Decision(allowed=True, reason="permissive-vuln-profile")


class HardenedAuthorizer:
    """# TODO(remediation-branch) Hardened authorizer stub."""

    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        _ = (ctx, action, resource)
        return Decision(allowed=False, reason="remediation-stub-not-implemented")


class PassthroughContextBuilder:
    """Vulnerable context builder used when VULN_PROFILE=true.

    # ASI03-V2: Token/context passthrough forwards whatever caller context is present.
    """

    def build_context(self, incoming_ctx: CallerContext, actor_id: str) -> CallerContext:
        chain = list(incoming_ctx.actor_chain)
        if not chain or chain[-1] != actor_id:
            chain.append(actor_id)
        return CallerContext(
            subject=incoming_ctx.subject,
            roles=incoming_ctx.roles,
            actor_chain=chain,
            token_claims=dict(incoming_ctx.token_claims),
            tenant=incoming_ctx.tenant,
        )


class HardenedContextBuilder:
    """# TODO(remediation-branch) Hardened context builder stub."""

    def build_context(self, incoming_ctx: CallerContext, actor_id: str) -> CallerContext:
        _ = (incoming_ctx, actor_id)
        raise NotImplementedError("remediation-stub-not-implemented")
