from decimal import Decimal
from aegis import AegisLocalPolicyGate


print("\n=== AEGIS TOOL_CALL_ID CRYPTO BINDING TEST ===")


def execute(tool_call_id):
    gate = AegisLocalPolicyGate()

    agent_id = "agent-binding-test"

    gate.ledger_data[agent_id] = Decimal("10.00")

    return gate.evaluar_gasto(
        agent_did=agent_id,
        operation="payment",
        tool_call_id=tool_call_id,
        amount_usd="1.00",
    )


first = execute("payment-A")
second = execute("payment-B")


print("FIRST ACTION_REF:", first["action_ref"])
print("SECOND ACTION_REF:", second["action_ref"])

print(
    "SAME ACTION_REF:",
    first["action_ref"] == second["action_ref"]
)


tool_call_bound = (
    first["action_ref"]
    != second["action_ref"]
)


print(
    "TOOL_CALL_ID CRYPTO BOUND:",
    tool_call_bound
)


if tool_call_bound:
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")