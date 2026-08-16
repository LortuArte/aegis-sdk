# 🛡️ AEGIS Core

### Execution-Boundary Authorization & Atomic L3 Settlement for AI Agents

**Enforce before execution. Verify before settlement.**

AEGIS is a security and economic-control layer for high-risk AI-agent tool calls — combining atomic budget enforcement, replay-safe authorization, deterministic receipts, SHA-256 action references, Ed25519 signatures, and an isolated atomic L3 settlement layer.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-3.1.0-blue)](https://pypi.org/project/aegis-core-lortuarte-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-Beta-orange)](#️-current-scope--limitations)
[![Security](https://img.shields.io/badge/security-adversarially_tested-success)](#-security-evidence)
[![L3](https://img.shields.io/badge/L3-7%2F7_PASS-success)](#️-atomic-l3-settlement)

```bash
pip install aegis-core-lortuarte-sdk
```

---

# 🚨 The Problem

Autonomous AI agents can initiate payments, purchases, trades, API actions, and other irreversible tool calls concurrently.

A policy decision made too far away from execution can leave room for:

```text
                 AI AGENT
                    │
                    ▼
               TOOL INTENT
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
       CALL #1   CALL #2   CALL #N
          │         │         │
          └─────────┼─────────┘
                    │
                    ▼
          CONCURRENT STATE RACE
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
   DUPLICATE EXECUTION    OVERSPEND
```

AEGIS moves the authorization boundary directly in front of tool execution.

```text
                  AI AGENT
                     │
                     ▼
                 TOOL INTENT
                     │
                     ▼
          ┌─────────────────────┐
          │      🛡️ AEGIS       │
          │  AUTHORIZATION GATE │
          └──────────┬──────────┘
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
            ALLOW          DENY
              │             │
              ▼             ▼
        EXECUTE TOOL      🛑 BLOCK
```

> **The protected tool executes only after an explicit ALLOW decision.**

---

# ⚡ What AEGIS Does

AEGIS Core 3.1.0 focuses on the economic and authorization boundary between an autonomous agent and a high-risk external action.

### 🔒 Atomic Budget Enforcement

Concurrent mutations of the process-local ledger are serialized by a lock.

### 🔁 Replay-Safe Idempotency

An exact replay of the same authorization returns the historical receipt without consuming the budget again.

Reuse of the same transaction identity with conflicting economic data is denied.

### 🔗 Tool-Call Cryptographic Binding

`tool_call_id` participates in the authorization identity used to derive the signed action reference.

Changing the tool-call identity changes the resulting `action_ref`.

### 🔑 Signed Authorization Receipts

AEGIS produces deterministic authorization payloads protected by:

```text
Deterministic Payload
        │
        ▼
      SHA-256
        │
        ▼
      Ed25519
        │
        ▼
Signed Authorization Receipt
```

### 🧪 Tamper Detection

Changing signed authorization data invalidates cryptographic verification.

### 🛑 Fail-Closed Behavior

Internal authorization failures deny execution.

An explicitly configured invalid Ed25519 private key aborts startup rather than silently replacing the configured cryptographic identity.

### 💰 Decimal Monetary Accounting

Economic state uses Python `Decimal` rather than binary floating-point arithmetic.

### 🏦 Atomic L3 Settlement

An isolated settlement layer consumes signed AEGIS authorizations and performs atomic buyer → seller balance transitions using SQLite transactions.

---

# 📦 Installation

```bash
pip install aegis-core-lortuarte-sdk
```

Requirements:

```text
Python >= 3.8
cryptography
```

`cryptography` is installed automatically by the package.

---

# 🚀 Quickstart

```python
from decimal import Decimal
from aegis import AegisLocalPolicyGate

gate = AegisLocalPolicyGate()

agent_id = "agent-demo-001"

gate.ledger_data[agent_id] = Decimal("10.00")

receipt = gate.evaluar_gasto(
    agent_did=agent_id,
    operation="stripe_charge",
    tool_call_id="payment-001",
    amount_usd="3.00",
)

if receipt["policy_decision"] == "allow":
    print("AUTHORIZED")
    # Execute the protected tool here.
else:
    print("BLOCKED")

print(receipt)
```

Expected authorization:

```text
AUTHORIZED
```

Economic transition:

```text
$10.00
   │
   │ request $3.00
   ▼
 ALLOW
   │
   ▼
$7.00
```

---

# 🛡️ Enforcement Boundary

Assume the remaining budget is:

```text
$7.00
```

The agent attempts:

```text
$20.00
```

AEGIS evaluates the action before external execution:

```text
             $7.00 AVAILABLE
                    │
                    │ REQUEST $20.00
                    ▼
             ┌─────────────┐
             │    DENY     │
             └──────┬──────┘
                    │
                    ▼
            budget_exhausted
                    │
                    ▼
            🛑 TOOL BLOCKED
```

Integration pattern:

```python
receipt = gate.evaluar_gasto(
    agent_did=agent_id,
    operation="stripe_charge",
    tool_call_id="payment-002",
    amount_usd="20.00",
)

if receipt["policy_decision"] == "allow":
    result = execute_payment()
else:
    result = "BLOCKED"
```

The integration layer remains responsible for ensuring the external tool is invoked only after `allow`.

---

# 🔁 Idempotency & Replay Protection

AEGIS identifies an authorization using the agent and tool-call identity.

First request:

```text
tool_call_id: payment-001
amount:       $3.00

        │
        ▼
      ALLOW
        │
        ├── budget decreases once
        ├── cached: False
        └── signed receipt created
```

Exact replay:

```text
tool_call_id: payment-001
amount:       $3.00

        │
        ▼
   HISTORICAL RECEIPT
        │
        ├── same action_ref
        ├── cached: True
        └── NO second debit
```

Conflicting replay:

```text
SAME TRANSACTION ID
        │
        ├── original amount: $1.00
        └── new amount:    $100.00
                    │
                    ▼
                  DENY
                    │
                    ▼
          idempotency_conflict
```

Validated:

```text
Exact replay does not double-debit       PASS
Same ID + different amount blocked       PASS
Same ID + different operation blocked    PASS
```

---

# 🔐 Cryptographic Authorization

AEGIS signs deterministic authorization semantics rather than an unstructured success flag.

```text
            POLICY EVALUATION
                    │
                    ▼
         DETERMINISTIC PAYLOAD
                    │
                    ├── agent_did
                    ├── operation
                    ├── amount
                    ├── decision
                    └── tool-call binding
                    │
                    ▼
                 SHA-256
                    │
                    ▼
                 Ed25519
                    │
                    ▼
          SIGNED POLICY RECEIPT
                    │
                    ▼
              action_ref
```

Example receipt:

```python
{
    "agent_did": "agent-demo-001",
    "operation": "stripe_charge",
    "amount_usd": "3.00",
    "policy_decision": "allow",
    "policy_attenuations": [],
    "policy_signature": "ed25519:...",
    "action_ref": "...",
    "cached": False
}
```

`action_ref` is represented as the 64-character hexadecimal encoding of a 32-byte SHA-256 digest.

```text
SHA-256 digest     32 bytes
        │
        ▼
action_ref         64 hexadecimal characters
```

---

# 🧪 Tamper Detection

Original signed authorization:

```text
ORIGINAL PAYLOAD
      │
      ├── SHA-256
      │
      └── Ed25519
             │
             ▼
           VALID ✓
```

Modify signed data:

```text
MODIFIED PAYLOAD
      │
      ├── different digest
      │
      └── original signature
             │
             ▼
          INVALID ✗
```

Validated:

```text
Signature verification             PASS
Tampered authorization rejected    PASS
```

---

# 🛑 Fail-Closed Security

AEGIS is designed to prefer denial over silent authorization when the protected authorization path fails.

```text
          INTERNAL FAILURE
                 │
                 ▼
              🛑 DENY
                 │
                 ▼
        TOOL MUST NOT EXECUTE
```

Validated forced cryptographic failure:

```text
BALANCE BEFORE:       10.00
DECISION:             deny
BALANCE AFTER:        10.00
BALANCE PRESERVED:    True
FAIL-CLOSED:          True
ROLLBACK:             PASS
```

Configured invalid-key behavior:

```text
CONSTRUCTOR EXCEPTION: ValueError
GATE CREATED:          False

FAIL-CLOSED STARTUP:   True
EMERGENCY RECOVERY:    False
SECURITY MODEL:        INVALID KEY REJECTED

RESULT: PASS
```

This prevents an invalid configured cryptographic identity from being silently replaced at startup.

---

# 💰 Financial-Loss Adversarial Matrix

AEGIS was exercised against a focused matrix of economic failure scenarios.

| Scenario | Result |
|:---|:---:|
| Exact replay does not double-debit | ✅ PASS |
| Same ID + different amount blocked | ✅ PASS |
| Same ID + different operation blocked | ✅ PASS |
| Signature failure preserves balance | ✅ PASS |
| Over-budget request blocked without mutation | ✅ PASS |
| Exact-balance authorization | ✅ PASS |
| Zero / negative / non-numeric fail closed | ✅ PASS |
| Excess monetary precision rejected | ✅ PASS |
| DENY does not execute tool | ✅ PASS |
| Signed authorization verifies | ✅ PASS |
| Tampered receipt rejected | ✅ PASS |
| `tool_call_id` changes `action_ref` | ✅ PASS |

```text
TOTAL TESTS: 12
PASS:        12
FAIL:        0

FINAL RESULT: PASS
```

---

# 🧵 Concurrent Double-Spend Protection

A 1,000-request adversarial contention test was executed against a budget capable of funding only one request.

Configuration:

```text
REQUESTS:         1,000
WORKERS:          100
INITIAL BALANCE:  $10.00
AMOUNT EACH:      $10.00
```

Result:

```text
                 $10 AVAILABLE
                       │
          1,000 COMPETING REQUESTS
                       │
                       ▼
                  AEGIS LOCK
                       │
               ┌───────┴───────┐
               │               │
               ▼               ▼
          1 × ALLOW       999 × DENY
               │
               ▼
          $10 AUTHORIZED
               │
               ▼
         FINAL BALANCE $0
```

Measured result:

| Property | Result |
|:---|---:|
| Allow | **1** |
| Deny | **999** |
| Authorized total | **$10.00** |
| Final balance | **$0.00** |
| Overspend | **NO** |
| Result | **PASS** |

This demonstrates concurrent budget protection **inside the current process-local execution model**.

It does not demonstrate cross-process or distributed consensus.

---

# 🏦 Atomic L3 Settlement

AEGIS includes an isolated L3 settlement layer that consumes a signed authorization before mutating settlement balances.

```text
              AI AGENT
                  │
                  ▼
        AEGIS AUTHORIZATION
                  │
          SHA-256 + Ed25519
                  │
                  ▼
        SIGNED POLICY RECEIPT
                  │
                  ▼
      ┌──────────────────────┐
      │   L3 VERIFICATION    │
      │                      │
      │ ✓ decision = allow   │
      │ ✓ payload rebuilt    │
      │ ✓ action_ref         │
      │ ✓ Ed25519 signature  │
      └──────────┬───────────┘
                 │
                 ▼
          BEGIN IMMEDIATE
                 │
          ┌──────┴──────┐
          │             │
          ▼             ▼
      DEBIT BUYER   CREDIT SELLER
          │             │
          └──────┬──────┘
                 │
                 ▼
       SETTLEMENT RECORD
                 │
                 ▼
               COMMIT
```

If settlement fails after the transaction begins:

```text
FAILURE
   │
   ▼
ROLLBACK
   │
   ▼
BALANCES PRESERVED
```

Validated L3 security matrix:

| L3 Property | Result |
|:---|:---:|
| Signed settlement | ✅ PASS |
| Conservation of value | ✅ PASS |
| Exact replay idempotent | ✅ PASS |
| Tampered seller blocked | ✅ PASS |
| Tampered amount blocked | ✅ PASS |
| Atomic rollback | ✅ PASS |
| Concurrent limited-budget settlement | ✅ PASS |

Concurrent L3 test:

```text
REQUESTS: 100

SETTLED: 1
DENIED:  99

TOTAL: 7
PASS:  7
FAIL:  0

FINAL RESULT: PASS
```

---

# ⚡ Measured Performance

Performance is reported by **execution layer**.

AEGIS does not use a single latency number to represent different workloads.

## Local Benchmark Environment

The following results were measured locally during the current validation run using `time.perf_counter_ns()`.

They are local process measurements and must not be interpreted as Internet or hosted API round-trip latency.

### 1️⃣ Economic Decision Primitive

Isolates local:

```text
lock
+
Decimal comparison
+
Decimal subtraction
+
quantization
```

| Metric | Measured |
|:---|---:|
| Minimum | 0.400 µs |
| **Median** | **0.500 µs** |
| P95 | 1.000 µs |
| P99 | 1.300 µs |

```text
MEDIAN = 0.000500 ms
```

### 2️⃣ Idempotency Cache Hit

| Metric | Measured |
|:---|---:|
| Minimum | 2.200 µs |
| **Median** | **2.400 µs** |
| P95 | 4.900 µs |
| P99 | 7.700 µs |

```text
MEDIAN = 0.002400 ms
```

### 3️⃣ Full Signed Authorization

Includes the complete local authorization path measured by the benchmark:

```text
validation
    │
    ▼
lock
    │
    ▼
idempotency
    │
    ▼
budget decision
    │
    ▼
deterministic payload
    │
    ▼
SHA-256
    │
    ▼
Ed25519
    │
    ▼
receipt
```

| Metric | Measured |
|:---|---:|
| Minimum | 45.200 µs |
| **Median** | **47.900 µs** |
| Mean | 57.363 µs |
| P95 | 81.600 µs |
| P99 | 153.900 µs |

```text
MEDIAN = 0.047900 ms
```

### 4️⃣ L3 SQLite In-Memory Settlement

Signed receipt verification + SQLite transactional settlement using `:memory:`.

| Metric | Measured |
|:---|---:|
| Minimum | 133.400 µs |
| **Median** | **146.550 µs** |
| P95 | 245.900 µs |
| P99 | 393.200 µs |

```text
MEDIAN = 0.146550 ms
```

### 5️⃣ L3 Local File-Backed SQLite

Signed receipt verification + local file-backed SQLite transaction.

| Metric | Measured |
|:---|---:|
| Minimum | 486.600 µs |
| **Median** | **969.200 µs** |
| Mean | 1.022 ms |
| P95 | 1.621 ms |
| P99 | 2.188 ms |

```text
MEDIAN = 0.969200 ms
```

> File-backed SQLite results include the local persistence path, but should not be interpreted as guaranteed physical-disk latency for every operation because SQLite and the operating system may cache I/O.

---

# 📊 Performance Summary

| Layer | Median | P95 | P99 |
|:---|---:|---:|---:|
| ⚡ Economic decision primitive | **0.500 µs** | 1.000 µs | 1.300 µs |
| 🔁 Idempotency cache hit | **2.400 µs** | 4.900 µs | 7.700 µs |
| 🔐 Full signed authorization | **47.900 µs** | 81.600 µs | 153.900 µs |
| 🏦 L3 SQLite `:memory:` | **146.550 µs** | 245.900 µs | 393.200 µs |
| 💾 L3 local file-backed SQLite | **969.200 µs** | 1.621 ms | 2.188 ms |

### Relative measured cost

```text
SIGNED / DECISION:       95.80×
FILE L3 / MEMORY L3:      6.61×
L3 MEMORY / SIGNED:       3.06×
```

---

# 🔬 Why the Latency Numbers Are Separated

A previous single latency number can hide which work is actually being measured.

AEGIS therefore reports the layers independently:

```text
0.500 µs
DECISION PRIMITIVE
      │
      ▼
2.400 µs
IDEMPOTENCY CACHE HIT
      │
      ▼
47.900 µs
FULL SIGNED AUTHORIZATION
      │
      ▼
146.550 µs
L3 SQLITE :MEMORY:
      │
      ▼
969.200 µs
LOCAL FILE-BACKED SQLITE
```

These numbers answer different questions.

AEGIS therefore does **not** present `0.005 ms` as a full L3 or end-to-end settlement latency claim.

The current evidence supports low-microsecond local hot paths and a sub-millisecond median for the tested local signed and SQLite settlement paths described above.

---

# 🧯 Benchmark Contamination Checks

The final evidence benchmark also isolates common measurement contamination.

### Print overhead

Measured write to `os.devnull`:

```text
NO-PRINT MEDIAN:        0.200 µs
PRINT MEDIAN:           2.400 µs
ADDED MEDIAN COST:      2.200 µs
```

### Intentional `sleep(0.001)`

```text
REQUESTED SLEEP:        1.000 ms
OBSERVED MEDIAN:        1.696 ms
P95:                    1.941 ms
P99:                    2.251 ms
```

Therefore intentional sleeps and console/debug work are kept conceptually separate from engine latency claims.

---

# 🚫 What These Benchmarks Do NOT Measure

The current benchmark does **not** measure:

```text
✗ Client → Internet → Render → client HTTP round-trip

✗ Multi-process coordination

✗ Multi-worker shared-state coordination

✗ Multi-node distributed consensus

✗ Remote Redis coordination

✗ Remote PostgreSQL coordination

✗ Stripe settlement latency

✗ Blockchain settlement latency
```

No number for those layers is inferred from the local benchmark.

```text
LOCAL ENGINE PERFORMANCE
          ≠
NETWORK ROUND-TRIP
          ≠
DISTRIBUTED CONSENSUS
          ≠
EXTERNAL FINANCIAL SETTLEMENT
```

---

# 🧪 Security Evidence

Current focused evidence:

```text
┌───────────────────────────────────────────────┐
│              AEGIS SECURITY                  │
├───────────────────────────────────────────────┤
│ Cryptographic rollback                 PASS  │
│ Idempotency conflict                   PASS  │
│ tool_call_id binding                   PASS  │
│ Invalid configured key                 PASS  │
│ Fail-closed startup                    PASS  │
│ Ed25519 verification                   PASS  │
│ Tamper detection                       PASS  │
│ DENY → tool not executed               PASS  │
│ Decimal boundary handling              PASS  │
│ Financial-loss matrix            12/12 PASS  │
│ 1,000-request double-spend             PASS  │
│ L3 settlement matrix               7/7 PASS  │
└───────────────────────────────────────────────┘
```

This evidence is intended to be reproducible from the repository rather than accepted as a marketing claim.

---

# 🧰 Reproduce the Evidence

Core integration:

```bash
python test_integration.py
```

Enforcement:

```bash
python test_enforcement.py
```

Concurrent budget protection:

```bash
python test_concurrency.py
```

Cryptographic rollback:

```bash
python test_signature_failure_rollback.py
```

Idempotency conflict:

```bash
python test_idempotency_conflict.py
```

Tool-call cryptographic binding:

```bash
python test_tool_call_binding.py
```

Configured-key fail-closed behavior:

```bash
python test_key_failure_behavior.py
```

Financial-loss adversarial matrix:

```bash
python test_financial_loss_matrix.py
```

1,000-request double-spend test:

```bash
python test_double_spend_1000.py
```

L3 settlement security:

```bash
python test_l3_settlement.py
```

Final layered performance evidence:

```bash
python benchmark_final_evidence.py
```

Expected high-level security status:

```text
CORE SECURITY              PASS
FINANCIAL MATRIX      12/12 PASS
DOUBLE-SPEND               PASS
L3 SECURITY            7/7 PASS
PERFORMANCE EVIDENCE   COMPLETE
```

---

# 🏗️ Current Architecture

```text
                         AI AGENT
                            │
                            ▼
                        TOOL INTENT
                            │
                            ▼
                ┌──────────────────────┐
                │   🛡️ AEGIS CORE     │
                │                      │
                │  Monetary Validation │
                │  Idempotency         │
                │  Atomic Lock         │
                │  Budget Enforcement  │
                └──────────┬───────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                  ALLOW          DENY
                    │             │
                    │             └──────────► 🛑 BLOCK
                    ▼
           DETERMINISTIC PAYLOAD
                    │
                    ▼
                 SHA-256
                    │
                    ▼
                 Ed25519
                    │
                    ▼
          SIGNED AUTHORIZATION
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
  PROTECTED TOOL        L3 SETTLEMENT
                              │
                              ▼
                    VERIFY AUTHORIZATION
                              │
                              ▼
                       BEGIN IMMEDIATE
                              │
                     ┌────────┴────────┐
                     │                 │
                     ▼                 ▼
                  DEBIT              CREDIT
                     │                 │
                     └────────┬────────┘
                              │
                              ▼
                            COMMIT
```

The authorization core and settlement layer are intentionally separated.

That separation makes it possible to benchmark, test, and reason about each boundary independently.

---

# 🔬 Current Security Model

AEGIS currently demonstrates these properties:

### 1. Enforce Before Execution

Authorization is produced before the integration invokes the protected external tool.

### 2. Atomic Process-Local Accounting

A lock protects local ledger mutation from concurrent access inside the current process.

### 3. Replay-Safe Authorization

Exact replay does not consume budget twice.

Conflicting reuse of transaction identity is denied.

### 4. Deterministic Authorization

Security-relevant authorization data is deterministically serialized before hashing and signing.

### 5. Cryptographic Verification

SHA-256 and Ed25519 allow downstream verification of authorization integrity.

### 6. Economic Rollback

Failures in protected authorization and settlement paths preserve economic state when the tested transaction must fail.

### 7. Atomic Local Settlement

The isolated L3 layer performs transactional buyer → seller mutation and records settlement atomically under the tested SQLite model.

---

# ⚠️ Current Scope & Limitations

**AEGIS Core 3.1.0 is Beta software.**

## Current tested scope

```text
✓ Process-local authorization
✓ Process-local locking
✓ Decimal monetary accounting
✓ Replay-safe idempotency
✓ Idempotency conflict detection
✓ Deterministic authorization receipts
✓ SHA-256 action references
✓ Ed25519 signatures
✓ tool_call_id cryptographic binding
✓ Fail-closed authorization behavior
✓ Invalid configured-key rejection
✓ Economic rollback
✓ Concurrent local budget enforcement
✓ Atomic SQLite L3 settlement
✓ L3 replay protection
✓ L3 tamper rejection
```

## Not currently claimed

```text
✗ Cross-process atomicity

✗ Shared state across multiple workers

✗ Multi-node consensus

✗ Distributed ledger coordination

✗ Redis-backed distributed locking

✗ PostgreSQL-backed distributed settlement

✗ Byzantine fault tolerance

✗ Blockchain finality

✗ Stripe settlement guarantees

✗ Internet-scale production readiness
```

These are separate production/distributed-system concerns and should not be inferred from the current local evidence.

---

# 🔭 Current vs Future Architecture

## Current

```text
Agent
  │
  ▼
AEGIS Core
  │
  ├── authorization
  ├── budget control
  ├── idempotency
  ├── SHA-256
  └── Ed25519
  │
  ▼
Signed Receipt
  │
  ▼
Local Atomic L3 Settlement
```

## Future / Distributed Direction

```text
                 MULTIPLE AGENTS
                       │
                       ▼
               DISTRIBUTED AEGIS
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     Shared State   Coordination   Persistence
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
             DISTRIBUTED SETTLEMENT
```

The distributed architecture is a direction, **not a claim about the current implementation**.

---

# 🎯 Current Position

AEGIS is not an LLM reasoning guardrail.

It operates at the execution boundary:

```text
              AGENT REASONING
                    │
                    ▼
                TOOL INTENT
                    │
                    ▼
              🛡️ AEGIS
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
    BUDGET      IDEMPOTENCY   CRYPTOGRAPHY
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
               ALLOW / DENY
                    │
              ┌─────┴─────┐
              │           │
              ▼           ▼
         TOOL EXECUTION   L3
                         SETTLEMENT
```

**The goal is narrow: make economically sensitive agent actions explicitly authorized, cryptographically verifiable, and testable before irreversible execution.**

---

# 📋 Evidence Status

```text
TESTED
   │
   ▼
 PASS
   │
   ▼
REPRODUCIBLE
   │
   ▼
DOCUMENTED
   │
   ▼
DEMO-READY
```

---

# 📦 Package

| | |
|:---|:---|
| **Distribution** | `aegis-core-lortuarte-sdk` |
| **Version** | `3.1.0` |
| **Python** | `>=3.8` |
| **Status** | Beta |
| **License** | MIT |

Install:

```bash
pip install aegis-core-lortuarte-sdk
```

---

# 📄 License

MIT License.