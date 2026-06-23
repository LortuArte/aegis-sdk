import time
import random
import uuid
import sys

# Configuración Estética (Estilo Agresivo/Pánico)
class Color:
    RED = '\033[91m'
    WHITE = '\033[97m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BG_RED = '\033[41m'
    BLINK = '\033[5m'

NUM_ATTACKS = 1000
AMOUNT_USD = 500
gasto_total = 0

def print_hex_dump():
    """Generates a fake hex dump for visual chaos"""
    hex_chars = "0123456789ABCDEF"
    dump = " ".join("".join(random.choices(hex_chars, k=2)) for _ in range(6))
    return f"0x{random.randint(0x10000, 0xFFFFF):05X} {dump}"

print(f"{Color.CYAN}[SYSTEM] Initializing Agentic Workflow (M2M Economy Module)...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.CYAN}[NETWORK] Establishing connection to Cloud HTTP Gateway...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.YELLOW}⚠️ WARNING: AEGIS Core SDK NOT DETECTED.{Color.RESET}")
print(f"{Color.YELLOW}⚠️ FALLBACK: Routing tool execution via Cloud HTTP Gateway (LangSmith/Portkey fallback).{Color.RESET}\n")
time.sleep(1)

print(f"{Color.BOLD}{Color.RED}" + "█"*80)
print(f"{Color.BLINK}🚨 SEV-1 CRITICAL: 1,000-THREAD DOUBLE SPEND VULNERABILITY EXPLOITED 🚨{Color.RESET}{Color.BOLD}{Color.RED}")
print("█"*80 + f"{Color.RESET}\n")

print(f"{Color.BG_RED}{Color.WHITE}{Color.BOLD} >>> YOUR AI AGENT IS 100ms AWAY FROM BANKRUPTING YOUR STARTUP <<< {Color.RESET}\n")

print(f"{Color.RED}[!] ROGUE LLM LOOP DETECTED: {NUM_ATTACKS} concurrent tool calls fired.{Color.RESET}")
print(f"{Color.RED}[!] HTTP LATENCY TRAP: >100ms network delay. Cannot block in-flight requests.{Color.RESET}\n")
time.sleep(1.5)

# Simulación Catastrófica de Sangrado (1000-Thread Vulnerability)
for i in range(1, NUM_ATTACKS + 1):
    gasto_total += AMOUNT_USD
    tx_id = str(uuid.uuid4())[:8]
    # Latency típica de HTTP en la nube
    latency = random.uniform(140.5, 210.3)
    hex_err = print_hex_dump()
    
    sys.stdout.write(f"{Color.RED}💀 [HTTP DELAY] {hex_err} | TX_{tx_id} | Latency: {latency:.2f}ms | Async Loop -> DOUBLE-SPEND: -${gasto_total:,.2f}{Color.RESET}\n")
    sys.stdout.flush()
    time.sleep(0.003)

# Reporte Post-Mortem usando el vocabulario de tu landing
print(f"\n{Color.RED}╔" + "═"*70 + "╗")
print(f"{Color.RED}║ {Color.WHITE}{Color.BOLD}POST-MORTEM REPORT: CLOUD GATEWAY VULNERABILITY{Color.RESET}{Color.RED}".ljust(80) + "║")
print(f"{Color.RED}╠" + "═"*70 + "╣")
print(f"{Color.RED}║ {Color.WHITE}INCIDENT ID:  req_{str(uuid.uuid4())[:12]}{Color.RED}".ljust(80) + "║")
print(f"{Color.RED}║ {Color.WHITE}ROOT CAUSE:   Network Latency / Asynchronous Double-Spend{Color.RED}".ljust(80) + "║")
print(f"{Color.RED}║ {Color.WHITE}TOOL ACCESSED: Stripe API (Live Mode){Color.RED}".ljust(80) + "║")
print(f"{Color.RED}║ {Color.WHITE}BLOCKED:      0 (HTTP Gateway too slow){Color.RED}".ljust(80) + "║")
print(f"{Color.RED}╚" + "═"*70 + "╝")

# El concepto de "Deuda Fantasma" de tu marketing
print(f"{Color.BG_RED}{Color.WHITE}{Color.BOLD}{Color.BLINK} >>> PHANTOM DEBT ACCUMULATED: -${gasto_total:,.2f} USD <<< {Color.RESET}\n")
print(f"{Color.BOLD}{Color.RED}*** STARTUP BANKRUPT. NETWORK LATENCY IS THE ENEMY. ***{Color.RESET}")