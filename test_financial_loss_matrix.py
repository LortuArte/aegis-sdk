from decimal import Decimal
from copy import deepcopy

from aegis import AegisLocalPolicyGate
from aegis.aegis_sdk import AegisCryptoEngine


print("\n============================================================")
print("AEGIS FINANCIAL LOSS / AUTHORIZATION ADVERSARIAL MATRIX")
print("============================================================")


results = []


def record(name, passed, details=""):
    results.append((name, passed, details))

    print(f"\nTEST: {name}")
    print("RESULT:", "PASS" if passed else "FAIL")

    if details:
        print("DETAIL:", details)


# ============================================================
# TEST 1
# EXACT REPLAY MUST NOT DEBIT TWICE
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-replay-agent"
gate.ledger_data[agent] = Decimal("10.00")

first = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="replay-001",
    amount_usd="3.00",
)

balance_after_first = gate.ledger_data[agent]

second = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="replay-001",
    amount_usd="3.00",
)

balance_after_second = gate.ledger_data[agent]

passed = (
    first["policy_decision"] == "allow"
    and first["cached"] is False
    and second["policy_decision"] == "allow"
    and second["cached"] is True
    and balance_after_first == Decimal("7.00")
    and balance_after_second == Decimal("7.00")
)

record(
    "EXACT REPLAY DOES NOT DOUBLE-DEBIT",
    passed,
    (
        f"balance first={balance_after_first}, "
        f"balance replay={balance_after_second}"
    ),
)


# ============================================================
# TEST 2
# SAME ID + DIFFERENT AMOUNT MUST BE DENIED
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-amount-conflict"
gate.ledger_data[agent] = Decimal("10.00")

gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="conflict-amount-001",
    amount_usd="1.00",
)

balance_before_conflict = gate.ledger_data[agent]

conflict = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="conflict-amount-001",
    amount_usd="9.00",
)

balance_after_conflict = gate.ledger_data[agent]

passed = (
    conflict["policy_decision"] == "deny"
    and any(
        item.get("field") == "idempotency_conflict"
        for item in conflict["policy_attenuations"]
    )
    and balance_after_conflict == balance_before_conflict
)

record(
    "SAME ID + DIFFERENT AMOUNT BLOCKED",
    passed,
    (
        f"before={balance_before_conflict}, "
        f"after={balance_after_conflict}"
    ),
)


# ============================================================
# TEST 3
# SAME ID + DIFFERENT OPERATION MUST BE DENIED
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-operation-conflict"
gate.ledger_data[agent] = Decimal("10.00")

gate.evaluar_gasto(
    agent_did=agent,
    operation="stripe_charge",
    tool_call_id="conflict-operation-001",
    amount_usd="2.00",
)

balance_before_conflict = gate.ledger_data[agent]

conflict = gate.evaluar_gasto(
    agent_did=agent,
    operation="crypto_transfer",
    tool_call_id="conflict-operation-001",
    amount_usd="2.00",
)

balance_after_conflict = gate.ledger_data[agent]

passed = (
    conflict["policy_decision"] == "deny"
    and any(
        item.get("field") == "idempotency_conflict"
        for item in conflict["policy_attenuations"]
    )
    and balance_after_conflict == balance_before_conflict
)

record(
    "SAME ID + DIFFERENT OPERATION BLOCKED",
    passed,
    (
        f"before={balance_before_conflict}, "
        f"after={balance_after_conflict}"
    ),
)


# ============================================================
# TEST 4
# SIGNATURE FAILURE MUST NOT CONSUME MONEY
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-signature-failure"
gate.ledger_data[agent] = Decimal("10.00")

balance_before = gate.ledger_data[agent]

original_sign = AegisCryptoEngine.firmar_hash


def forced_sign_failure(*args, **kwargs):
    raise RuntimeError("FORCED_SIGNATURE_FAILURE")


AegisCryptoEngine.firmar_hash = staticmethod(
    forced_sign_failure
)

try:
    receipt = gate.evaluar_gasto(
        agent_did=agent,
        operation="payment",
        tool_call_id="signature-failure-001",
        amount_usd="4.00",
    )

finally:
    AegisCryptoEngine.firmar_hash = original_sign


balance_after = gate.ledger_data[agent]

passed = (
    receipt["policy_decision"] == "deny"
    and balance_after == balance_before
    and any(
        item.get("field") == "internal_engine_fault"
        for item in receipt["policy_attenuations"]
    )
)

record(
    "SIGNATURE FAILURE PRESERVES BALANCE",
    passed,
    f"before={balance_before}, after={balance_after}",
)


# ============================================================
# TEST 5
# OVER-BUDGET REQUEST MUST NOT MUTATE LEDGER
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-over-budget"
gate.ledger_data[agent] = Decimal("10.00")

receipt = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="over-budget-001",
    amount_usd="10.01",
)

balance_after = gate.ledger_data[agent]

passed = (
    receipt["policy_decision"] == "deny"
    and balance_after == Decimal("10.00")
    and any(
        item.get("field") == "budget_exhausted"
        for item in receipt["policy_attenuations"]
    )
)

record(
    "OVER-BUDGET REQUEST BLOCKED WITHOUT MUTATION",
    passed,
    f"final_balance={balance_after}",
)


# ============================================================
# TEST 6
# EXACT BALANCE MUST AUTHORIZE ONCE
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-exact-balance"
gate.ledger_data[agent] = Decimal("10.00")

receipt = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="exact-balance-001",
    amount_usd="10.00",
)

balance_after = gate.ledger_data[agent]

passed = (
    receipt["policy_decision"] == "allow"
    and balance_after == Decimal("0.00")
)

