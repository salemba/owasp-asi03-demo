# Threat Model

## System DFD

- **User / Customer:** Initiates request via API Gateway (`gateway`).
- **API Gateway (`gateway`):** Ingests requests, attaches `CallerContext`, routes to `support_agent`.
- **Support Agent (`support_agent`):** Manages dialog, calls CRM and Orders MCP tools, delegates to `settlement_agent` via A2A HTTP.
- **Settlement Agent (`settlement_agent`):** Ingests `A2AMessage`, checks policy, executes Payments and Ledger MCP tools.
- **MCP Servers (`crm`, `orders`, `payments`, `ledger`):** Perform data access and mutations, write audit logs.

## Assets

- Customer Funds & Refund Execution (`payments` MCP)
- Financial Ledger Invariants (`ledger` MCP)
- Order & Customer Records (`orders`, `crm` MCPs)
- Audit Logs (`audit_events` table)

## STRIDE Table

| Element | Spoofing | Tampering | Repudiation | Information Disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| A2A Delegation | V3: Untrusted claim flags in `A2AMessage` | V2: Forged caller context / passthrough tokens | Missing actor chain propagation | Exposure of customer IDs in A2A envelope | Rapid refund requests (V5) | V1: Service identity elevation |
| Settlement Agent | V1: Generic `settlement_service` subject | Bypassing goodwill limit via claims | Unaudited actor attribution | Cross-customer order reading (V4) | Velocity exhaustion (V5) | BOLA cross-customer refund (V4) |

## ASI03 Mapping

| Vulnerability ID | OWASP ASI03 Vector | Location | Attack Test |
|---|---|---|---|
| **V1** | Shared Service Identity | `settlement_agent/runner.py` | `tests/attacks/test_attacks.py::test_attack_a5_shared_id_redirect` |
| **V2** | Token Passthrough | `common/security/authz.py` | `tests/attacks/test_attacks.py::test_attack_a3_token_passthrough` |
| **V3** | Trusted Delegation Claims | `settlement_agent/runner.py` | `tests/attacks/test_attacks.py::test_attack_a2_trusted_claims` |
| **V4** | Missing Object-Level Authz (BOLA) | `settlement_agent/runner.py` | `tests/attacks/test_attacks.py::test_attack_a1_cross_customer_refund` |
| **V5** | No Cumulative Limit | `settlement_agent/runner.py` | `tests/attacks/test_attacks.py::test_attack_a4_cumulative_limit_exfiltrated` |

