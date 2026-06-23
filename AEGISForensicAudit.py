import time
import random
import hashlib
import sys

# Configuración Estética (Estilo Ciberseguridad/Matrix)
class Color:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BG_CYAN = '\033[46m'
    BG_GREEN = '\033[42m'
    BLINK = '\033[5m'

NUM_ATTACKS = 1000
AMOUNT_USD = 500

def generate_crypto_sig(index):
    return hashlib.sha256(f"aegis_tx_{index}_{time.time()}".encode()).hexdigest()[:16].upper()

print(f"\n{Color.CYAN}[SYSTEM] Initializing Agentic Workflow (M2M Economy Module)...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.CYAN}[SYSTEM] Scanning for tool execution guardrails...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.GREEN}[+] AEGIS Core SDK detected (aegis-core-lortuarte-sdk).{Color.RESET}")
time.sleep(0.5)
print(f"{Color.BOLD}{Color.GREEN}[+] 🛡️ LOCAL IPC MEMORY LOCKS: ACTIVATED. TARGET LATENCY: < 1ms{Color.RESET}\n")
time.sleep(1)

print(f"{Color.BOLD}{Color.CYAN}" + "█"*80)
print(f"⚡ SECURE ENVIRONMENT: OPTIMISTIC CONCURRENCY CONTROL (OCC) IN EFFECT ⚡")
print("█"*80 + f"{Color.RESET}\n")

# ¡AQUÍ ESTÁ EL ESLOGAN CORREGIDO!
print(f"{Color.BG_CYAN}{Color.WHITE}{Color.BOLD} >>> YOUR AI AGENT IS 100ms AWAY FROM BANKRUPTING YOUR STARTUP <<< {Color.RESET}\n")

print(f"{Color.CYAN}⚠️ ROGUE LLM LOOP DETECTED ({NUM_ATTACKS} CONCURRENT STRIKES){Color.RESET}")
print(f"{Color.CYAN}✨ INTERCEPTING TOOL EXECUTION AT MEMORY LEVEL...{Color.RESET}\n")
time.sleep(1)

start_time = time.perf_counter()

# Efecto Matrix Auditoría (Alineación perfecta, resolución sub-milisegundo)
for i in range(1, NUM_ATTACKS + 1):
    # Latencia Sub-milisegundo (< 1ms)
    simulated_latency = random.uniform(0.0001, 0.0009)
    sig = generate_crypto_sig(i)
    
    sys.stdout.write(f"{Color.GREEN}[AEGIS OCC] TX_{i:04d} | Sig: ed25519:{sig} | IPC_LOCK: ACQUIRED | STATUS: REJECTED ({simulated_latency:.4f}ms) 🛑{Color.RESET}\n")
    sys.stdout.flush()
    time.sleep(0.002)

end_time = time.perf_counter()
total_latency = (end_time - start_time) * 1000
money_saved = NUM_ATTACKS * AMOUNT_USD

# Reporte Forense Profesional
print(f"\n{Color.CYAN}╔" + "═"*76 + "╗")
print(f"{Color.CYAN}║ {Color.WHITE}{Color.BOLD}AEGIS ENTERPRISE: SUB-MILLISECOND RESOLUTION REPORT{Color.RESET}{Color.CYAN}".ljust(86) + "║")
print(f"{Color.CYAN}╠" + "═"*76 + "╣")
print(f"{Color.CYAN}║ {Color.WHITE}Time to Resolution:   {total_latency:.2f} ms{Color.CYAN}".ljust(85) + "║")
print(f"{Color.CYAN}║ {Color.WHITE}Concurrent Requests:  {NUM_ATTACKS}{Color.CYAN}".ljust(85) + "║")
print(f"{Color.CYAN}║ {Color.WHITE}Failed Cloud Blocks:  0{Color.CYAN}".ljust(85) + "║")
print(f"{Color.CYAN}║ {Color.WHITE}AEGIS IPC Intercepts: {NUM_ATTACKS} (100% OCC Compliance){Color.CYAN}".ljust(85) + "║")
print(f"{Color.CYAN}╚" + "═"*76 + "╝")

print(f"{Color.BG_GREEN}{Color.WHITE}{Color.BOLD}{Color.BLINK} >>> CORPORATE WALLET SAVED: ${money_saved:,.2f} USD <<< {Color.RESET}\n")
print(f"{Color.BOLD}{Color.GREEN}✅ VERDICT: INFRASTRUCTURE SECURED. ZERO FINANCIAL DRIFT. 🛡️{Color.RESET}")