import io
import contextlib

from aegis import AegisLocalPolicyGate


print("\n=== AEGIS PRIVATE KEY FAILURE BEHAVIOR TEST ===")

INVALID_KEY = "THIS_IS_NOT_A_VALID_ED25519_PRIVATE_KEY"

captured_output = io.StringIO()

constructor_exception = None
gate = None

try:
    with contextlib.redirect_stdout(captured_output):
        gate = AegisLocalPolicyGate(
            private_key_b64=INVALID_KEY
        )

except Exception as exc:
    constructor_exception = exc


output = captured_output.getvalue()


print(
    "CONSTRUCTOR EXCEPTION:",
    type(constructor_exception).__name__
    if constructor_exception
    else "NONE"
)

print(
    "GATE CREATED:",
    gate is not None
)

print(
    "EMERGENCY KEY MESSAGE:",
    "Activando llave de emergencia" in output
)

if gate is not None:
    print(
        "PRIVATE KEY EXISTS:",
        hasattr(gate, "private_key")
    )

    print(
        "PUBLIC KEY EXISTS:",
        hasattr(gate, "public_key")
    )

    try:
        public_key = gate.obtener_clave_publica_b64()

        print(
            "PUBLIC KEY GENERATED:",
            public_key.startswith("ed25519:")
        )

    except Exception:
        print(
            "PUBLIC KEY GENERATED:",
            False
        )


fail_closed_startup = (
    constructor_exception is not None
)


silent_recovery = (
    constructor_exception is None
    and gate is not None
)


print(
    "\nFAIL-CLOSED STARTUP:",
    fail_closed_startup
)

print(
    "EMERGENCY RECOVERY:",
    silent_recovery
)


if fail_closed_startup:
    print("SECURITY MODEL: INVALID KEY REJECTED")
    print("RESULT: PASS")

else:
    print("SECURITY MODEL: INVALID KEY REPLACED")
    print("RESULT: REVIEW REQUIRED")