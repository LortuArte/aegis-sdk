from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier, Lock

from aegis import AegisLocalPolicyGate


REQUESTS = 100
WORKERS = 100
AGENT_DID = "same-id-local-reproduction"
OPERATION = "x402_paid_tool_call"
TOOL_CALL_ID = "same-tool-call-001"
AMOUNT_USD = "0.001"
INITIAL_BUDGET = Decimal("0.001000")


gate = AegisLocalPolicyGate()
gate.ledger_data[AGENT_DID] = INITIAL_BUDGET

start_barrier = Barrier(REQUESTS)
counter_lock = Lock()
external_calls = 0


def simulated_external_tool():
    global external_calls

    with counter_lock:
        external_calls += 1

    return "PAYMENT_EXECUTED"


def concurrent_attempt(_):
    start_barrier.wait()

    receipt = gate.evaluar_gasto(
        agent_did=AGENT_DID,
        operation=OPERATION,
        tool_call_id=TOOL_CALL_ID,
        amount_usd=AMOUNT_USD,
    )

    # Safe execution-disposition pattern introduced in AEGIS 3.4.0.
    if receipt["execution_permitted"] is True:
        simulated_external_tool()

    return receipt


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    receipts = list(
        executor.map(
            concurrent_attempt,
            range(REQUESTS),
        )
    )


decisions = Counter(
    receipt["policy_decision"]
    for receipt in receipts
)

cached_replays = sum(
    receipt["cached"] is True
    for receipt in receipts
)

new_authorizations = sum(
    receipt["policy_decision"] == "allow"
    and receipt["cached"] is False
    for receipt in receipts
)

execution_grants = sum(
    receipt["execution_permitted"] is True
    for receipt in receipts
)

final_balance = gate.ledger_data[AGENT_DID]

safe_execution = (
    new_authorizations == 1
    and execution_grants == 1
    and external_calls == 1
    and final_balance == Decimal("0.000000")
)


print("=== AEGIS SAME TOOL_CALL_ID CONTENTION TEST ===")
print("LIVE NETWORK CALLS: 0")
print("SCOPE: local / single-process")
print("REQUESTS:", REQUESTS)
print("WORKERS:", WORKERS)
print("TOOL_CALL_ID:", TOOL_CALL_ID)
print("ALLOW RESPONSES:", decisions["allow"])
print("DENY RESPONSES:", decisions["deny"])
print("NEW AUTHORIZATIONS:", new_authorizations)
print("EXECUTION GRANTS:", execution_grants)
print("CACHED REPLAYS:", cached_replays)
print("EXTERNAL EXECUTIONS:", external_calls)
print("FINAL BALANCE:", final_balance)
print("EXPECTED EXTERNAL EXECUTIONS: 1")
print(
    "RESULT:",
    "PASS"
    if safe_execution
    else "FAIL - DUPLICATE EXTERNAL EXECUTION",
)

assert safe_execution, (
    "The same tool_call_id was permitted to execute "
    f"the external tool {external_calls} times."
)