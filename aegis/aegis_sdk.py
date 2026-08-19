# ==============================================================================
# AEGIS L3 ENGINE - SDK DE PRODUCCION CRIPTOGRAFICO
# Monetary safety + rollback + idempotency conflict + tool-call binding
# + fail-closed configured-key initialization
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


MONEY_QUANTUM = Decimal("0.000001")
MAX_DECIMAL_PLACES = 6


# ==============================================================================
# CRYPTO ENGINE
# ==============================================================================

class AegisCryptoEngine:
    """
    Motor criptografico interno de AEGIS.

    Hashing determinista y firmas Ed25519.
    """

    @staticmethod
    def ordenar_diccionario(datos: Any) -> Any:
        if isinstance(datos, dict):
            return {
                k: AegisCryptoEngine.ordenar_diccionario(datos[k])
                for k in sorted(datos.keys())
            }

        if isinstance(datos, list):
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
        return hashlib.sha256(
            json_string.encode("utf-8")
        ).digest()

    @staticmethod
    def firmar_hash(
        hash_bytes: bytes,
        clave_privada: ed25519.Ed25519PrivateKey
    ) -> str:
        firma_binaria = clave_privada.sign(hash_bytes)

        firma_b64 = base64.b64encode(
            firma_binaria
        ).decode("utf-8")

        return f"ed25519:{firma_b64}"

    @staticmethod
    def verificar_firma(
        hash_bytes: bytes,
        firma_string: str,
        clave_publica: ed25519.Ed25519PublicKey
    ) -> bool:
        try:
            if not isinstance(firma_string, str):
                return False

            if not firma_string.startswith("ed25519:"):
                return False

            firma_b64 = firma_string.split(":", 1)[1]

            firma_binaria = base64.b64decode(
                firma_b64,
                validate=True
            )

            clave_publica.verify(
                firma_binaria,
                hash_bytes
            )

            return True

        except (
            InvalidSignature,
            ValueError,
            TypeError
        ):
            return False


# ==============================================================================
# LOCAL POLICY GATE
# ==============================================================================

