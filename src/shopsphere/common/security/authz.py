from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from shopsphere.common.security.context import CallerContext


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str


class Authorizer(Protocol):
    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        """Evaluate whether the caller can perform action on resource."""


class AllowAllAuthorizer:
    async def authorize(self, ctx: CallerContext, action: str, resource: str) -> Decision:
        # TODO(step-4): Replace with OPA-backed authorizer.
        _ = (ctx, action, resource)
        return Decision(allowed=True, reason="allow-all-step2")
