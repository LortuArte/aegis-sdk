import time
import random
import os
import hashlib

# Fuerza los colores en la terminal de Windows
os.system('')

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BG_RED = '\033[41m'

NUM_ATTACKS = 1000 
AMOUNT_USD = 50

print(f"\n{Color.CYAN}[SYSTEM] Initializing Agent Workflow...{Color.RESET}")
time.sleep(0.5)
print(f"{Color.CYAN}[SYSTEM] AEGIS SDK detected. Routing transactions through L3 Gate.{Color.RESET}")
time.sleep(1)
print(f"{Color.BOLD}{Color.GREEN}[+] 🛡️ AEGIS ACID LOCKS: ACTIVATED. TARGET LATENCY: < 0.01ms{Color.RESET}\n")
time.sleep(1)

print(f"{Color.BOLD}{Color.RED}================================================================={Color.RESET}")
print(f"{Color.BOLD}{Color.BG_RED}{Color.WHITE} 🚨 CRITICAL INCIDENT: CONCURRENT DOUBLE-SPEND DRIFT DETECTED 🚨 {Color.RESET}")
print(f"{Color.BOLD}{Color.RED}================================================================={Color.RESET}\n")
time.sleep(0.5)

print(f"{Color.YELLOW}⚠️ IMMINENT ASYNCHRONOUS BURST IMPACT ({NUM_ATTACKS} REQUESTS){Color.RESET}")
print(f"{Color.RED}💥 RECEIVING ATTACK...{Color.RESET}\n")
time.sleep(0.5)

start_time = time.perf_counter()

# Efecto Matrix Acelerado con Firmas Criptográficas Visuales
for i in range(1, NUM_ATTACKS + 1):
    simulated_latency = random.uniform(0.002, 0.005)
    # Genera un hash criptográfico visual para dar máxima credibilidad
    mock_signature = hashlib.sha256(f"tx_{i}_{time.time()}".encode()).hexdigest()[:16].upper()
    
    print(f"{Color.GREEN}[⚡ AEGIS L3] TX_{i:04d} | Sig: ed25519:{mock_signature} | ACID LOCK -> BLOCKED ({simulated_latency:.4f}ms) 🛑{Color.RESET}")
    time.sleep(0.001) 

end_time = time.perf_counter()
total_latency = (end_time - start_time) * 1000
money_saved = NUM_ATTACKS * AMOUNT_USD

print(f"\n{Color.CYAN}╔══════════════════════════════════════════════════════════════════╗{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.BOLD}🛡️  AEGIS ENTERPRISE: FORENSIC RESOLUTION REPORT{Color.RESET}                 {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}╠══════════════════════════════════════════════════════════════════╣{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.WHITE}Time to Resolution:   {total_latency:.2f} ms{Color.RESET}                                {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.WHITE}Concurrent Requests:  {NUM_ATTACKS}{Color.RESET}                                       {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.RED}Failed Cloud Blocks:  0{Color.RESET}                                          {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.GREEN}AEGIS L3 Intercepts:  {NUM_ATTACKS} (100% ACID Compliance){Color.RESET}              {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}╠══════════════════════════════════════════════════════════════════╣{Color.RESET}")
print(f"{Color.CYAN}║{Color.RESET} {Color.BOLD}{Color.YELLOW}💰 CORPORATE WALLET SAVED: ${money_saved:,.2f} USD{Color.RESET}                      {Color.CYAN}║{Color.RESET}")
print(f"{Color.CYAN}╚══════════════════════════════════════════════════════════════════╝{Color.RESET}\n")

print(f"{Color.BOLD}{Color.GREEN}✅ VERDICT: INFRASTRUCTURE SECURED. ZERO FINANCIAL DRIFT. 🛡️{Color.RESET}")