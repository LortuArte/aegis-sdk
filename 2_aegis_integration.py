from aegis import PolicyGate

# 1. Initialize local IPC Client
aegis_gate = PolicyGate(daily_budget_usd=100)

def execute_agent_payment(agent_id, amount):
    # 2. Intercept budget spending BEFORE tool execution (<1ms lock)
    decision = aegis_gate.evaluate_tool_execution(
        agent_id=agent_id,
        operation="stripe_charge",
        amount=amount
    )
    
    if decision["status"] == "ALLOW":
        # Safe to execute real API call
        # stripe.Charge.create(...)
        return "Transaction Authorized"
    else:
        # Loop blocked instantly. Budget saved.
        return f"BLOCKED: Asynchronous Double-Spend Prevented in {decision['latency']}ms"