import time
import uuid
import random
import os

os.system('') # Activar colores Windows

class Color:
    RED = '\033[91m'
    GREY = '\033[90m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BG_RED = '\033[41m'

print(f"\n{Color.WHITE}> Initialize Agentic Workflow | Cloud Gateway Latency: ~184ms...{Color.RESET}\n")
time.sleep(1)

gasto = 0
for i in range(1, 1001):
    gasto += 50
    tx = str(uuid.uuid4())[:8]
    lat = random.uniform(140.5, 210.3)
    print(f"{Color.RED}[FATAL] HTTP Delay allowed thread {i:03d} to bypass budget. TX_{tx} | Latency: {lat:.2f}ms | Debt: -${gasto:,.2f} USD{Color.RESET}")
    time.sleep(0.001)

print(f"\n{Color.BG_RED}{Color.WHITE} 🚨 SEV-1 CRITICAL INCIDENT: CORPORATE BUDGET EXHAUSTED (-$50,000 USD) 🚨 {Color.RESET}\n")

