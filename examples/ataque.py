import time

print("\n🚨 [WARNING] AGENT ASYNC LOOP DETECTED 🚨")
print("===========================================")
time.sleep(1)

saldo_gastado = 0
for i in range(1, 21):
    saldo_gastado += 5.00
    print(f"\033[91m[FAILED] Web2 API Timeout. Agent fired transaction {i}. Budget drained: ${saldo_gastado:.2f}\033[0m")
    time.sleep(0.1) # Va rapidísimo

print("\n💥 FATAL ERROR: Corporate Budget Exhausted (-$100.00 in 2 seconds) 💥")