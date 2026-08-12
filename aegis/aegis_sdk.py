# ==============================================================================
# AEGIS L3 ENGINE - SDK DE PRODUCCIÓN CRIPTOGRÁFICO
# Monetary safety patch: Decimal
# ==============================================================================

import json
import hashlib
import base64
import threading
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


CENT = Decimal("0.01")


class AegisCryptoEngine:
    """
    Motor criptográfico interno de AEGIS.
    Hashing determinista y firmas Ed25519.
    """

    @staticmethod
    def ordenar_diccionario(datos: Any) -> Any:
        if isinstance(datos, dict):
            return {
                k: AegisCryptoEngine.ordenar_diccionario(datos[k])
                for k in sorted(datos.keys())
            }
        elif isinstance(datos, list):
            return [
                AegisCryptoEngine.ordenar_diccionario(elemento)
                for elemento in datos
            ]
        return datos

    @staticmethod
    def generar_string_determinista(datos: dict) -> str:
        datos_ordenados = AegisCryptoEngine.ordenar_diccionario(datos)
        return json.dumps(
            datos_ordenados,
            separators=(",", ":"),
            ensure_ascii=False
        )

    @staticmethod
    def calcular_sha256(json_string: str) -> bytes:
        return hashlib.sha256(json_string.encode("utf-8")).digest()

    @staticmethod
    def firmar_hash(
        hash_bytes: bytes,
        clave_privada: ed25519.Ed25519PrivateKey
    ) -> str:
        firma_binaria = clave_privada.sign(hash_bytes)
        firma_b64 = base64.b64encode(firma_binaria).decode("utf-8")
        return f"ed25519:{firma_b64}"

    @staticmethod
    def verificar_firma(
        hash_bytes: bytes,
        firma_string: str,
        clave_publica: ed25519.Ed25519PublicKey
    ) -> bool:
        try:
            if not firma_string.startswith("ed25519:"):
                return False

            firma_b64 = firma_string.split(":", 1)[1]
            firma_binaria = base64.b64decode(firma_b64)

            clave_publica.verify(firma_binaria, hash_bytes)
            return True

        except (InvalidSignature, ValueError, TypeError):
            return False


