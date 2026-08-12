from decimal import Decimal
from aegis import AegisLocalPolicyGate


print("\n=== AEGIS IDEMPOTENCY CONFLICT TEST ===")

gate = AegisLocalPolicyGate()

AGENT_ID = "agent-idempotency-conflict"
TOOL_CALL_ID = "payment-conflict-001"

gate.ledger_data[AGENT_ID] = Decimal("10.00")

print("INITIAL BALANCE:", gate.ledger_data[AGENT_ID])


first = gate.evaluar_gasto(
    agent_did=AGENT_ID,
    operation="payment",
    tool_call_id=TOOL_CALL_ID,
    amount_usd="1.00",
)

print("\nFIRST REQUEST")
print("AMOUNT:", first["amount_usd"])
print("DECISION:", first["policy_decision"])
print("CACHED:", first["cached"])
print("BALANCE:", gate.ledger_data[AGENT_ID])


second = gate.evaluar_gasto(
    agent_did=AGENT_ID,
    operation="payment",
    tool_call_id=TOOL_CALL_ID,
    amount_usd="100.00",
)

print("\nSECOND REQUEST — SAME ID, DIFFERENT AMOUNT")
print("REQUESTED AMOUNT: 100.00")
print("RETURNED AMOUNT:", second["amount_usd"])
print("DECISION:", second["policy_decision"])
print("CACHED:", second["cached"])
print("ATTENUATIONS:", second["policy_attenuations"])
print("BALANCE:", gate.ledger_data[AGENT_ID])


conflict_detected = (
    second["policy_decision"] == "deny"
    and any(
        item.get("field") == "idempotency_conflict"
        and item.get("applied") is True
        for item in second["policy_attenuations"]
    )
)

print("\nCONFLICT DETECTED:", conflict_detected)

if conflict_detected:
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")