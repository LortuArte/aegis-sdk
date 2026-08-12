from decimal import Decimal
from aegis import AegisLocalPolicyGate
from aegis.aegis_sdk import AegisCryptoEngine

print("\n=== AEGIS SIGNATURE FAILURE / ROLLBACK TEST ===")

gate = AegisLocalPolicyGate()

AGENT_ID = "agent-rollback-test"
INITIAL_BALANCE = Decimal("10.00")

gate.ledger_data[AGENT_ID] = INITIAL_BALANCE
balance_before = gate.ledger_data[AGENT_ID]

print("BALANCE BEFORE:", balance_before)

original_sign = AegisCryptoEngine.firmar_hash

def forced_signing_failure(*args, **kwargs):
    raise RuntimeError("FORCED_SIGNING_FAILURE")

AegisCryptoEngine.firmar_hash = staticmethod(forced_signing_failure)

try:
    result = gate.evaluar_gasto(
        agent_did=AGENT_ID,
        operation="rollback_test",
        tool_call_id="rollback-001",
        amount_usd="3.00",
    )

    print("DECISION:", result.get("policy_decision"))
    print("ATTENUATIONS:", result.get("policy_attenuations"))

except Exception as exc:
    result = None
    print("UNHANDLED EXCEPTION:", type(exc).__name__, str(exc))

finally:
    AegisCryptoEngine.firmar_hash = original_sign

balance_after = gate.ledger_data[AGENT_ID]

print("BALANCE AFTER:", balance_after)

balance_preserved = balance_after == balance_before
print("BALANCE PRESERVED:", balance_preserved)

fail_closed = (
    result is not None
    and result.get("policy_decision") == "deny"
)

print("FAIL-CLOSED:", fail_closed)

rollback_pass = fail_closed and balance_preserved
print("ROLLBACK PASS:", rollback_pass)

if rollback_pass:
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")
