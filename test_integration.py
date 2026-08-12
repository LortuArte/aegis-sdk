import json
import time

from aegis import AegisLocalPolicyGate, AegisCryptoEngine


AGENT = "did:key:aegis_final_demo_agent"
OPERATION = "stripe_charge"
TOOL_CALL_ID = "boardy-integration-001"
AMOUNT = 1.00


def execute_payment_tool(decision):
    """Simulated payment tool. It must never execute when policy denies."""
    if decision["policy_decision"] != "allow":
        return "BLOCKED"

    return "PAYMENT_EXECUTED"


print()
print("=== AEGIS INTEGRATED SECURITY TEST ===")
print()

gate = AegisLocalPolicyGate()

# ----------------------------------------------------------------------
# 1. POLICY
# ----------------------------------------------------------------------

start = time.perf_counter_ns()

decision = gate.evaluar_gasto(
    agent_did=AGENT,
    operation=OPERATION,
    tool_call_id=TOOL_CALL_ID,
    amount_usd=AMOUNT,
)

policy_elapsed_ns = time.perf_counter_ns() - start

print("POLICY:", decision["policy_decision"])
print("POLICY LATENCY:", policy_elapsed_ns, "ns")

assert decision["policy_decision"] == "allow"


# ----------------------------------------------------------------------
# 2. IDEMPOTENCY
# ----------------------------------------------------------------------

second_decision = gate.evaluar_gasto(
    agent_did=AGENT,
    operation=OPERATION,
    tool_call_id=TOOL_CALL_ID,
    amount_usd=AMOUNT,
)

print("IDEMPOTENCY FIRST CACHED:", decision["cached"])
print("IDEMPOTENCY SECOND CACHED:", second_decision["cached"])

assert decision["cached"] is False
assert second_decision["cached"] is True


# ----------------------------------------------------------------------
# 3. DETERMINISTIC PAYLOAD
# ----------------------------------------------------------------------

payload = {
    "agent_did": decision["agent_did"],
    "operation": decision["operation"],
    "amount_usd": decision["amount_usd"],
    "policy_decision": decision["policy_decision"],
    "policy_attenuations": decision["policy_attenuations"],
}

payload_string = AegisCryptoEngine.generar_string_determinista(payload)

print("PAYLOAD:", payload_string)


# ----------------------------------------------------------------------
# 4. SHA-256
# ----------------------------------------------------------------------

hash_bytes = AegisCryptoEngine.calcular_sha256(payload_string)

print("SHA256:", hash_bytes.hex())


# ----------------------------------------------------------------------
# 5. ED25519 SIGNATURE
# ----------------------------------------------------------------------

signature = AegisCryptoEngine.firmar_hash(
    hash_bytes,
    gate.private_key,
)

print("ED25519:", signature[:35] + "...")


# ----------------------------------------------------------------------
# 6. POSITIVE VERIFICATION
# ----------------------------------------------------------------------

positive_verification = AegisCryptoEngine.verificar_firma(
    hash_bytes,
    signature,
    gate.public_key,
)

print("VERIFICATION POSITIVE:", positive_verification)

assert positive_verification is True


# ----------------------------------------------------------------------
# 7. PAYLOAD TAMPERING
# ----------------------------------------------------------------------

tampered_payload = dict(payload)
tampered_payload["amount_usd"] = "9999.00"

tampered_string = AegisCryptoEngine.generar_string_determinista(
    tampered_payload
)

tampered_hash = AegisCryptoEngine.calcular_sha256(
    tampered_string
)

negative_verification = AegisCryptoEngine.verificar_firma(
    tampered_hash,
    signature,
    gate.public_key,
)

print("VERIFICATION AFTER TAMPERING:", negative_verification)

assert negative_verification is False


# ----------------------------------------------------------------------
# 8. ENFORCEMENT → TOOL
# ----------------------------------------------------------------------

tool_calls = 0

tool_result = execute_payment_tool(decision)

if tool_result == "PAYMENT_EXECUTED":
    tool_calls += 1

print("ALLOW TOOL RESULT:", tool_result)

assert tool_result == "PAYMENT_EXECUTED"


# ----------------------------------------------------------------------
# 9. DENIED REQUEST → MUST NOT REACH TOOL
# ----------------------------------------------------------------------

deny_decision = gate.evaluar_gasto(
    agent_did=AGENT,
    operation=OPERATION,
    tool_call_id="boardy-denied-001",
    amount_usd=999.00,
)

deny_tool_result = execute_payment_tool(deny_decision)

if deny_tool_result == "PAYMENT_EXECUTED":
    tool_calls += 1

print("DENY POLICY:", deny_decision["policy_decision"])
print("DENY TOOL RESULT:", deny_tool_result)

assert deny_decision["policy_decision"] == "deny"
assert deny_tool_result == "BLOCKED"


# ----------------------------------------------------------------------
# 10. FINAL REPORT
# ----------------------------------------------------------------------

total_elapsed_ns = time.perf_counter_ns() - start

print()
print("=== AEGIS INTEGRATION REPORT ===")
print("POLICY:", "PASS")
print("IDEMPOTENCY:", "PASS")
print("DETERMINISTIC PAYLOAD:", "PASS")
print("SHA-256:", "PASS")
print("ED25519:", "PASS")
print("VERIFICATION POSITIVE:", "PASS")
print("TAMPER DETECTION:", "PASS")
print("ENFORCEMENT:", "PASS")
print("TOOL EXECUTION:", "PASS")
print("TOOL CALLS:", tool_calls)
print("FINAL BALANCE:", gate.ledger_data[AGENT])
print("POLICY LATENCY:", policy_elapsed_ns, "ns")
print("TOTAL TEST TIME:", total_elapsed_ns, "ns")
print()
print("RESULT: PASS")