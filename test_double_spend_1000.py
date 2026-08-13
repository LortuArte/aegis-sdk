from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from collections import Counter
from time import perf_counter

from aegis import AegisLocalPolicyGate


print("\n=== AEGIS 1000-WAY DOUBLE-SPEND ADVERSARIAL TEST ===")

REQUESTS = 1000
WORKERS = 100

AGENT_ID = "agent-double-spend-1000"
INITIAL_BALANCE = Decimal("10.00")
AMOUNT_PER_REQUEST = "10.00"

gate = AegisLocalPolicyGate()
gate.ledger_data[AGENT_ID] = INITIAL_BALANCE


def attack_request(index):
    return gate.evaluar_gasto(
        agent_did=AGENT_ID,
        operation="payment",
        tool_call_id=f"attack-{index}",
        amount_usd=AMOUNT_PER_REQUEST,
    )


start = perf_counter()

results = []

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = [
        executor.submit(attack_request, i)
        for i in range(REQUESTS)
    ]

    for future in as_completed(futures):
        results.append(future.result())

elapsed = perf_counter() - start


decisions = Counter(
    result["policy_decision"]
    for result in results
)

allow_count = decisions.get("allow", 0)
deny_count = decisions.get("deny", 0)

final_balance = gate.ledger_data[AGENT_ID]

authorized_total = (
    Decimal(str(allow_count))
    * Decimal(AMOUNT_PER_REQUEST)
)

expected_allow = 1
expected_deny = REQUESTS - 1


print("REQUESTS:", REQUESTS)
print("WORKERS:", WORKERS)
print("INITIAL BALANCE:", INITIAL_BALANCE)
print("AMOUNT EACH:", AMOUNT_PER_REQUEST)

print("\n=== RESULTS ===")
print("ALLOW:", allow_count)
print("DENY:", deny_count)
print("FINAL BALANCE:", final_balance)
print("AUTHORIZED TOTAL:", authorized_total)

print("ELAPSED:", elapsed, "seconds")

if elapsed > 0:
    print(
        "THROUGHPUT:",
        REQUESTS / elapsed,
        "req/s"
    )


no_overspend = (
    authorized_total <= INITIAL_BALANCE
)

correct_allow_count = (
    allow_count == expected_allow
)

correct_deny_count = (
    deny_count == expected_deny
)

correct_final_balance = (
    final_balance == Decimal("0.00")
)


print("\nNO OVERSPEND:", no_overspend)
print("CORRECT ALLOW COUNT:", correct_allow_count)
print("CORRECT DENY COUNT:", correct_deny_count)
print("CORRECT FINAL BALANCE:", correct_final_balance)


passed = (
    no_overspend
    and correct_allow_count
    and correct_deny_count
    and correct_final_balance
)


if passed:
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")