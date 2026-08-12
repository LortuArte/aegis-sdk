# 🛡️ AEGIS Core

### Enterprise AI Agent Policy Firewall

**Enforce before execution.**

Local policy enforcement for high-risk AI agent tool calls — with atomic budget control, idempotency, deterministic receipts, SHA-256 action references, and Ed25519 signatures.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-3.1.0-blue)](https://pypi.org/project/aegis-core-lortuarte-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-Beta-orange)](#-current-scope--limitations)

```bash
pip install aegis-core-lortuarte-sdk
```

---

## 🚨 The Problem

Autonomous AI agents can issue multiple high-risk tool calls concurrently.

For payments, trades, purchases, or other irreversible operations, a race condition can allow duplicate or over-budget execution before external infrastructure reacts.

```text
Agent decides to spend
        │
        ├──── Tool Call #1
        ├──── Tool Call #2
        ├──── Tool Call #3
        └──── Tool Call #N

        ↓

Potential concurrent budget race
```

AEGIS moves policy enforcement directly in front of tool execution.

```text
                    ┌──────────────────────┐
AI Agent ──────────►│  🛡️ AEGIS POLICY    │
                    │        GATE          │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                  ALLOW                  DENY
                    │                     │
                    ▼                     ▼
             Execute Tool             🛑 BLOCK
```

> **The protected tool executes only after an ALLOW decision.**

---

# ⚡ Why AEGIS?

AEGIS Core 3.1.0 focuses on the execution boundary between an autonomous agent and a high-risk tool.

### 🔒 Atomic Budget Enforcement

Concurrent mutations of the process-local ledger are protected by a lock.

### 🔁 Idempotent Tool Calls

Replaying the same `agent_did + tool_call_id` returns the original authorization receipt instead of consuming the budget again.

### 🔑 Signed Authorization Receipts

Policy decisions generate deterministic payloads, SHA-256 action references, and Ed25519 signatures.

### 🧪 Tamper Detection

Changing signed policy data invalidates signature verification.

### 🛑 Fail-Closed

Internal policy-engine faults produce a DENY decision rather than silently authorizing execution.

### 💰 Decimal Accounting

Monetary state uses Python `Decimal` rather than binary floating-point arithmetic.

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

# Initialize the local policy gate
gate = AegisLocalPolicyGate()

agent_id = "agent-demo-001"

# Assign a local budget
gate.ledger_data[agent_id] = Decimal("10.00")

# Evaluate BEFORE executing the external tool
receipt = gate.evaluar_gasto(
    agent_did=agent_id,
    operation="stripe_charge",
    tool_call_id="payment-001",
    amount_usd="3.00",
)

if receipt["policy_decision"] == "allow":
    print("AUTHORIZED")
    # stripe.Charge.create(...)
else:
    print("BLOCKED")

print(receipt)
```

Expected decision:

```text
AUTHORIZED
```

Budget transition:

```text
$10.00
   │
   │  request: $3.00
   ▼
 ALLOW
   │
   ▼
$7.00 remaining
```

---

# 🛡️ Enforcement Example

Assume the remaining budget is:

```text
$7.00
```

The agent attempts:

```text
$20.00
```

AEGIS evaluates the operation before tool execution:

```text
$7.00 available
      │
      │ request $20.00
      ▼
┌──────────────┐
│     DENY     │
└──────┬───────┘
       │
       ▼
budget_exhausted
       │
       ▼
🛑 TOOL NOT EXECUTED
```

Example integration:

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

---

# 🔁 Idempotency / Replay Protection

AEGIS identifies a local transaction using:

```text
agent_did + tool_call_id
```

First request:

```text
tool_call_id: payment-001
amount:       $3.00

→ ALLOW
→ balance decreases once
→ cached: False
```

Replay of the same tool call:

```text
tool_call_id: payment-001
amount:       $3.00

→ same action_ref
→ same signed receipt
→ cached: True
→ balance DOES NOT decrease again
```

Validated behavior:

```text
FIRST CACHED:     False
SECOND CACHED:    True
SAME ACTION_REF:  True
```

---

# 🔐 Cryptographic Authorization

Every successfully evaluated policy operation produces an auditable receipt.

Pipeline:

```text
┌─────────────────────┐
│  Policy Evaluation  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Deterministic JSON  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       SHA-256       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Ed25519 Signature │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Auditable Receipt   │
└─────────────────────┘
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

The `action_ref` is the hexadecimal representation of the 32-byte SHA-256 digest:

```text
SHA-256 digest     = 32 bytes
action_ref         = 64 hexadecimal characters
```

---

# 🧪 Tamper Detection

AEGIS verifies the Ed25519 signature against the deterministic policy payload.

Validated test:

```text
ORIGINAL SIGNATURE VALID:   True

             ↓ modify payload

TAMPERED SIGNATURE VALID:   False
```

Conceptually:

```text
Original Payload
      │
      ├── SHA-256
      │
      └── Ed25519
             │
             ▼
           VALID ✓


Modified Payload
      │
      ├── different SHA-256
      │
      └── original signature
             │
             ▼
          INVALID ✗
```

---

# 🛑 Fail-Closed Behavior

If an internal exception occurs during the protected policy-evaluation path, AEGIS denies the operation.

Validated forced-fault result:

```text
POLICY DECISION: deny

ATTENUATION:
internal_engine_fault

SIGNATURE:
error_no_signature

ACTION_REF:
0000000000000000000000000000000000000000000000000000000000000000

FAIL-CLOSED PASS: True
```

The intended security behavior is:

```text
Internal Engine Fault
         │
         ▼
      🛑 DENY
         │
         ▼
External Tool Must Not Execute
```

---

# 🧵 Concurrent Budget Protection

A real contention test was executed against the process-local ledger.

Configuration:

```text
REQUESTS: 100
```

Result:

```text
ALLOW:          1
DENY:          99
FINAL BALANCE:  0.00
RESULT:         PASS
```

Visualized:

```text
                   $1 available
                        │
         ┌──────────────┼──────────────┐
         │              │              │
      Request        Request        Request ...
         │              │              │
         └──────────────┼──────────────┘
                        │
                    AEGIS LOCK
                        │
             ┌──────────┴──────────┐
             │                     │
          1 × ALLOW            99 × DENY
             │
             ▼
        FINAL = $0.00

        ZERO FINANCIAL DRIFT
```

This validates concurrent budget enforcement **within the current process-local model**.

---

# 📊 Concurrent Performance Benchmark

Latest validated local benchmark:

```text
REQUESTS: 1,000
WORKERS:  100
```

### Results

| Metric | Measured Result |
|:---|---:|
| ⚡ Minimum | **68.800 µs** |
| ⚡ Median | **212.350 µs** |
| Mean | 5.644 ms |
| P95 | 12.668 ms |
| P99 | 23.697 ms |
| Maximum | 35.497 ms |
| Throughput | **6,579.89 req/s** |
| Requests | 1,000 |
| Result | **PASS** |

### What this means

The measured **median policy evaluation was sub-millisecond** on the development machine.

AEGIS does **not** claim sub-millisecond P95 or P99 latency from this benchmark.

Tail latency increases under contention.

Performance varies with:

- CPU
- operating system
- Python runtime
- worker count
- workload
- contention level

Reproduce the benchmark:

```bash
python benchmark_concurrency_performance.py
```

---

# 🧪 Integrated Security Test

The end-to-end validation currently checks:

| Test | Result |
|:---|:---:|
| Policy evaluation | ✅ PASS |
| Idempotency | ✅ PASS |
| Deterministic payload | ✅ PASS |
| SHA-256 | ✅ PASS |
| Ed25519 | ✅ PASS |
| Signature verification | ✅ PASS |
| Tamper detection | ✅ PASS |
| Enforcement | ✅ PASS |
| Tool execution control | ✅ PASS |
| Concurrent budget protection | ✅ PASS |
| Clean wheel installation | ✅ PASS |

Run:

```bash
python test_integration.py
```

---

# 📦 Clean Package Verification

AEGIS Core 3.1.0 has also been validated from a newly built wheel inside a fresh virtual environment.

```text
SOURCE
   │
   ▼
BUILD
   │
   ▼
WHEEL 3.1.0
   │
   ▼
FRESH VIRTUAL ENVIRONMENT
   │
   ▼
pip install
   │
   ▼
site-packages
   │
   ▼
REAL POLICY EXECUTION
   │
   ▼
PASS
```

Validated clean-install result:

```text
PACKAGE VERSION:       3.1.0
DISTRIBUTION VERSION:  3.1.0
DECISION:              allow
BALANCE:               4.00
SIGNATURE:             True
ACTION_REF LENGTH:     64
CLEAN INSTALL TEST:    True
```

This confirms the validation is not dependent on importing the local development source tree.

---

# 🏗️ Architecture

```text
                    AI AGENT
                       │
                       │ tool intent
                       ▼
            ┌─────────────────────┐
            │ AEGIS LOCAL POLICY  │
            │        GATE         │
            └──────────┬──────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
         IDEMPOTENCY          LEDGER
              │                 │
              └────────┬────────┘
                       │
                       ▼
                  ATOMIC LOCK
                       │
                       ▼
               POLICY DECISION
                  │         │
               ALLOW       DENY
                  │         │
                  │         └────────► 🛑 BLOCK
                  │
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
          SIGNED POLICY RECEIPT
                  │
                  ▼
             PROTECTED TOOL
```

---

# 🔬 Security Model

AEGIS Core currently focuses on five properties:

### 1. Enforce Before Execution

The policy decision is produced before the integration invokes the protected external tool.

### 2. Atomic Process-Local Accounting

A lock protects ledger mutation from concurrent access inside the current process.

### 3. Idempotent Execution Decisions

Repeated transaction identifiers return the historical receipt instead of consuming budget twice.

### 4. Deterministic Authorization

Policy-relevant data is deterministically serialized before hashing.

### 5. Cryptographic Verification

SHA-256 and Ed25519 allow downstream verification of the generated policy receipt.

---

# ⚠️ Current Scope & Limitations

**AEGIS Core 3.1.0 is Beta software.**

The current implementation provides:

```text
✓ Process-local enforcement
✓ Process-local locking
✓ In-memory ledger
✓ Decimal monetary accounting
✓ Idempotency
✓ Deterministic receipts
✓ SHA-256 action references
✓ Ed25519 signatures
✓ Fail-closed policy behavior
```

It does **not currently claim**:

```text
✗ Cross-process atomicity
✗ Distributed consensus
✗ Durable ledger persistence
✗ Multi-node coordination
```

The integration layer is responsible for ensuring that protected tools execute **only after an `allow` decision**.

Persistent state and distributed coordination are separate production-layer concerns.

---

# 🧰 Validation Scripts

Focused technical validation included in the repository:

```text
test_integration.py
test_concurrency.py
test_enforcement.py
benchmark_concurrency_performance.py
```

Examples:

```bash
python test_integration.py
python test_concurrency.py
python test_enforcement.py
python benchmark_concurrency_performance.py
```

---

# 🎯 Current Position

```text
Agent Reasoning
      │
      ▼
Tool Intent
      │
      ▼
🛡️ AEGIS
      │
      ├── Budget
      ├── Idempotency
      ├── Atomicity
      ├── Determinism
      ├── SHA-256
      ├── Ed25519
      └── Fail-Closed
      │
      ▼
ALLOW / DENY
      │
      ▼
Real-World Tool Execution
```

**AEGIS is not an LLM reasoning guardrail.**

It is an execution-boundary policy layer designed to make high-risk agent actions explicitly authorized before execution.

---

# 📋 Package

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