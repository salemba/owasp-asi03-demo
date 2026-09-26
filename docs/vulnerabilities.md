# OWASP ASI03 Vulnerabilities Reference

This document catalogs the deliberate vulnerability patterns (V1–V5) embedded in ShopSphere when `VULN_PROFILE=true`.

| ID | Title | Mechanism | Vulnerable Component | Attack Test | OWASP ASI03 Category |
|---|---|---|---|---|---|
| **V1** | Shared Service Identity | `settlement_agent` drops customer context and uses a single static `settlement_service` identity token for all downstream calls. | `settlement_agent/runner.py` | `test_attack_a5_shared_id_redirect` | ASI03-V1 Identity & Token Misuse |
| **V2** | Token Passthrough | `gateway`/`support_agent` forwards whatever bearer token/roles are in context, including cached escalation supervisor tokens. | `common/security/authz.py` (`PassthroughContextBuilder`), `support_agent/runner.py` | `test_attack_a3_token_passthrough` | ASI03-V2 Unchecked Context Passthrough |
| **V3** | Trusted Delegation Claims | `settlement_agent` trusts untrusted `A2AMessage.claims` (`requested_by`, `approved`, `approval_ref`) to bypass policy authorization thresholds. | `settlement_agent/runner.py` | `test_attack_a2_trusted_claims` | ASI03-V3 Unverified Agent-to-Agent Claims |
| **V4** | Missing Object-Level Authz (BOLA) | Refund endpoints accept any `order_id` without verifying that the order belongs to the authenticated caller/customer. | `settlement_agent/runner.py` | `test_attack_a1_cross_customer_refund` | ASI03-V4 Broken Object-Level Authorization |
| **V5** | No Cumulative Velocity Limit | Goodwill/refund limits per customer/quarter are not tracked or enforced across multiple requests. | `settlement_agent/runner.py` | `test_attack_a4_cumulative_limit_exfiltrated` | ASI03-V5 Unenforced Cumulative Limits |

---

## Vulnerability Details

### V1: Shared Service Identity
- **Description:** `settlement_agent` executes requests using a generic service identity (`settlement_service`), obscuring original customer lineage at the MCP boundary.
- **Remediation Stub:** `# TODO(remediation-branch)` in `settlement_agent/runner.py`.

### V2: Token Passthrough
- **Description:** The `PassthroughContextBuilder` blindly propagates elevated roles (e.g. `support_supervisor`) from previous context turns without re-authenticating the caller.
- **Remediation Stub:** `HardenedContextBuilder` in `shopsphere/common/security/authz.py`.

### V3: Trusted Delegation Claims
- **Description:** Unverified claim flags inside `A2AMessage.claims` are trusted as proof of supervisor approval without cryptographic verification or OPA authorization.
- **Remediation Stub:** `# TODO(remediation-branch)` in `settlement_agent/runner.py`.

### V4: Broken Object-Level Authorization (BOLA)
- **Description:** Customer A can issue a refund request against Customer B's order because object-to-subject ownership is not checked.
- **Remediation Stub:** `# TODO(remediation-branch)` in `settlement_agent/runner.py`.

### V5: No Cumulative Limit
- **Description:** Goodwill quota checks use `used_quota = 0.00` per request instead of querying total historical refunds for the quarter.
- **Remediation Stub:** `# TODO(remediation-branch)` in `settlement_agent/runner.py`.
