from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, DateTime, Enum, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from shopsphere.common.persistence.base import Base


class CustomerTier(StrEnum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class OrderStatus(StrEnum):
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    DELIVERED_DAMAGED = "DELIVERED_DAMAGED"
    LOST = "LOST"
    RETURNED = "RETURNED"


class PaymentMethodType(StrEnum):
    CARD = "CARD"
    IBAN = "IBAN"
    WALLET = "WALLET"


class RefundStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"


class LedgerSide(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class CustomerORM(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "crm"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    tier: Mapped[CustomerTier] = mapped_column(Enum(CustomerTier, name="customer_tier"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CRMSupportTicketORM(Base):
    __tablename__ = "support_tickets"
    __table_args__ = {"schema": "crm"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    subject: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OrderORM(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "orders"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, name="order_status"), index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OrderLineORM(Base):
    __tablename__ = "order_lines"
    __table_args__ = {"schema": "orders"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    sku: Mapped[str] = mapped_column(String(64))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))


class PaymentMethodORM(Base):
    __tablename__ = "payment_methods"
    __table_args__ = {"schema": "payments"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    type: Mapped[PaymentMethodType] = mapped_column(
        Enum(PaymentMethodType, name="payment_method_type")
    )
    masked_ref: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(default=True)


class RefundORM(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_refunds_idempotency_key"),
        {"schema": "payments"},
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    destination_payment_method_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    status: Mapped[RefundStatus] = mapped_column(
        Enum(RefundStatus, name="refund_status"), index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128))
    requested_by: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LedgerAccountORM(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "ledger"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    currency: Mapped[str] = mapped_column(String(3))


class JournalEntryORM(Base):
    __tablename__ = "journal_entries"
    __table_args__ = {"schema": "ledger"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    reference_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostingORM(Base):
    __tablename__ = "postings"
    __table_args__ = {"schema": "ledger"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    entry_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    account_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    customer_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), index=True)
    side: Mapped[LedgerSide] = mapped_column(Enum(LedgerSide, name="ledger_side"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditEventORM(Base):
    __tablename__ = "audit_events"
    __table_args__ = {"schema": "audit"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor_subject: Mapped[str] = mapped_column(String(300))
    actor_chain: Mapped[list[str]] = mapped_column(JSON)
    action: Mapped[str] = mapped_column(String(200))
    resource: Mapped[str] = mapped_column(String(300))
    decision: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(300))
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
