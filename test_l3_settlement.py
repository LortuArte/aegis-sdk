from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from aegis import AegisLocalPolicyGate
from aegis.l3_settlement import AegisL3Settlement


print("\n============================================================")
print("AEGIS L3 ATOMIC SETTLEMENT SECURITY TEST")
print("============================================================")


results = []


def record(name, passed):
    results.append(
        (
            name,
            passed
        )
    )

    print(
        f"{name}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


# ======================================================================
# 1. VALID SIGNED SETTLEMENT
# ======================================================================

gate = AegisLocalPolicyGate()

buyer = "did:key:l3-buyer"
seller = "did:key:l3-seller"

gate.ledger_data[
    buyer
] = Decimal("100.00")

l3 = AegisL3Settlement()

l3.seed_account(
    buyer,
    "10.00"
)

l3.seed_account(
    seller,
    "0.01"
)

initial_total = (
    l3.get_balance(buyer)
    + l3.get_balance(seller)
)


receipt = gate.evaluar_gasto(
    agent_did=buyer,
    operation=f"l3_transfer:{seller}",
    tool_call_id="l3-valid-001",
    amount_usd="3.00",
)


settlement = l3.settle(
    receipt,
    gate.public_key
)


valid_settlement = (
    settlement["status"]
    == "SETTLED"

    and settlement["cached"]
    is False

    and l3.get_balance(buyer)
    == Decimal("7.00")

    and l3.get_balance(seller)
    == Decimal("3.01")
)


record(
    "SIGNED SETTLEMENT",
    valid_settlement
)


# ======================================================================
# 2. CONSERVATION OF VALUE
# ======================================================================

final_total = (
    l3.get_balance(buyer)
    + l3.get_balance(seller)
)

record(
    "CONSERVATION OF VALUE",
    final_total
    == initial_total
)


# ======================================================================
# 3. EXACT REPLAY
# ======================================================================

before_replay_buyer = (
    l3.get_balance(buyer)
)

before_replay_seller = (
    l3.get_balance(seller)
)


replay = l3.settle(
    receipt,
    gate.public_key
)


record(
    "EXACT REPLAY IDEMPOTENT",
    (
        replay["cached"] is True

        and l3.get_balance(buyer)
        == before_replay_buyer

        and l3.get_balance(seller)
        == before_replay_seller

        and l3.settlement_count()
        == 1
    )
)


# ======================================================================
# 4. TAMPERED SELLER
# ======================================================================

tampered = receipt.copy()

tampered[
    "operation"
] = "l3_transfer:attacker"


tamper_blocked = False

try:
    l3.settle(
        tampered,
        gate.public_key
    )

except ValueError:
    tamper_blocked = True


record(
    "TAMPERED SELLER BLOCKED",
    tamper_blocked
)


# ======================================================================
# 5. TAMPERED AMOUNT
# ======================================================================

tampered_amount = receipt.copy()

tampered_amount[
    "amount_usd"
] = "9.00"


amount_tamper_blocked = False

try:
    l3.settle(
        tampered_amount,
        gate.public_key
    )

except ValueError:
    amount_tamper_blocked = True


record(
    "TAMPERED AMOUNT BLOCKED",
    amount_tamper_blocked
)


# ======================================================================
# 6. DATABASE ROLLBACK AFTER DEBIT
# ======================================================================

rollback_gate = (
    AegisLocalPolicyGate()
)

rollback_buyer = (
    "did:key:rollback-buyer"
)

rollback_seller = (
    "did:key:rollback-seller"
)


rollback_gate.ledger_data[
    rollback_buyer
] = Decimal("100.00")


rollback_l3 = (
    AegisL3Settlement()
)


rollback_l3.seed_account(
    rollback_buyer,
    "10.00"
)

rollback_l3.seed_account(
    rollback_seller,
    "0.01"
)


rollback_receipt = (
    rollback_gate.evaluar_gasto(
        agent_did=rollback_buyer,
        operation=(
            f"l3_transfer:"
            f"{rollback_seller}"
        ),
        tool_call_id="rollback-l3-001",
        amount_usd="5.00",
    )
)


def forced_failure():
    raise RuntimeError(
        "FORCED_L3_FAILURE"
    )


rollback_l3._after_debit_hook = (
    forced_failure
)


rollback_happened = False

try:
    rollback_l3.settle(
        rollback_receipt,
        rollback_gate.public_key
    )

except RuntimeError:
    rollback_happened = True


record(
    "ATOMIC ROLLBACK",
    (
        rollback_happened

        and rollback_l3.get_balance(
            rollback_buyer
        )
        == Decimal("10.00")

        and rollback_l3.get_balance(
            rollback_seller
        )
        == Decimal("0.01")

        and rollback_l3.settlement_count()
        == 0
    )
)


# ======================================================================
# 7. CONCURRENT SETTLEMENT / LIMITED BUDGET
# ======================================================================

stress_gate = (
    AegisLocalPolicyGate()
)

stress_buyer = (
    "did:key:stress-buyer"
)

stress_seller = (
    "did:key:stress-seller"
)


# Authorization budget deliberately larger
# than actual settlement funds.
stress_gate.ledger_data[
    stress_buyer
] = Decimal("1000.00")


stress_l3 = (
    AegisL3Settlement()
)

stress_l3.seed_account(
    stress_buyer,
    "10.00"
)

stress_l3.seed_account(
    stress_seller,
    "0.01"
)


stress_receipts = []

for i in range(100):

    stress_receipts.append(
        stress_gate.evaluar_gasto(
            agent_did=stress_buyer,
            operation=(
                f"l3_transfer:"
                f"{stress_seller}"
            ),
            tool_call_id=(
                f"stress-l3-{i}"
            ),
            amount_usd="10.00",
        )
    )


def run_settlement(receipt):
    try:
        result = (
            stress_l3.settle(
                receipt,
                stress_gate.public_key
            )
        )

        return result["status"]

    except ValueError:
        return "DENIED"


with ThreadPoolExecutor(
    max_workers=50
) as executor:

    outcomes = list(
        executor.map(
            run_settlement,
            stress_receipts
        )
    )


settled_count = (
    outcomes.count(
        "SETTLED"
    )
)

denied_count = (
    outcomes.count(
        "DENIED"
    )
)


record(
    "CONCURRENT LIMITED-BUDGET SETTLEMENT",
    (
        settled_count == 1
        and denied_count == 99

        and stress_l3.get_balance(
            stress_buyer
        )
        == Decimal("0.00")

        and stress_l3.get_balance(
            stress_seller
        )
        == Decimal("10.01")

        and stress_l3.settlement_count()
        == 1
    )
)


print(
    "\nSETTLED:",
    settled_count
)

print(
    "DENIED:",
    denied_count
)


# ======================================================================
# FINAL REPORT
# ======================================================================

passed = sum(
    1
    for _, result in results
    if result
)

failed = (
    len(results)
    - passed
)


print(
    "\n============================================================"
)

print(
    "L3 FINAL REPORT"
)

print(
    "============================================================"
)

print(
    "TOTAL:",
    len(results)
)

print(
    "PASS:",
    passed
)

print(
    "FAIL:",
    failed
)


if failed == 0:
    print(
        "\nFINAL RESULT: PASS"
    )

else:
    print(
        "\nFINAL RESULT: FAIL"
    )