class AegisLocalPolicyGate:
    """
    Guardian local de politicas AEGIS.

    Flujo:

        validacion monetaria
        -> lock atomico process-local
        -> idempotencia
        -> control presupuestario
        -> payload determinista
        -> tool_call_id binding
        -> SHA-256
        -> Ed25519
        -> recibo verificable
        -> commit economico
        -> commit de idempotencia
        -> fail-closed
    """

    def __init__(
        self,
        private_key_b64: Optional[str] = None
    ):
        self._lock = threading.Lock()

        # ======================================================================
        # PROCESS-LOCAL LEDGER
        # ======================================================================

        self.ledger_data: Dict[str, Decimal] = {
            "did:key:langchain_test_agent": Decimal("50.00"),
            "did:key:aegis_final_demo_agent": Decimal("10.00"),
        }

        # ======================================================================
        # PROCESS-LOCAL IDEMPOTENCY REGISTRY
        # ======================================================================

        self.idempotencia_tx: Dict[str, Dict[str, Any]] = {}

        # ======================================================================
        # ED25519 KEY INITIALIZATION
        #
        # SECURITY POLICY
        #
        # 1. No configured key:
        #       Generate a new local Ed25519 key.
        #
        # 2. Valid configured key:
        #       Use exactly the configured identity.
        #
        # 3. Invalid configured key:
        #       Abort initialization.
        #
        # A configured cryptographic identity must never be silently replaced.
        # ======================================================================

        if private_key_b64 is None:
            self.private_key = (
                ed25519.Ed25519PrivateKey.generate()
            )

        else:
            try:
                private_key_bytes = base64.b64decode(
                    private_key_b64,
                    validate=True
                )

                self.private_key = (
                    ed25519.Ed25519PrivateKey.from_private_bytes(
                        private_key_bytes
                    )
                )

            except Exception as exc:
                raise ValueError(
                    "Invalid configured Ed25519 private key. "
                    "AEGIS startup aborted."
                ) from exc

        self.public_key = self.private_key.public_key()

    # ==========================================================================
    # PUBLIC KEY
    # ==========================================================================

    def obtener_clave_publica_b64(self) -> str:
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        return (
            "ed25519:"
            + base64.b64encode(pub_bytes).decode("utf-8")
        )

    # ==========================================================================
    # MONEY NORMALIZATION
    # ==========================================================================

    @staticmethod
    def _normalizar_amount(
        amount_usd: Any
    ) -> Decimal:
        """
        Normaliza cantidades monetarias de forma estricta.

        Reglas:
        - bool no permitido
        - NaN / Infinity no permitidos
        - amount <= 0 no permitido
        - mas de dos decimales no permitido
        """

        if isinstance(amount_usd, bool):
            raise ValueError(
                "amount_usd no puede ser booleano"
            )

        if isinstance(amount_usd, Decimal):
            amount = amount_usd

        else:
            amount = Decimal(
                str(amount_usd)
            )

        if not amount.is_finite():
            raise ValueError(
                "amount_usd debe ser finito"
            )

        if amount <= Decimal("0"):
            raise ValueError(
                "amount_usd debe ser mayor que cero"
            )

        if amount.as_tuple().exponent < -MAX_DECIMAL_PLACES:
            raise ValueError(
                "amount_usd no puede tener mas de 6 decimales"
            )

        return amount.quantize(
            MONEY_QUANTUM,
            rounding=ROUND_HALF_UP
        )

    # ==========================================================================
    # STANDARD FAIL-CLOSED DENY RECEIPT
    # ==========================================================================

    @staticmethod
    def _deny_receipt(
        agent_did: str,
        operation: str,
        tool_call_id: str,
        amount_usd: str,
        reason: str
    ) -> dict:
        return {
            "agent_did": agent_did,
            "operation": operation,
            "tool_call_id": tool_call_id,
            "amount_usd": amount_usd,
            "policy_decision": "deny",
            "policy_attenuations": [
                {
                    "field": reason,
                    "applied": True
                }
            ],
            "policy_signature": "error_no_signature",
            "action_ref": "0" * 64,
            "cached": False,
            "execution_permitted": False
        }

    # ==========================================================================
    # POLICY EVALUATION
    # ==========================================================================

    def evaluar_gasto(
        self,
        agent_did: str,
        operation: str,
        tool_call_id: str,
        amount_usd: Any
    ) -> dict:

        id_transaccion = (
            f"{agent_did}:{tool_call_id}"
        )

        # ======================================================================
        # 0. MONEY VALIDATION
        # ======================================================================

        try:
            amount = self._normalizar_amount(
                amount_usd
            )

        except (
            InvalidOperation,
            ValueError,
            TypeError
        ):
            return self._deny_receipt(
                agent_did=agent_did,
                operation=operation,
                tool_call_id=tool_call_id,
                amount_usd=str(amount_usd),
                reason="invalid_amount"
            )

        # ======================================================================
        # PROCESS-LOCAL ATOMIC SECTION
        # ======================================================================

        with self._lock:

            # ==================================================================
            # 1. IDEMPOTENCY
            # ==================================================================

            if id_transaccion in self.idempotencia_tx:

                recibo_historico = (
                    self.idempotencia_tx[
                        id_transaccion
                    ].copy()
                )

                same_operation = (
                    recibo_historico.get(
                        "operation"
                    )
                    == operation
                )

                same_amount = (
                    recibo_historico.get(
                        "amount_usd"
                    )
                    == f"{amount:.6f}"
                )

                same_tool_call_id = (
                    recibo_historico.get(
                        "tool_call_id"
                    )
                    == tool_call_id
                )

                # ==============================================================
                # CRITICO 2
                #
                # Reusing the same transaction identity with different economic
                # semantics is an explicit conflict, not a cache hit.
                # ==============================================================

                if not (
                    same_operation
                    and same_amount
                    and same_tool_call_id
                ):
                    return self._deny_receipt(
                        agent_did=agent_did,
                        operation=operation,
                        tool_call_id=tool_call_id,
                        amount_usd=f"{amount:.6f}",
                        reason="idempotency_conflict"
                    )

                recibo_historico[
                    "cached"
                ] = True

                recibo_historico[
                    "execution_permitted"
                ] = False

                return recibo_historico

            try:
                # ==============================================================
                # 2. READ CURRENT LEDGER
                # ==============================================================

                current_balance = (
                    self.ledger_data.get(
                        agent_did,
                        Decimal("0.00")
                    )
                )

                decision = "deny"
                attenuations = []

                # IMPORTANT:
                # No economic state is mutated here.
                pending_balance = current_balance

                # ==============================================================
                # 3. BUDGET DECISION
                # ==============================================================

                if current_balance >= amount:

                    pending_balance = (
                        current_balance
                        - amount
                    ).quantize(
                        MONEY_QUANTUM
                    )

                    decision = "allow"

                else:

                    attenuations = [
                        {
                            "field": "budget_exhausted",
                            "applied": True
                        }
                    ]

                # ==============================================================
                # 4. DETERMINISTIC AUTHORIZATION PAYLOAD
                #
                # CRITICO 3
                #
                # tool_call_id is inside the deterministic payload.
                # Therefore it is cryptographically bound to both action_ref
                # and policy_signature.
                # ==============================================================

                recibo_payload = {
                    "agent_did": agent_did,
                    "operation": operation,
                    "tool_call_id": tool_call_id,
                    "amount_usd": f"{amount:.6f}",
                    "policy_decision": decision,
                    "policy_attenuations": (
                        sorted(
                            attenuations,
                            key=lambda x: x["field"]
                        )
                        if attenuations
                        else []
                    )
                }

                # ==============================================================
                # 5. DETERMINISTIC SERIALIZATION
                # ==============================================================

                json_string = (
                    AegisCryptoEngine
                    .generar_string_determinista(
                        recibo_payload
                    )
                )

                # ==============================================================
                # 6. SHA-256 ACTION REFERENCE
                # ==============================================================

                hash_bytes = (
                    AegisCryptoEngine
                    .calcular_sha256(
                        json_string
                    )
                )

                # ==============================================================
                # 7. ED25519 SIGNATURE
                # ==============================================================

                firma = (
                    AegisCryptoEngine
                    .firmar_hash(
                        hash_bytes,
                        self.private_key
                    )
                )

                # ==============================================================
                # 8. AUDITABLE RECEIPT
                # ==============================================================

                recibo_final = (
                    recibo_payload.copy()
                )

                recibo_final[
                    "policy_signature"
                ] = firma

                recibo_final[
                    "action_ref"
                ] = hash_bytes.hex()

                recibo_final[
                    "cached"
                ] = False

                recibo_final[
                    "execution_permitted"
                ] = (
                    decision == "allow"
                )

                # ==============================================================
                # 9. ECONOMIC COMMIT
                #
                # CRITICO 1
                #
                # Economic state is committed ONLY AFTER:
                #
                # - policy evaluation
                # - deterministic payload generation
                # - SHA-256
                # - Ed25519 signature
                # - final receipt construction
                #
                # If signing or any previous stage raises an exception, execution
                # jumps to FAIL-CLOSED without modifying the balance.
                # ==============================================================

                if decision == "allow":

                    self.ledger_data[
                        agent_did
                    ] = pending_balance

                # ==============================================================
                # 10. IDEMPOTENCY COMMIT
                # ==============================================================

                self.idempotencia_tx[
                    id_transaccion
                ] = recibo_final.copy()

                return recibo_final

            except Exception:
                # ==============================================================
                # FAIL-CLOSED
                #
                # Internal failure before economic commit:
                #
                # - deny authorization
                # - no signature presented as valid
                # - no economic state mutation
                # - no idempotency commit
                # ==============================================================

                return self._deny_receipt(
                    agent_did=agent_did,
                    operation=operation,
                    tool_call_id=tool_call_id,
                    amount_usd=f"{amount:.6f}",
                    reason="internal_engine_fault"
                )