record(
    "EXACT BALANCE AUTHORIZATION",
    passed,
    f"final_balance={balance_after}",
)


# ============================================================
# TEST 7
# ZERO / NEGATIVE / NON-NUMERIC MUST FAIL CLOSED
# ============================================================

invalid_values = [
    "0.00",
    "-1.00",
    "abc",
]

all_invalid_passed = True

for index, invalid in enumerate(invalid_values):
    gate = AegisLocalPolicyGate()

    agent = f"matrix-invalid-{index}"
    gate.ledger_data[agent] = Decimal("10.00")

    receipt = gate.evaluar_gasto(
        agent_did=agent,
        operation="payment",
        tool_call_id=f"invalid-{index}",
        amount_usd=invalid,
    )

    if not (
        receipt["policy_decision"] == "deny"
        and gate.ledger_data[agent] == Decimal("10.00")
    ):
        all_invalid_passed = False


record(
    "ZERO / NEGATIVE / NON-NUMERIC FAIL CLOSED",
    all_invalid_passed,
)


# ============================================================
# TEST 8
# TOO MANY DECIMALS MUST BE REJECTED
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-precision"
gate.ledger_data[agent] = Decimal("10.00")

receipt = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="precision-001",
    amount_usd="1.0000001",
)

passed = (
    receipt["policy_decision"] == "deny"
    and gate.ledger_data[agent] == Decimal("10.00")
)

record(
    "EXCESS MONETARY PRECISION REJECTED",
    passed,
    f"final_balance={gate.ledger_data[agent]}",
)


# ============================================================
# TEST 9
# DENY MUST NEVER EXECUTE THE EXTERNAL TOOL
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-enforcement"
gate.ledger_data[agent] = Decimal("1.00")

tool_calls = []


def dangerous_payment_tool():
    tool_calls.append("EXECUTED")
    return "PAYMENT_EXECUTED"


receipt = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="enforcement-deny-001",
    amount_usd="5.00",
)

if receipt["policy_decision"] == "allow":
    dangerous_payment_tool()
else:
    tool_result = "BLOCKED"


passed = (
    receipt["policy_decision"] == "deny"
    and len(tool_calls) == 0
)

record(
    "DENY DOES NOT EXECUTE TOOL",
    passed,
    f"external_tool_calls={len(tool_calls)}",
)


# ============================================================
# TEST 10
# SIGNED RECEIPT MUST VERIFY
# ============================================================

gate = AegisLocalPolicyGate()

agent = "matrix-signature-positive"
gate.ledger_data[agent] = Decimal("10.00")

receipt = gate.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="signature-positive-001",
    amount_usd="1.00",
)

payload = {
    "agent_did": receipt["agent_did"],
    "operation": receipt["operation"],
    "tool_call_id": receipt["tool_call_id"],
    "amount_usd": receipt["amount_usd"],
    "policy_decision": receipt["policy_decision"],
    "policy_attenuations": receipt["policy_attenuations"],
}

deterministic = (
    AegisCryptoEngine.generar_string_determinista(
        payload
    )
)

hash_bytes = (
    AegisCryptoEngine.calcular_sha256(
        deterministic
    )
)

verification = (
    AegisCryptoEngine.verificar_firma(
        hash_bytes,
        receipt["policy_signature"],
        gate.public_key,
    )
)

passed = (
    receipt["policy_decision"] == "allow"
    and verification is True
    and receipt["action_ref"] == hash_bytes.hex()
)

record(
    "SIGNED AUTHORIZATION VERIFIES",
    passed,
    f"signature_valid={verification}",
)


# ============================================================
# TEST 11
# TAMPERED RECEIPT MUST FAIL VERIFICATION
# ============================================================

tampered_payload = deepcopy(payload)

tampered_payload["amount_usd"] = "9.00"

tampered_json = (
    AegisCryptoEngine.generar_string_determinista(
        tampered_payload
    )
)

tampered_hash = (
    AegisCryptoEngine.calcular_sha256(
        tampered_json
    )
)

tampered_verification = (
    AegisCryptoEngine.verificar_firma(
        tampered_hash,
        receipt["policy_signature"],
        gate.public_key,
    )
)

passed = (
    tampered_verification is False
)

record(
    "TAMPERED RECEIPT REJECTED",
    passed,
    f"tampered_signature_valid={tampered_verification}",
)


# ============================================================
# TEST 12
# DIFFERENT TOOL_CALL_ID MUST CHANGE ACTION_REF
# ============================================================

gate_a = AegisLocalPolicyGate()
gate_b = AegisLocalPolicyGate()

agent = "matrix-action-ref-binding"

gate_a.ledger_data[agent] = Decimal("10.00")
gate_b.ledger_data[agent] = Decimal("10.00")

first = gate_a.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="binding-A",
    amount_usd="1.00",
)

second = gate_b.evaluar_gasto(
    agent_did=agent,
    operation="payment",
    tool_call_id="binding-B",
    amount_usd="1.00",
)

passed = (
    first["action_ref"]
    != second["action_ref"]
)

record(
    "TOOL_CALL_ID CHANGES ACTION_REF",
    passed,
    (
        f"same_action_ref="
        f"{first['action_ref'] == second['action_ref']}"
    ),
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n============================================================")
print("AEGIS FINANCIAL LOSS MATRIX REPORT")
print("============================================================")

passed_count = sum(
    1
    for _, passed, _ in results
    if passed
)

failed_count = len(results) - passed_count

for name, passed, _ in results:
    print(
        f"{name}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


print("\nTOTAL TESTS:", len(results))
print("PASS:", passed_count)
print("FAIL:", failed_count)


if failed_count == 0:
    print("\nFINAL RESULT: PASS")
else:
    print("\nFINAL RESULT: FAIL")