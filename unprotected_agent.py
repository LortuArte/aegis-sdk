import time
import os

os.system('')

class Color:
    ROJO = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BG_ROJO = '\033[41m'
    BLANCO = '\033[97m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'

print(f"\n{Color.CYAN}[SYSTEM] Initializing Agent Workflow...{Color.RESET}")
time.sleep(1)
print(f"{Color.YELLOW}⚠️ WARNING: No local Policy Gate detected. Using standard Cloud API...{Color.RESET}\n")
time.sleep(1)

print(f"{Color.BOLD}{Color.ROJO}=================================================={Color.RESET}")
print(f"{Color.BOLD}{Color.BG_ROJO}{Color.BLANCO} 🚨 CRITICAL ALERT: ASYNC LOOP DETECTED 🚨 {Color.RESET}")
print(f"{Color.BOLD}{Color.ROJO}=================================================={Color.RESET}\n")
time.sleep(0.5)

gasto_total = 0
for i in range(1, 26):
    gasto_total += 50
    print(f"{Color.ROJO}💀 [FAILED] Web2 API Timeout. Agent fired transaction {i:02d}. Budget drained: ${gasto_total:,.2f} 💸{Color.RESET}")
    time.sleep(0.15)

print(f"\n{Color.BOLD}{Color.BG_ROJO}{Color.BLANCO} 💥 FATAL ERROR: CORPORATE BUDGET EXHAUSTED (-${gasto_total:,.2f} in 3.7 seconds) 💥 {Color.RESET}\n")