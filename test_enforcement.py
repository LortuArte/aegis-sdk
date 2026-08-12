from aegis import AegisLocalPolicyGate

tool_calls = []

def fake_payment_tool(agent_id, amount):
    tool_calls.append({
        "agent_id": agent_id,
        "amount": amount
    })
    return "PAYMENT_EXECUTED"


gate = AegisLocalPolicyGate()

agent = "did:key:aegis_final_demo_agent"

# ============================================================
# TEST 1 — ALLOW debe llegar a la herramienta
# ============================================================

decision_allow = gate.evaluar_gasto(
    agent,
    "stripe_charge",
    "enforcement-allow-001",
    5.00
)

if decision_allow["policy_decision"] == "allow":
    result_allow = fake_payment_tool(agent, 5.00)
else:
    result_allow = "BLOCKED"


# ============================================================
# TEST 2 — DENY NO debe llegar a la herramienta
# ============================================================

decision_deny = gate.evaluar_gasto(
    agent,
    "stripe_charge",
    "enforcement-deny-001",
    999.00
)

if decision_deny["policy_decision"] == "allow":
    result_deny = fake_payment_tool(agent, 999.00)
else:
    result_deny = "BLOCKED"


# ============================================================
# VERIFICACIÓN
# ============================================================

print("=== AEGIS POLICY → ENFORCEMENT → TOOL TEST ===")

print("ALLOW DECISION:", decision_allow["policy_decision"])
print("ALLOW TOOL RESULT:", result_allow)

print("DENY DECISION:", decision_deny["policy_decision"])
print("DENY TOOL RESULT:", result_deny)

print("TOTAL TOOL CALLS:", len(tool_calls))

allow_ok = (
    decision_allow["policy_decision"] == "allow"
    and result_allow == "PAYMENT_EXECUTED"
)

deny_ok = (
    decision_deny["policy_decision"] == "deny"
    and result_deny == "BLOCKED"
)

if allow_ok and deny_ok and len(tool_calls) == 1:
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")