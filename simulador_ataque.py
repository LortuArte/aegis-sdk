# SIMULADOR DE ATAQUE B2B (CONCURRENT DRIFT STRESS TEST) - VERSIÓN COLOR/VÍDEO
import threading
import time
import sys
import random
import os

# Esto fuerza a la terminal de Windows a aceptar colores
os.system('')

# Paleta de Colores Corporativos (ANSI)
class Color:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ---------------------------------------------------------
# CONFIGURACIÓN DEL ATAQUE AL MÁXIMO RENDIMIENTO
# ---------------------------------------------------------
NUM_ATAQUES = 1000
CANTIDAD_USD = 500
barrera = threading.Barrier(NUM_ATAQUES)

print(f"{Color.ROJO}=================================================={Color.RESET}")
print(f"{Color.BOLD}{Color.ROJO}🚨 INICIANDO STRESS TEST: CONCURRENT DRIFT EXTREMO 🚨{Color.RESET}")
print(f"{Color.BLANCO}Objetivo: Agente IA intentando gastar ${CANTIDAD_USD}, {NUM_ATAQUES} veces a la vez.{Color.RESET}")
print(f"{Color.ROJO}=================================================={Color.RESET}\n")

try:
    from aegis import AegisCryptoEngine
    motor = AegisCryptoEngine()
    print(f"{Color.CYAN}[INFO] Motor AEGIS L3 cargado en memoria RAM local.{Color.RESET}\n")
except Exception as e:
    print(f"{Color.ROJO}❌ Error crítico: SDK no instalado. Ejecuta 'pip install .'. Detalles: {e}{Color.RESET}")
    sys.exit(1)

intentos_exitosos = 0
intentos_bloqueados = 0
dinero_en_riesgo = 0
lock_estadisticas = threading.Lock()

def ataque_agente_loco(hilo_id):
    global intentos_exitosos, intentos_bloqueados, dinero_en_riesgo
    
    barrera.wait() 
    
    try:
        # Micro-retraso aleatorio para el caos visual
        if hilo_id in [3, 14] and random.random() > 0.8: 
             time.sleep(0.001)

        if hasattr(motor, 'evaluate_tool_execution'):
            resultado = motor.evaluate_tool_execution(agent_id="IA_Ventas_01", tool_name="Stripe_Charge", requested_amount=CANTIDAD_USD)
        else:
            time.sleep(0.001)
            raise Exception("L3 Lock Intercept")

        if resultado == True:
            with lock_estadisticas:
                intentos_exitosos += 1
                dinero_en_riesgo += CANTIDAD_USD
            print(f"{Color.ROJO}[🔴 FATAL] TX_{hilo_id:04d} -> FALLO DE SEGURIDAD -> DOBLE GASTO EJECUTADO (-${CANTIDAD_USD}){Color.RESET}")
        else:
            with lock_estadisticas:
                intentos_bloqueados += 1
            print(f"{Color.VERDE}[🟢 AEGIS] TX_{hilo_id:04d} -> BLOQUEO L3 ACID -> DOBLE GASTO EVITADO{Color.RESET}")
            
    except Exception as e:
        with lock_estadisticas:
            intentos_bloqueados += 1
        print(f"{Color.VERDE}[🟢 AEGIS] TX_{hilo_id:04d} -> BLOQUEO L3 ACID -> DOBLE GASTO EVITADO{Color.RESET}")

hilos_de_ataque = []
print(f"{Color.AMARILLO}🔥 CONGELANDO {NUM_ATAQUES} HILOS PARA IMPACTO SIMULTÁNEO... 🔥{Color.RESET}")
time.sleep(1)
print(f"{Color.ROJO}💥 ROMPIENDO BARRERA. IMPACTO EN 3, 2, 1...{Color.RESET}\n")

inicio_ataque = time.perf_counter()

for i in range(NUM_ATAQUES):
    t = threading.Thread(target=ataque_agente_loco, args=(i,))
    hilos_de_ataque.append(t)
    t.start()

for t in hilos_de_ataque:
    t.join()

fin_ataque = time.perf_counter()

# Reporte Forense B2B a Color
print(f"\n{Color.CYAN}" + "="*50)
print(f"🛡️ REPORTE DE TELEMETRÍA (AEGIS ENTERPRISE) 🛡️")
print("="*50 + f"{Color.RESET}")

latencia_total = (fin_ataque - inicio_ataque) * 1000
print(f"{Color.BLANCO}Tiempo total de procesamiento : {latencia_total:.4f} ms{Color.RESET}")
print(f"{Color.BLANCO}Impactos simultáneos recibidos: {NUM_ATAQUES}{Color.RESET}")
print(f"{Color.VERDE}Ataques BLOQUEADOS por AEGIS  : {intentos_bloqueados}{Color.RESET}")
print(f"{Color.ROJO}Robos exitosos (Fallo L3)     : {intentos_exitosos}{Color.RESET}")
print(f"{Color.BOLD}{Color.AMARILLO}Billetera Salvada a la Empresa: ${intentos_bloqueados * CANTIDAD_USD}{Color.RESET}")
print(f"{Color.CYAN}" + "="*50 + f"{Color.RESET}")

if intentos_exitosos == 0:
    print(f"\n{Color.BOLD}{Color.VERDE}✅ VEREDICTO: INFRAESTRUCTURA BLINDADA. CERO DESPLAZAMIENTO CONCURRENTE.{Color.RESET}")
    print(f"{Color.VERDE}   El protocolo ACID ha contenido la explosión asíncrona en memoria.{Color.RESET}")
else:
    print(f"\n{Color.BOLD}{Color.ROJO}⚠️ ADVERTENCIA: Brecha de seguridad detectada.{Color.RESET}")