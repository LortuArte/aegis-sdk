import time
import os
import random
import uuid

# Fuerza los colores en la terminal de Windows
os.system('')

class Color:
    ROJO = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BG_ROJO = '\033[41m'
    BLANCO = '\033[97m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GRIS = '\033[90m'

print(f"\n{Color.CYAN}[SYSTEM] Initializing Agentic Workflow (us-east-1)...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.GRIS}[NETWORK] Establishing connection to Cloud Provider API...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.YELLOW}⚠️ WARNING: L3 Local Policy Gate (AEGIS) NOT DETECTED.{Color.RESET}")
print(f"{Color.YELLOW}⚠️ FALLBACK: Routing transactions via standard Cloud Gateway (High Latency).{Color.RESET}\n")
time.sleep(1)

print(f"{Color.BOLD}{Color.ROJO}======================================================================{Color.RESET}")
print(f"{Color.BOLD}{Color.BG_ROJO}{Color.BLANCO} 🚨 SEV-1 CRITICAL INCIDENT: ASYNCHRONOUS CONCURRENT DRIFT DETECTED 🚨 {Color.RESET}")
print(f"{Color.BOLD}{Color.ROJO}======================================================================{Color.RESET}\n")
time.sleep(0.5)

NUM_ATTACKS = 1000
AMOUNT_USD = 50
gasto_total = 0

print(f"{Color.ROJO}[!] INCOMING BURST: {NUM_ATTACKS} concurrent tool calls detected.{Color.RESET}")
print(f"{Color.GRIS}[!] CLOUD GATEWAY RESPONSE TIME: ~184ms (Too slow to block in-flight requests){Color.RESET}\n")
time.sleep(1)

# Simulación de la caída catastrófica
# Imprime rápido visualmente, pero la latencia que muestra el texto es alta para justificar el robo
for i in range(1, NUM_ATTACKS + 1):
    gasto_total += AMOUNT_USD
    tx_id = str(uuid.uuid4())[:8]
    latency = random.uniform(140.5, 210.3)
    
    print(f"{Color.ROJO}💀 [FAILED] TX_{tx_id} | Latency: {latency:.2f}ms | Race Condition. Budget drained: -${gasto_total:,.2f} USD{Color.RESET}")
    time.sleep(0.001) 

print(f"\n{Color.ROJO}╔══════════════════════════════════════════════════════════════════╗{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BOLD}📉 POST-MORTEM INCIDENT REPORT: CLOUD GATEWAY FAILURE{Color.RESET}            {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}╠══════════════════════════════════════════════════════════════════╣{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BLANCO}INCIDENT ID:        req_{str(uuid.uuid4())[:12]}{Color.RESET}                   {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BLANCO}SEVERITY:           SEV-1 (CRITICAL){Color.RESET}                             {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BLANCO}ROOT CAUSE:         Network Latency / Concurrent Drift{Color.RESET}           {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BLANCO}TOTAL REQUESTS:     {NUM_ATTACKS}{Color.RESET}                                         {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.YELLOW}BLOCKED BY CLOUD:   0 (Latency window exceeded){Color.RESET}                  {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}╠══════════════════════════════════════════════════════════════════╣{Color.RESET}")
print(f"{Color.ROJO}║{Color.RESET} {Color.BOLD}{Color.BG_ROJO}{Color.BLANCO} 💸 TOTAL FINANCIAL LOSS: -${gasto_total:,.2f} USD {Color.RESET}                           {Color.ROJO}║{Color.RESET}")
print(f"{Color.ROJO}╚══════════════════════════════════════════════════════════════════╝{Color.RESET}\n")

print(f"{Color.BOLD}{Color.ROJO}💥 SYSTEM HALTED. MANUAL INTERVENTION REQUIRED. 💥{Color.RESET}\n")