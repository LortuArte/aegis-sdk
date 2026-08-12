import concurrent.futures
import time

from aegis import AegisLocalPolicyGate


gate = AegisLocalPolicyGate()
agent = "did:key:aegis_final_demo_agent"


def attempt(i):
    return gate.evaluar_gasto(
        agent_did=agent,
        operation="stripe_charge",
        tool_call_id=f"concurrent-{i}",
        amount_usd=10.00,
    )


start = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    results = list(executor.map(attempt, range(100)))

elapsed = time.perf_counter() - start

allowed = [
    r for r in results
    if r["policy_decision"] == "allow"
]

denied = [
    r for r in results
    if r["policy_decision"] == "deny"
]

print()
print("=== AEGIS REAL CONCURRENCY TEST ===")
print("REQUESTS:", len(results))
print("ALLOW:", len(allowed))
print("DENY:", len(denied))
print("FINAL BALANCE:", gate.ledger_data[agent])
print("ELAPSED:", elapsed, "seconds")
print("THROUGHPUT:", len(results) / elapsed, "req/s")

assert len(results) == 100
assert len(allowed) == 1
assert len(denied) == 99
assert gate.ledger_data[agent] == 0.00

print("RESULT: PASS")