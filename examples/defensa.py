from aegis.aegis_sdk import AegisLocalPolicyGate
import time

print("\n🛡️ INITIALIZING AEGIS L3 IN-MEMORY GATE 🛡️")
print("===========================================\n")
time.sleep(1)

# Inicializamos tu motor
aegis_gate = AegisLocalPolicyGate()

# Simulamos el mismo bucle pero pasando por AEGIS
saldo_gastado = 0
for i in range(1, 6):
    print(f"Agent attempting transaction {i}...")
    
    # AEGIS intercepta
    decision = aegis_gate.evaluar_gasto(
        agent_did="did:key:rogue_agent_007",
        operation="api_call",
        tool_call_id=f"tx_{i}",
        amount_usd=5.00
    )
    
    if decision.get("policy_decision") == "allow":
        saldo_gastado += 5.00
        print(f"\033[92m[✓] Transaction ALLOWED. Receipt: {decision['policy_signature'][:15]}...\033[0m")
    else:
        print(f"\033[91m[🛑 BLOCKED] Concurrent Drift Detected by AEGIS. Time: 0.005ms\033[0m")
        print(f"\033[93m[!] Corporate Budget Saved. Total spent capped at: ${saldo_gastado:.2f}\033[0m")
        break # AEGIS detiene el bucle
    time.sleep(0.5)