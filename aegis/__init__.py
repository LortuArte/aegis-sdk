from .aegis_sdk import AegisCryptoEngine, AegisLocalPolicyGate
from .l3_settlement import AegisL3Settlement

__version__ = "3.1.0"

# Backward-compatible alias
version = __version__

__all__ = [
    "AegisCryptoEngine",
    "AegisLocalPolicyGate",
    "AegisL3Settlement",
]