class AegisLocalPolicyGate:
    """
    Guardián de políticas AEGIS.

    Cadena de seguridad:
        validación monetaria
        -> idempotencia
        -> lock atómico
        -> control presupuestario
        -> payload determinista
        -> SHA-256
        -> Ed25519
        -> recibo verificable
        -> fail-closed
    """

    def __init__(self, private_key_b64: Optional[str] = None):
        self._lock = threading.Lock()

        # Ledger monetario exacto.
        self.ledger_data: Dict[str, Decimal] = {
            "did:key:langchain_test_agent": Decimal("50.00"),
            "did:key:aegis_final_demo_agent": Decimal("10.00"),
        }

        # Protección contra replay / doble ejecución.
        self.idempotencia_tx: Dict[str, Dict[str, Any]] = {}

        try:
            if private_key_b64:
                self.private_key = (
                    ed25519.Ed25519PrivateKey.from_private_bytes(
                        base64.b64decode(private_key_b64)
                    )
                )
            else:
                self.private_key = ed25519.Ed25519PrivateKey.generate()

            self.public_key = self.private_key.public_key()

        except Exception as e:
            print(
                f"[AEGIS CRYPTO FATAL]: Error inicializando llaves: {e}. "
                "Activando llave de emergencia."
            )

            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

    def obtener_clave_publica_b64(self) -> str:
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        return (
            "ed25519:"
            + base64.b64encode(pub_bytes).decode("utf-8")
        )

    @staticmethod
    def _normalizar_amount(amount_usd: Any) -> Decimal:
        """
        Convierte la cantidad recibida a Decimal usando representación textual.

        Se evita Decimal(float) porque conservaría el error binario del float.
        """

        if isinstance(amount_usd, bool):
            raise ValueError("amount_usd no puede ser booleano")

        if isinstance(amount_usd, Decimal):
            amount = amount_usd
        else:
            amount = Decimal(str(amount_usd))

        if not amount.is_finite():
            raise ValueError("amount_usd debe ser finito")

        if amount <= Decimal("0"):
            raise ValueError("amount_usd debe ser mayor que cero")

        return amount.quantize(CENT, rounding=ROUND_HALF_UP)

    def evaluar_gasto(
        self,
        agent_did: str,
        operation: str,
        tool_call_id: str,
        amount_usd: Any
    ) -> dict:

        id_transaccion = f"{agent_did}:{tool_call_id}"

        try:
            amount = self._normalizar_amount(amount_usd)
        except (InvalidOperation, ValueError, TypeError):
            return {
                "agent_did": agent_did,
                "operation": operation,
                "amount_usd": str(amount_usd),
                "policy_decision": "deny",
                "policy_attenuations": [
                    {
                        "field": "invalid_amount",
                        "applied": True
                    }
                ],
                "policy_signature": "error_no_signature",
                "action_ref": "0" * 64,
                "cached": False
            }

        with self._lock:

            # ==============================================================
            # 1. IDEMPOTENCIA
            # ==============================================================

            if id_transaccion in self.idempotencia_tx:
                recibo_historico = self.idempotencia_tx[
                    id_transaccion
                ].copy()

                recibo_historico["cached"] = True
                return recibo_historico

            try:
                # ==========================================================
                # 2. CONTROL ATÓMICO DEL LEDGER
                # ==========================================================

                current_balance = self.ledger_data.get(
                    agent_did,
                    Decimal("0.00")
                )

                decision = "deny"
                attenuations = []

                if current_balance >= amount:

                    new_balance = (
                        current_balance - amount
                    ).quantize(CENT)

                    self.ledger_data[agent_did] = new_balance
                    decision = "allow"

                else:

                    attenuations = [
                        {
                            "field": "budget_exhausted",
                            "applied": True
                        }
                    ]

                # ==========================================================
                # 3. PAYLOAD DETERMINISTA
                # ==============================================================

                recibo_payload = {
                    "agent_did": agent_did,
                    "operation": operation,
                    "amount_usd": f"{amount:.2f}",
                    "policy_decision": decision,
                    "policy_attenuations": sorted(
                        attenuations,
                        key=lambda x: x["field"]
                    )
                    if attenuations
                    else []
                }

                # ==========================================================
                # 4. HASH
                # ==============================================================

                json_string = (
                    AegisCryptoEngine.generar_string_determinista(
                        recibo_payload
                    )
                )

                hash_bytes = (
                    AegisCryptoEngine.calcular_sha256(
                        json_string
                    )
                )

                # ==========================================================
                # 5. FIRMA Ed25519
                # ==============================================================

                firma = AegisCryptoEngine.firmar_hash(
                    hash_bytes,
                    self.private_key
                )

                # ==========================================================
                # 6. RECIBO AUDITABLE
                # ==============================================================

                recibo_final = recibo_payload.copy()

                recibo_final["policy_signature"] = firma
                recibo_final["action_ref"] = hash_bytes.hex()
                recibo_final["cached"] = False

                # ==========================================================
                # 7. REGISTRO DE IDEMPOTENCIA
                # ==============================================================

                self.idempotencia_tx[id_transaccion] = (
                    recibo_final.copy()
                )

                return recibo_final

            except Exception:
                # ==========================================================
                # FAIL-CLOSED
                # ==============================================================

                return {
                    "agent_did": agent_did,
                    "operation": operation,
                    "amount_usd": f"{amount:.2f}",
                    "policy_decision": "deny",
                    "policy_attenuations": [
                        {
                            "field": "internal_engine_fault",
                            "applied": True
                        }
                    ],
                    "policy_signature": "error_no_signature",
                    "action_ref": "0" * 64,
                    "cached": False
                }