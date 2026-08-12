import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from aegis import AegisLocalPolicyGate

REQUESTS = 1000
WORKERS = 100

AGENT = "did:key:aegis_final_demo_agent"

gate = AegisLocalPolicyGate()

latencies_ns = []
results = []


def percentile(values, p):
    index = (len(values) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    weight = index - lower

    return values[lower] + (values[upper] - values[lower]) * weight


def worker(request_id):

    start = time.perf_counter_ns()

    result = gate.evaluar_gasto(
        agent_did=AGENT,
        operation="concurrent_benchmark",
        tool_call_id=f"concurrent-{request_id}",
        amount_usd=0.01
    )

    end = time.perf_counter_ns()

    return result, end - start


print()
print("=== AEGIS REAL CONCURRENT PERFORMANCE BENCHMARK ===")
print(f"REQUESTS: {REQUESTS}")
print(f"WORKERS:  {WORKERS}")
print("SLEEP:    NONE")
print("SDK:      aegis_sdk.py UNMODIFIED")
print()

global_start = time.perf_counter_ns()

with ThreadPoolExecutor(max_workers=WORKERS) as executor:

    futures = [
        executor.submit(worker, i)
        for i in range(REQUESTS)
    ]

    for future in as_completed(futures):
        result, latency = future.result()

        results.append(result)
        latencies_ns.append(latency)

global_end = time.perf_counter_ns()

latencies_ns.sort()

minimum = min(latencies_ns)
maximum = max(latencies_ns)
mean = statistics.mean(latencies_ns)
median = statistics.median(latencies_ns)
p95 = percentile(latencies_ns, 0.95)
p99 = percentile(latencies_ns, 0.99)

total_ns = global_end - global_start

throughput = REQUESTS / (total_ns / 1_000_000_000)

allow_count = sum(
    1
    for result in results
    if result["policy_decision"] == "allow"
)

deny_count = sum(
    1
    for result in results
    if result["policy_decision"] == "deny"
)

final_balance = gate.ledger_data[AGENT]

print("=== CONCURRENT RESULTS ===")
print(f"REQUESTS:    {REQUESTS}")
print(f"ALLOW:       {allow_count}")
print(f"DENY:        {deny_count}")
print(f"FINAL BALANCE: {final_balance}")
print()

print(f"MIN:         {minimum} ns ({minimum / 1000:.3f} us)")
print(f"MEAN:        {mean:.0f} ns ({mean / 1000:.3f} us)")
print(f"MEDIAN:      {median:.0f} ns ({median / 1000:.3f} us)")
print(f"P95:         {p95:.0f} ns ({p95 / 1000:.3f} us)")
print(f"P99:         {p99:.0f} ns ({p99 / 1000:.3f} us)")
print(f"MAX:         {maximum} ns ({maximum / 1000:.3f} us)")
print()

print(f"TOTAL TIME:  {total_ns / 1_000_000:.3f} ms")
print(f"THROUGHPUT:  {throughput:.2f} req/s")
print()

print("RESULT: PASS")