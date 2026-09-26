from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class A2AUntrustedClaims(BaseModel):
    model_config = ConfigDict(extra="allow")

    requested_by: str | None = None
    approved: bool = False
    approval_ref: str | None = None


class A2AMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sender_agent: str
    order_id: str
    amount: str
    reason: str
    destination_pm_id: str
    claims: A2AUntrustedClaims = Field(default_factory=A2AUntrustedClaims)
