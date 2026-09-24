# Architecture

```mermaid
flowchart LR
  Customer((Customer)) --> Gateway[Gateway\nFastAPI]
  Gateway --> Support[Support Agent\nFastAPI]
  Support --> Settlement[Settlement Agent\nFastAPI]
  Settlement --> Finance[Finance Approval\nFastAPI]

  Support --> Orders[MCP Orders]
  Support --> CRM[MCP CRM]
  Settlement --> Payments[MCP Payments]
  Settlement --> Ledger[MCP Ledger]

  Gateway --> KC[Keycloak]
  Settlement --> OPA[OPA]
  Orders --> PG[(Postgres)]
  CRM --> PG
  Payments --> PG
  Ledger --> PG

  Gateway --> OTEL[OTel Collector]
  Support --> OTEL
  Settlement --> OTEL
  OTEL --> Jaeger[Jaeger]

  subgraph TrustBoundaryA[External Boundary]
    Customer
  end

  subgraph TrustBoundaryB[Platform Boundary]
    Gateway
    Support
    Settlement
    Finance
    Orders
    CRM
    Payments
    Ledger
    KC
    OPA
    PG
    OTEL
    Jaeger
  end
```

## Data Model

- Schemas are isolated by bounded context: `crm`, `orders`, `payments`, `ledger`, `audit`.
- Cross-schema references are by ID only (no cross-schema foreign keys).
- Monetary values use decimal columns and ISO-4217 currency codes.
- `ledger.postings` and `audit.audit_events` are append-only.

```mermaid
erDiagram
  CRM_CUSTOMERS {
    uuid id PK
    string email UK
    string full_name
    string tier
    timestamptz created_at
  }

  CRM_SUPPORT_TICKETS {
    uuid id PK
    uuid customer_id
    string subject
    text body
    timestamptz created_at
  }

  ORDERS_ORDERS {
    uuid id PK
    uuid customer_id
    string status
    decimal total
    string currency
    timestamptz placed_at
    timestamptz delivered_at
  }

  ORDERS_ORDER_LINES {
    uuid id PK
    uuid order_id
    string sku
    int quantity
    decimal unit_price
    string currency
  }

  PAYMENTS_PAYMENT_METHODS {
    uuid id PK
    uuid customer_id
    string type
    string masked_ref
    bool is_active
  }

  PAYMENTS_REFUNDS {
    uuid id PK
    uuid order_id
    uuid customer_id
    decimal amount
    string currency
    uuid destination_payment_method_id
    string status
    string idempotency_key UK
    string requested_by
    timestamptz created_at
  }

  LEDGER_ACCOUNTS {
    uuid id PK
    string code UK
    string name
    string currency
  }

  LEDGER_JOURNAL_ENTRIES {
    uuid id PK
    uuid reference_id
    string description
    timestamptz created_at
  }

  LEDGER_POSTINGS {
    uuid id PK
    uuid entry_id
    uuid account_id
    uuid customer_id
    string side
    decimal amount
    string currency
    timestamptz created_at
  }

  AUDIT_AUDIT_EVENTS {
    uuid id PK
    timestamptz timestamp
    string actor_subject
    jsonb actor_chain
    string action
    string resource
    string decision
    string reason
    string trace_id
  }

  CRM_CUSTOMERS ||--o{ CRM_SUPPORT_TICKETS : customer_id
  ORDERS_ORDERS ||--o{ ORDERS_ORDER_LINES : order_id
  PAYMENTS_PAYMENT_METHODS ||--o{ PAYMENTS_REFUNDS : destination_payment_method_id
  LEDGER_JOURNAL_ENTRIES ||--o{ LEDGER_POSTINGS : entry_id
  LEDGER_ACCOUNTS ||--o{ LEDGER_POSTINGS : account_id
```
