# 🛡️ AEGIS Core: The Tool-Execution Firewall for FinTech AI Agents

**Cloud HTTP Gateways (like LangSmith) protect your LLM tokens. AEGIS protects your Stripe account and Crypto Wallets from asynchronous Agent Double-Spending.**

## 🚨 The 1,000-Thread Double Spend Vulnerability

When an autonomous agent enters a hyper-cognitive loop, it can fire hundreds of concurrent tool calls (e.g., Stripe API charges or Web3 transactions).

Cloud-based guardrails suffer from network latency (~50ms - 150ms). By the time the cloud gateway registers the budget depletion, the in-flight transactions have already drained your accounts.

**[ 🎥 INSERT_YOUR_1000_THREAD_GIF_HERE.gif ]**
*(Above: AEGIS Local IPC locking 999 rogue concurrent Stripe charges in <1ms, preventing a $99,900 phantom debt).*

## ⚡ Why AEGIS? (Zero-Latency Policy Enforcement)

AEGIS is a horizontal **L3 Policy Gate** designed purely for speed and state locking. It sits exactly between your Agent's reasoning engine and your execution tools.

* **Sub-Millisecond Concurrency:** High-Frequency Local IPC Memory Locks (`< 1ms`) budget resolution.
* **Infrastructure Agnostic:** Works with LangChain, AutoGen, CrewAI, or raw Python scripts.
* **Zero Dependencies:** No Redis, no Kafka. Pure Python in-memory atomic locks.

## 📦 Quickstart & Installation

```bash
pip install aegis-core-lortuarte-sdk
```

## 🛠️ Proof of Concept: The 3-Line Integration

Wrap your high-risk tools (payments, trades, database writes) with the AEGIS gate.

```python
from aegis import PolicyGate

# 1. Initialize local IPC Client
aegis_gate = PolicyGate(daily_budget_usd=100)

def execute_agent_payment(agent_id, amount):
    # 2. Intercept budget spending BEFORE tool execution (<1ms Lock)
    decision = aegis_gate.evaluate_tool_execution(
        agent_id=agent_id, 
        operation="stripe_charge", 
        amount=amount
    )
    
    if decision["status"] == "ALLOW":
        # Safe to execute real API call
        # stripe.Charge.create(...)
        return "Transaction Authorized"
    else:
        # Loop blocked instantly. Budget saved.
        return f"BLOCKED: Asynchronous Double-Spend Prevented in {decision['latency']}ms"
```

## 🧠 The Architecture (vs. LLM Gateways)

| Feature | LangSmith / Portkey (Cloud) | AEGIS Core (Local IPC) | 
| :--- | :--- | :--- | 
| **Primary Target** | Token Spend / Prompt Injection | Tool Execution / Money Spend | 
| **Latency** | 50ms - 200ms (HTTP) | **< 1ms (In-Memory)** | 
| **Double-Spend Protection** | Fails under high concurrency | **Atomic deterministic locking** | 

**Built for the Machine-to-Machine (M2M) Economy.**
