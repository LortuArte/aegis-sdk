from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Lock
import json
import platform
import sys

import aegis
from aegis import AegisLocalPolicyGate


AGENT_ID = "external-validator"
TOOL_CALL_ID = "external-same-logical-call"
ATTEMPTS = 100

gate = AegisLocalPolicyGate()
gate.ledger_data[AGENT_ID] = Decimal("1.000000")

downstream_count = 0
downstream_lock = Lock()


def attempt(_):
    global downstream_count

    receipt = gate.evaluar_gasto(
        agent_did=AGENT_ID,
        operation="external_validation_tool",
        tool_call_id=TOOL_CALL_ID,
        amount_usd="1.000000",
    )

    if receipt.get("execution_permitted") is True:
        with downstream_lock:
            downstream_count += 1

    return receipt


with ThreadPoolExecutor(max_workers=100) as pool:
    receipts = list(pool.map(attempt, range(ATTEMPTS)))


execution_grants = sum(
    1
    for receipt in receipts
    if receipt.get("execution_permitted") is True
)

cached_replays = sum(
    1
    for receipt in receipts
    if receipt.get("cached") is True
)

final_balance = str(gate.ledger_data[AGENT_ID])

passed = (
    execution_grants == 1
    and cached_replays == 99
    and downstream_count == 1
    and Decimal(final_balance) == Decimal("0.000000")
)

result = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "aegis_version": aegis.__version__,
    "aegis_module_path": aegis.__file__,
    "attempts": ATTEMPTS,
    "execution_grants": execution_grants,
    "cached_replays": cached_replays,
    "downstream_executions": downstream_count,
    "final_balance": final_balance,
    "result": "PASS" if passed else "FAIL",
}

print(json.dumps(result, indent=2))
print("RESULT:", result["result"])

raise SystemExit(0 if passed else 1)
