"""Create step-2 persistence schema

Revision ID: 0001_initial_persistence
Revises:
Create Date: 2026-09-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_persistence"
down_revision = None
branch_labels = None
depends_on = None


customer_tier = sa.Enum("BRONZE", "SILVER", "GOLD", "PLATINUM", name="customer_tier")
order_status = sa.Enum(
    "PLACED",
    "SHIPPED",
    "DELIVERED",
    "DELIVERED_DAMAGED",
    "LOST",
    "RETURNED",
    name="order_status",
)
payment_method_type = sa.Enum("CARD", "IBAN", "WALLET", name="payment_method_type")
refund_status = sa.Enum("PENDING", "APPROVED", "EXECUTED", "REJECTED", name="refund_status")
ledger_side = sa.Enum("DEBIT", "CREDIT", name="ledger_side")


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS crm")
    op.execute("CREATE SCHEMA IF NOT EXISTS orders")
    op.execute("CREATE SCHEMA IF NOT EXISTS payments")
    op.execute("CREATE SCHEMA IF NOT EXISTS ledger")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("tier", customer_tier, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="crm",
    )
    op.create_table(
        "support_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="crm",
    )
    op.create_index(
        "ix_support_tickets_customer_id", "support_tickets", ["customer_id"], schema="crm"
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "placed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        schema="orders",
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"], schema="orders")
    op.create_index("ix_orders_status", "orders", ["status"], schema="orders")
    op.create_table(
        "order_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        schema="orders",
    )
    op.create_index("ix_order_lines_order_id", "order_lines", ["order_id"], schema="orders")

    op.create_table(
        "payment_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", payment_method_type, nullable=False),
        sa.Column("masked_ref", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="payments",
    )
    op.create_index(
        "ix_payment_methods_customer_id", "payment_methods", ["customer_id"], schema="payments"
    )
    op.create_table(
        "refunds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("destination_payment_method_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", refund_status, nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("requested_by", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("idempotency_key", name="uq_refunds_idempotency_key"),
        schema="payments",
    )
    op.create_index("ix_refunds_customer_id", "refunds", ["customer_id"], schema="payments")
    op.create_index("ix_refunds_order_id", "refunds", ["order_id"], schema="payments")
    op.create_index("ix_refunds_status", "refunds", ["status"], schema="payments")

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        schema="ledger",
    )
    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="ledger",
    )
    op.create_index(
        "ix_journal_entries_reference_id", "journal_entries", ["reference_id"], schema="ledger"
    )
    op.create_table(
        "postings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("side", ledger_side, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="ledger",
    )
    op.create_index("ix_postings_account_id", "postings", ["account_id"], schema="ledger")
    op.create_index("ix_postings_customer_id", "postings", ["customer_id"], schema="ledger")
    op.create_index("ix_postings_entry_id", "postings", ["entry_id"], schema="ledger")

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("actor_subject", sa.String(length=300), nullable=False),
        sa.Column("actor_chain", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("action", sa.String(length=200), nullable=False),
        sa.Column("resource", sa.String(length=300), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=True),
        schema="audit",
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION ledger.prevent_postings_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'ledger.postings is append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_postings_no_update
        BEFORE UPDATE ON ledger.postings
        FOR EACH ROW EXECUTE FUNCTION ledger.prevent_postings_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_postings_no_delete
        BEFORE DELETE ON ledger.postings
        FOR EACH ROW EXECUTE FUNCTION ledger.prevent_postings_mutation();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit.prevent_audit_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit.audit_events is append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_events_no_update
        BEFORE UPDATE ON audit.audit_events
        FOR EACH ROW EXECUTE FUNCTION audit.prevent_audit_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_events_no_delete
        BEFORE DELETE ON audit.audit_events
        FOR EACH ROW EXECUTE FUNCTION audit.prevent_audit_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_no_delete ON audit.audit_events")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_no_update ON audit.audit_events")
    op.execute("DROP FUNCTION IF EXISTS audit.prevent_audit_mutation")

    op.execute("DROP TRIGGER IF EXISTS trg_postings_no_delete ON ledger.postings")
    op.execute("DROP TRIGGER IF EXISTS trg_postings_no_update ON ledger.postings")
    op.execute("DROP FUNCTION IF EXISTS ledger.prevent_postings_mutation")

    op.drop_table("audit_events", schema="audit")

    op.drop_index("ix_postings_entry_id", table_name="postings", schema="ledger")
    op.drop_index("ix_postings_customer_id", table_name="postings", schema="ledger")
    op.drop_index("ix_postings_account_id", table_name="postings", schema="ledger")
    op.drop_table("postings", schema="ledger")

    op.drop_index("ix_journal_entries_reference_id", table_name="journal_entries", schema="ledger")
    op.drop_table("journal_entries", schema="ledger")
    op.drop_table("accounts", schema="ledger")

    op.drop_index("ix_refunds_status", table_name="refunds", schema="payments")
    op.drop_index("ix_refunds_order_id", table_name="refunds", schema="payments")
    op.drop_index("ix_refunds_customer_id", table_name="refunds", schema="payments")
    op.drop_table("refunds", schema="payments")
    op.drop_index("ix_payment_methods_customer_id", table_name="payment_methods", schema="payments")
    op.drop_table("payment_methods", schema="payments")

    op.drop_index("ix_order_lines_order_id", table_name="order_lines", schema="orders")
    op.drop_table("order_lines", schema="orders")
    op.drop_index("ix_orders_status", table_name="orders", schema="orders")
    op.drop_index("ix_orders_customer_id", table_name="orders", schema="orders")
    op.drop_table("orders", schema="orders")

    op.drop_index("ix_support_tickets_customer_id", table_name="support_tickets", schema="crm")
    op.drop_table("support_tickets", schema="crm")
    op.drop_table("customers", schema="crm")

