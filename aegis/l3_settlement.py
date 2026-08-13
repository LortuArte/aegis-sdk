import sqlite3
import threading
import time

from decimal import Decimal, InvalidOperation
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import ed25519

from .aegis_sdk import AegisCryptoEngine


CENT = Decimal("0.01")
OPERATION_PREFIX = "l3_transfer:"


class AegisL3Settlement:
    """
    Minimal isolated AEGIS L3 settlement engine.

    Security properties:

    - requires valid AEGIS signed authorization
    - buyer bound to signed agent_did
    - seller bound to signed operation
    - amount bound to signed payload
    - tool_call_id bound to signed payload
    - atomic SQLite transaction
    - integer cents, not float
    - settlement idempotency
    - rollback on persistence failure
    - process-local concurrency lock

    This is intentionally NOT a distributed consensus engine.
    """

    def __init__(
        self,
        db_path: str = ":memory:"
    ):
        self.db_path = db_path
        self._lock = threading.Lock()

        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            isolation_level=None
        )

        self.conn.row_factory = sqlite3.Row

        self.conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        if db_path != ":memory:":
            self.conn.execute(
                "PRAGMA journal_mode = WAL"
            )

        self._initialize_schema()

    # ======================================================================
    # SCHEMA
    # ======================================================================

    def _initialize_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                agent_id TEXT PRIMARY KEY,
                balance_cents INTEGER NOT NULL
                    CHECK(balance_cents >= 0)
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settlements (
                settlement_id TEXT PRIMARY KEY,
                tool_call_id TEXT UNIQUE NOT NULL,
                buyer_id TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL
                    CHECK(amount_cents > 0),
                action_ref TEXT NOT NULL,
                created_ns INTEGER NOT NULL
            )
            """
        )

    # ======================================================================
    # MONEY
    # ======================================================================

    @staticmethod
    def _usd_to_cents(
        amount_usd
    ) -> int:
        try:
            amount = Decimal(
                str(amount_usd)
            )

        except InvalidOperation as exc:
            raise ValueError(
                "Invalid monetary amount"
            ) from exc

        if not amount.is_finite():
            raise ValueError(
                "Amount must be finite"
            )

        if amount <= Decimal("0"):
            raise ValueError(
                "Amount must be positive"
            )

        if amount.as_tuple().exponent < -2:
            raise ValueError(
                "Amount cannot exceed two decimals"
            )

        normalized = amount.quantize(CENT)

        return int(
            normalized * 100
        )

    @staticmethod
    def _cents_to_usd(
        cents: int
    ) -> str:
        return f"{Decimal(cents) / 100:.2f}"

    # ======================================================================
    # ACCOUNT SETUP
    # ======================================================================

    def seed_account(
        self,
        agent_id: str,
        balance_usd
    ):
        cents = self._usd_to_cents(
            balance_usd
        )

        with self._lock:
            self.conn.execute(
                """
                INSERT INTO accounts (
                    agent_id,
                    balance_cents
                )
                VALUES (?, ?)
                ON CONFLICT(agent_id)
                DO UPDATE SET
                    balance_cents = excluded.balance_cents
                """,
                (
                    agent_id,
                    cents
                )
            )

    def get_balance(
        self,
        agent_id: str
    ) -> Decimal:
        row = self.conn.execute(
            """
            SELECT balance_cents
            FROM accounts
            WHERE agent_id = ?
            """,
            (agent_id,)
        ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown account: {agent_id}"
            )

        return (
            Decimal(
                row["balance_cents"]
            )
            / Decimal("100")
        ).quantize(CENT)

    # ======================================================================
    # AUTHORIZATION VERIFICATION
    # ======================================================================

    @staticmethod
    def _authorization_payload(
        receipt: dict
    ) -> dict:
        return {
            "agent_did":
                receipt["agent_did"],

            "operation":
                receipt["operation"],

            "tool_call_id":
                receipt["tool_call_id"],

            "amount_usd":
                receipt["amount_usd"],

            "policy_decision":
                receipt["policy_decision"],

            "policy_attenuations":
                receipt["policy_attenuations"],
        }

    @classmethod
    def _verify_authorization(
        cls,
        receipt: dict,
        public_key: ed25519.Ed25519PublicKey
    ):
        required = {
            "agent_did",
            "operation",
            "tool_call_id",
            "amount_usd",
            "policy_decision",
            "policy_attenuations",
            "policy_signature",
            "action_ref",
        }

        missing = (
            required
            - set(receipt.keys())
        )

        if missing:
            raise ValueError(
                "Incomplete authorization receipt"
            )

        if (
            receipt["policy_decision"]
            != "allow"
        ):
            raise ValueError(
                "Authorization is not ALLOW"
            )

        operation = receipt[
            "operation"
        ]

        if not operation.startswith(
            OPERATION_PREFIX
        ):
            raise ValueError(
                "Authorization is not an L3 transfer"
            )

        seller_id = operation[
            len(OPERATION_PREFIX):
        ].strip()

        if not seller_id:
            raise ValueError(
                "Missing signed seller identity"
            )

        payload = (
            cls._authorization_payload(
                receipt
            )
        )

        deterministic = (
            AegisCryptoEngine
            .generar_string_determinista(
                payload
            )
        )

        hash_bytes = (
            AegisCryptoEngine
            .calcular_sha256(
                deterministic
            )
        )

        if (
            receipt["action_ref"]
            != hash_bytes.hex()
        ):
            raise ValueError(
                "Authorization action_ref mismatch"
            )

        valid_signature = (
            AegisCryptoEngine
            .verificar_firma(
                hash_bytes,
                receipt[
                    "policy_signature"
                ],
                public_key
            )
        )

        if not valid_signature:
            raise ValueError(
                "Invalid authorization signature"
            )

        return {
            "buyer_id":
                receipt["agent_did"],

            "seller_id":
                seller_id,

            "amount_cents":
                cls._usd_to_cents(
                    receipt["amount_usd"]
                ),

            "tool_call_id":
                receipt["tool_call_id"],

            "action_ref":
                receipt["action_ref"],
        }

    # ======================================================================
    # FAILURE-INJECTION HOOK
    #
    # Tests may monkeypatch this.
    # Production behavior is no-op.
    # ======================================================================

    def _after_debit_hook(self):
        return None

    # ======================================================================
    # ATOMIC SETTLEMENT
    # ======================================================================

    def settle(
        self,
        authorization_receipt: dict,
        authorization_public_key:
            ed25519.Ed25519PublicKey
    ) -> dict:

        authorization = (
            self._verify_authorization(
                authorization_receipt,
                authorization_public_key
            )
        )

        buyer_id = authorization[
            "buyer_id"
        ]

        seller_id = authorization[
            "seller_id"
        ]

        amount_cents = authorization[
            "amount_cents"
        ]

        tool_call_id = authorization[
            "tool_call_id"
        ]

        action_ref = authorization[
            "action_ref"
        ]

        if buyer_id == seller_id:
            raise ValueError(
                "Buyer and seller must differ"
            )

        settlement_id = (
            f"l3:{action_ref}"
        )

        with self._lock:

            # ==============================================================
            # IDEMPOTENCY
            # ==============================================================

            existing = self.conn.execute(
                """
                SELECT *
                FROM settlements
                WHERE tool_call_id = ?
                """,
                (tool_call_id,)
            ).fetchone()

            if existing is not None:

                if (
                    existing["action_ref"]
                    != action_ref
                ):
                    raise ValueError(
                        "L3 idempotency conflict"
                    )

                return {
                    "settlement_id":
                        existing[
                            "settlement_id"
                        ],

                    "status":
                        "SETTLED",

                    "buyer_id":
                        existing[
                            "buyer_id"
                        ],

                    "seller_id":
                        existing[
                            "seller_id"
                        ],

                    "amount_usd":
                        self._cents_to_usd(
                            existing[
                                "amount_cents"
                            ]
                        ),

                    "action_ref":
                        existing[
                            "action_ref"
                        ],

                    "cached":
                        True,
                }

            # ==============================================================
            # TRANSACTION START
            # ==============================================================

            try:
                self.conn.execute(
                    "BEGIN IMMEDIATE"
                )

                buyer = self.conn.execute(
                    """
                    SELECT balance_cents
                    FROM accounts
                    WHERE agent_id = ?
                    """,
                    (buyer_id,)
                ).fetchone()

                seller = self.conn.execute(
                    """
                    SELECT balance_cents
                    FROM accounts
                    WHERE agent_id = ?
                    """,
                    (seller_id,)
                ).fetchone()

                if buyer is None:
                    raise ValueError(
                        "Unknown buyer"
                    )

                if seller is None:
                    raise ValueError(
                        "Unknown seller"
                    )

                buyer_balance = buyer[
                    "balance_cents"
                ]

                seller_balance = seller[
                    "balance_cents"
                ]

                if (
                    buyer_balance
                    < amount_cents
                ):
                    raise ValueError(
                        "Insufficient settlement balance"
                    )

                new_buyer_balance = (
                    buyer_balance
                    - amount_cents
                )

                new_seller_balance = (
                    seller_balance
                    + amount_cents
                )

                # ==========================================================
                # DEBIT
                # ==========================================================

                self.conn.execute(
                    """
                    UPDATE accounts
                    SET balance_cents = ?
                    WHERE agent_id = ?
                    """,
                    (
                        new_buyer_balance,
                        buyer_id
                    )
                )

                # Fault injection point.
                self._after_debit_hook()

                # ==========================================================
                # CREDIT
                # ==========================================================

                self.conn.execute(
                    """
                    UPDATE accounts
                    SET balance_cents = ?
                    WHERE agent_id = ?
                    """,
                    (
                        new_seller_balance,
                        seller_id
                    )
                )

                # ==========================================================
                # IMMUTABLE SETTLEMENT RECORD
                # ==========================================================

                self.conn.execute(
                    """
                    INSERT INTO settlements (
                        settlement_id,
                        tool_call_id,
                        buyer_id,
                        seller_id,
                        amount_cents,
                        action_ref,
                        created_ns
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        settlement_id,
                        tool_call_id,
                        buyer_id,
                        seller_id,
                        amount_cents,
                        action_ref,
                        time.time_ns()
                    )
                )

                self.conn.execute(
                    "COMMIT"
                )

                return {
                    "settlement_id":
                        settlement_id,

                    "status":
                        "SETTLED",

                    "buyer_id":
                        buyer_id,

                    "seller_id":
                        seller_id,

                    "amount_usd":
                        self._cents_to_usd(
                            amount_cents
                        ),

                    "action_ref":
                        action_ref,

                    "cached":
                        False,
                }

            except Exception:
                try:
                    self.conn.execute(
                        "ROLLBACK"
                    )
                except sqlite3.Error:
                    pass

                raise

    # ======================================================================
    # INTROSPECTION
    # ======================================================================

    def settlement_count(self) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM settlements
            """
        ).fetchone()

        return int(
            row["count"]
        )

    def close(self):
        self.conn.close()