from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: UUID = Field(default_factory=uuid4)
    email: str
    full_name: str


class OrderLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)


class Order(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    lines: list[OrderLine]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PaymentMethod(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method_id: UUID = Field(default_factory=uuid4)
    provider: str
    token_reference: str


class RefundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)
    reason: str


class RefundDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    approved: bool
    policy_reference: str | None = None


class LedgerEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: UUID = Field(default_factory=uuid4)
    account: str
    side: Literal["debit", "credit"]
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: UUID = Field(default_factory=uuid4)
    requested_by: str
    action_type: str
    reference_id: UUID
    details: dict[str, str] = Field(default_factory=dict)
