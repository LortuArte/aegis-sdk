from decimal import Decimal

from aegis import (
    AegisLocalPolicyGate,
    AegisL3Settlement,
)


def check(name: str, passed: bool):
    print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return passed


print("=" * 60)
print("AEGIS MICROPAYMENT PRECISION TEST")
print("=" * 60)

results = []


# ============================================================
# TEST 1
# $0.001 MUST BE VALID
# ============================================================

gate = AegisLocalPolicyGate()
gate.ledger_data["micro-001"] = Decimal("0.010000")

receipt = gate.evaluar_gasto(
    agent_did="micro-001",
    operation="payment",
    tool_call_id="micro-payment-001",
    amount_usd="0.001",
)

results.append(
    check(
        "$0.001 AUTHORIZATION",
        receipt["policy_decision"] == "allow"
        and receipt["amount_usd"] == "0.001000"
        and gate.ledger_data["micro-001"]
        == Decimal("0.009000"),
    )
)


# ============================================================
# TEST 2
# SMALLEST SUPPORTED UNIT MUST BE VALID
# ============================================================

gate = AegisLocalPolicyGate()
gate.ledger_data["micro-min"] = Decimal("0.000001")

receipt = gate.evaluar_gasto(
    agent_did="micro-min",
    operation="payment",
    tool_call_id="micro-min-001",
    amount_usd="0.000001",
)

results.append(
    check(
        "$0.000001 AUTHORIZATION",
        receipt["policy_decision"] == "allow"
        and receipt["amount_usd"] == "0.000001"
        and gate.ledger_data["micro-min"]
        == Decimal("0.000000"),
    )
)


# ============================================================
# TEST 3
# MORE THAN 6 DECIMALS MUST FAIL CLOSED
# ============================================================

gate = AegisLocalPolicyGate()
gate.ledger_data["micro-invalid"] = Decimal("1.000000")

receipt = gate.evaluar_gasto(
    agent_did="micro-invalid",
    operation="payment",
    tool_call_id="micro-invalid-001",
    amount_usd="0.0000001",
)

results.append(
    check(
        "7-DECIMAL AMOUNT REJECTED",
        receipt["policy_decision"] == "deny"
        and receipt["policy_attenuations"][0]["field"]
        == "invalid_amount"
        and gate.ledger_data["micro-invalid"]
        == Decimal("1.000000"),
    )
)


# ============================================================
# TEST 4
# SIGNED $0.001 L3 SETTLEMENT
# ============================================================

buyer = "micro-buyer"
seller = "micro-seller"

gate = AegisLocalPolicyGate()
gate.ledger_data[buyer] = Decimal("0.010000")

authorization = gate.evaluar_gasto(
    agent_did=buyer,
    operation=f"l3_transfer:{seller}",
    tool_call_id="micro-l3-001",
    amount_usd="0.001",
)

l3 = AegisL3Settlement()

l3.seed_account(
    buyer,
    "0.010000",
)

l3.seed_account(
    seller,
    "0.000001",
)

before_total = (
    l3.get_balance(buyer)
    + l3.get_balance(seller)
)

settlement = l3.settle(
    authorization_receipt=authorization,
    authorization_public_key=gate.public_key,
)

buyer_after = l3.get_balance(buyer)
seller_after = l3.get_balance(seller)

after_total = (
    buyer_after
    + seller_after
)

results.append(
    check(
        "$0.001 SIGNED L3 SETTLEMENT",
        settlement["status"] == "SETTLED"
        and settlement["amount_usd"] == "0.001000"
        and buyer_after == Decimal("0.009000")
        and seller_after == Decimal("0.001001")
        and before_total == after_total,
    )
)

l3.close()


# ============================================================
# FINAL REPORT
# ============================================================

passed = sum(results)
failed = len(results) - passed

print()
print("=" * 60)
print("MICROPAYMENT FINAL REPORT")
print("=" * 60)
print("TOTAL:", len(results))
print("PASS:", passed)
print("FAIL:", failed)
print(
    "FINAL RESULT:",
    "PASS" if failed == 0 else "FAIL",
)