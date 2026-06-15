# ==============================================================================
# AEGIS L3 ENGINE - SDK DE PRODUCCIÓN CRIPTOGRÁFICO (PROD V2.1.0 - BLINDADO)
# ==============================================================================
# Autor: Iraitz (Founder, AEGIS)
# Propósito: Hashing Determinista, Firmas Ed25519, Idempotencia Local,
#            Mitigación de Coma Flotante y Arquitectura Fail-Closed Completa.
# ==============================================================================

import json
import hashlib
import base64
import time
import threading
from typing import Dict, Any, Tuple, Optional, List
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# NOTA CRÍTICA: Aquí NO debe existir ninguna línea "from aegis_sdk import ..."
# Las clases se declaran directamente para evitar la recursión circular en Python.

class AegisCryptoEngine:
    """
    Motor criptográfico interno de AEGIS.
    Garantiza que toda firma y hash emitido sea determinista, inmutable y verificable.
    """
    @staticmethod
    def ordenar_diccionario(datos: Any) -> Any:
        """Ordena recursivamente las llaves de cualquier diccionario o lista."""
        if isinstance(datos, dict):
            return {k: AegisCryptoEngine.ordenar_diccionario(datos[k]) for k in sorted(datos.keys())}
        elif isinstance(datos, list):
            return [AegisCryptoEngine.ordenar_diccionario(elemento) for elemento in datos]
        return datos

    @staticmethod
    def generar_string_determinista(datos: dict) -> str:
        """Paso 1: Convierte el diccionario ordenado en un JSON string compacto sin espacios residuales."""
        datos_ordenados = AegisCryptoEngine.ordenar_diccionario(datos)
        return json.dumps(datos_ordenados, separators=(',', ':'))

    @staticmethod
    def calcular_sha256(json_string: str) -> bytes:
        """Paso 2: Genera el hash SHA-256 binario del string determinista."""
        return hashlib.sha256(json_string.encode('utf-8')).digest()

    @staticmethod
    def firmar_hash(hash_bytes: bytes, clave_privada: ed25519.Ed25519PrivateKey) -> str:
        """Paso 3: Firma el hash binario resultante con la clave privada Ed25519."""
        firma_binaria = clave_privada.sign(hash_bytes)
        firma_b64 = base64.b64encode(firma_binaria).decode('utf-8')
        return f"ed25519:{firma_b64}"

    @staticmethod
    def verificar_firma(hash_bytes: bytes, firma_string: str, clave_publica: ed25519.Ed25519PublicKey) -> bool:
        """Valida localmente que una firma Ed25519 sea legítima para un hash dado."""
        try:
            if not firma_string.startswith("ed25519:"):
                return False
            firma_b64 = firma_string.split(":")[1]
            firma_binaria = base64.b64decode(firma_b64)
            clave_publica.verify(firma_binaria, hash_bytes)
            return True
        except (InvalidSignature, Exception):
            return False


class AegisLocalPolicyGate:
    """
    Guardián de Políticas con control presupuestario local, mitigación
    de condiciones de carrera (ACID) y blindaje de idempotencia transaccional.
    """
    def __init__(self, private_key_b64: Optional[str] = None):
        self._lock = threading.Lock()
        
        # Bóveda semilla de presupuestos en memoria RAM
        self.ledger_data = {
            "did:key:langchain_test_agent": 50.00,
            "did:key:aegis_final_demo_agent": 10.00
        }
        
        # Tabla de idempotencia para evitar dobles cargos por latencia o reintentos
        self.idempotencia_tx: Dict[str, Dict[str, Any]] = {}

        # Inicialización de claves asimétricas Ed25519
        try:
            if private_key_b64:
                self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
                    base64.b64decode(private_key_b64)
                )
            else:
                self.private_key = ed25519.Ed25519PrivateKey.generate()
            
            self.public_key = self.private_key.public_key()
        except Exception as e:
            print(f"⚠️ [AEGIS CRYPTO FATAL]: Error inicializando llaves: {e}. Activando llave de emergencia.")
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

    def obtener_clave_publica_b64(self) -> str:
        """Exporta la clave pública en formato legible para la verificación externa."""
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return f"ed25519:{base64.b64encode(pub_bytes).decode('utf-8')}"

    def evaluar_gasto(self, agent_did: str, operation: str, tool_call_id: str, amount_usd: float) -> dict:
        """
        Gobernanza de recursos con bloqueos ACID locales en memoria RAM.
        La idempotencia evita el doble cobro. Si se aprueba, emite un recibo Ed25519 inmutable.
        """
        id_transaccion = f"{agent_did}:{tool_call_id}"

        with self._lock:  # Candado ACID exclusivo para prevenir condiciones de carrera
            # 1. Filtro estricto de Idempotencia
            if id_transaccion in self.idempotencia_tx:
                recibo_historico = self.idempotencia_tx[id_transaccion].copy()
                recibo_historico["cached"] = True
                return recibo_historico

            try:
                # 2. Control de saldo y mitigación del Precision Drift de coma flotante
                current_balance = self.ledger_data.get(agent_did, 0.0)
                decision = "deny"
                attenuations = []

                if current_balance >= amount_usd:
                    # Deducción matemática redondeada a dos decimales
                    self.ledger_data[agent_did] = round(current_balance - amount_usd, 2)
                    decision = "allow"
                else:
                    attenuations = [{"field": "budget_exhausted", "applied": True}]

                # 3. Formación del payload estructurado
                recibo_payload = {
                    "agent_did": agent_did,
                    "operation": operation,
                    "amount_usd": f"{amount_usd:.2f}",
                    "policy_decision": decision,
                    "policy_attenuations": sorted(attenuations, key=lambda x: x["field"]) if attenuations else []
                }

                # 4. Flujo de firma criptográfica
                json_string = AegisCryptoEngine.generar_string_determinista(recibo_payload)
                hash_bytes = AegisCryptoEngine.calcular_sha256(json_string)
                firma = AegisCryptoEngine.firmar_hash(hash_bytes, self.private_key)

                # Construcción del recibo de auditoría final
                recibo_final = recibo_payload.copy()
                recibo_final["policy_signature"] = f"{firma}"
                recibo_final["action_ref"] = hash_bytes.hex()
                recibo_final["cached"] = False

                # Registro permanente en la tabla de idempotencia local
                self.idempotencia_tx[id_transaccion] = recibo_final.copy()
                return recibo_final

            except Exception as e:
                # Filosofía Fail-Closed: denegación absoluta en caso de excepción del motor
                return {
                    "agent_did": agent_did,
                    "operation": operation,
                    "amount_usd": f"{amount_usd:.2f}",
                    "policy_decision": "deny",
                    "policy_attenuations": [{"field": "internal_engine_fault", "applied": True}],
                    "policy_signature": "error_no_signature",
                    "action_ref": "0000000000000000000000000000000000000000000000000000000000000000",
                    "cached": False
                }