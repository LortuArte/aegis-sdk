import gc
import io
import os
import statistics
import tempfile
import threading
import time

from contextlib import redirect_stdout
from decimal import Decimal

from aegis import AegisLocalPolicyGate
from aegis.l3_settlement import AegisL3Settlement


# ==============================================================================
# AEGIS FINAL PERFORMANCE EVIDENCE
#
# PURPOSE
#
# Produce one reproducible benchmark separating:
#
# 1. Timer overhead
# 2. Isolated economic decision primitive
# 3. Idempotency cache-hit
# 4. Full signed authorization
# 5. L3 settlement using SQLite :memory:
# 6. L3 settlement using a real SQLite file
# 7. Python print/write overhead
# 8. Intentional sleep contamination
#
# IMPORTANT
#
# This benchmark DOES NOT claim to measure:
#
# - Internet latency
# - Render round-trip
# - multi-node coordination
# - Redis
# - PostgreSQL
# - blockchain settlement
# - Stripe settlement
#
# Those must be benchmarked separately if/when they exist in the tested path.
# ==============================================================================


print()
print("=" * 72)
print("AEGIS FINAL PERFORMANCE EVIDENCE")
print("=" * 72)


# ==============================================================================
# CONFIGURATION
# ==============================================================================

TIMER_SAMPLES = 20_000

DECISION_WARMUP = 5_000
DECISION_SAMPLES = 50_000

CACHE_WARMUP = 1_000
CACHE_SAMPLES = 10_000

SIGNED_WARMUP = 1_000
SIGNED_SAMPLES = 10_000

L3_WARMUP = 100
L3_SAMPLES = 2_000

PRINT_SAMPLES = 10_000

SLEEP_SAMPLES = 250
SLEEP_SECONDS = 0.001

CENT = Decimal("0.01")


# ==============================================================================
# STATISTICS
# ==============================================================================

def percentile(values, pct):
    ordered = sorted(values)

    index = int(
        (pct / 100)
        * (len(ordered) - 1)
    )

    return ordered[index]


def stats(values_ns):
    return {
        "samples": len(values_ns),
        "min": min(values_ns),
        "median": statistics.median(values_ns),
        "mean": statistics.mean(values_ns),
        "p95": percentile(values_ns, 95),
        "p99": percentile(values_ns, 99),
        "max": max(values_ns),
    }


def ns_to_us(value):
    return value / 1_000


def ns_to_ms(value):
    return value / 1_000_000


def print_metric(
    name,
    values_ns
):
    result = stats(values_ns)

    print()
    print(f"=== {name} ===")
    print("SAMPLES:", result["samples"])

    for label in (
        "min",
        "median",
        "mean",
        "p95",
        "p99",
        "max",
    ):
        value = result[label]

        print(
            f"{label.upper():7}: "
            f"{value:.0f} ns | "
            f"{ns_to_us(value):.3f} us | "
            f"{ns_to_ms(value):.6f} ms"
        )

    return result


def measure(function, samples):
    measurements = []

    for _ in range(samples):

        start = time.perf_counter_ns()

        function()

        end = time.perf_counter_ns()

        measurements.append(
            end - start
        )

    return measurements


# ==============================================================================
# 0. TIMER OVERHEAD
# ==============================================================================

timer_values = []

for _ in range(TIMER_SAMPLES):

    start = time.perf_counter_ns()
    end = time.perf_counter_ns()

    timer_values.append(
        end - start
    )


timer_stats = print_metric(
    "0. PERF_COUNTER_NS OVERHEAD",
    timer_values
)


# ==============================================================================
# 1. ISOLATED DECISION PRIMITIVE
#
# IMPORTANT:
#
# This intentionally isolates:
#
# - threading.Lock acquisition
# - Decimal comparison
# - Decimal subtraction
# - Decimal quantization
#
# It is NOT the complete AegisLocalPolicyGate method.
# ==============================================================================

decision_lock = threading.Lock()

decision_balance = Decimal(
    "1000000.00"
)

decision_amount = Decimal(
    "0.01"
)


def isolated_decision():

    with decision_lock:

        if (
            decision_balance
            >= decision_amount
        ):

            new_balance = (
                decision_balance
                - decision_amount
            ).quantize(
                CENT
            )

            return (
                "allow",
                new_balance
            )

        return (
            "deny",
            decision_balance
        )


for _ in range(
    DECISION_WARMUP
):
    isolated_decision()


decision_values = measure(
    isolated_decision,
    DECISION_SAMPLES
)


decision_stats = print_metric(
    "1. ISOLATED ECONOMIC DECISION PRIMITIVE",
    decision_values
)


# ==============================================================================
# 2. IDEMPOTENCY CACHE-HIT
# ==============================================================================

cache_gate = AegisLocalPolicyGate()

CACHE_AGENT = (
    "did:key:final-benchmark-cache"
)

cache_gate.ledger_data[
    CACHE_AGENT
] = Decimal("100.00")


initial_cache_receipt = (
    cache_gate.evaluar_gasto(
        agent_did=CACHE_AGENT,
        operation="benchmark_cache",
        tool_call_id="cache-static-id",
        amount_usd="1.00",
    )
)


if (
    initial_cache_receipt[
        "policy_decision"
    ]
    != "allow"
):
    raise RuntimeError(
        "Unable to initialize cache benchmark"
    )


def cached_authorization():

    receipt = (
        cache_gate.evaluar_gasto(
            agent_did=CACHE_AGENT,
            operation="benchmark_cache",
            tool_call_id="cache-static-id",
            amount_usd="1.00",
        )
    )

    if receipt.get(
        "cached"
    ) is not True:
        raise RuntimeError(
            "Expected idempotency cache hit"
        )


for _ in range(
    CACHE_WARMUP
):
    cached_authorization()


cache_values = measure(
    cached_authorization,
    CACHE_SAMPLES
)


cache_stats = print_metric(
    "2. IDEMPOTENCY CACHE-HIT",
    cache_values
)


# ==============================================================================
# 3. FULL SIGNED AUTHORIZATION PATH
#
# This calls the real AegisLocalPolicyGate.evaluar_gasto().
#
# Includes:
#
# - monetary validation
# - process-local lock
# - idempotency lookup
# - budget decision
# - deterministic payload
# - tool_call_id binding
# - SHA-256
# - Ed25519 signature
# - receipt construction
# - economic commit
# - idempotency commit
# ==============================================================================

signed_gate = AegisLocalPolicyGate()

SIGNED_AGENT = (
    "did:key:final-benchmark-signed"
)

signed_gate.ledger_data[
    SIGNED_AGENT
] = Decimal(
    "1000000.00"
)


for index in range(
    SIGNED_WARMUP
):

    receipt = (
        signed_gate.evaluar_gasto(
            agent_did=SIGNED_AGENT,
            operation="benchmark_signed",
            tool_call_id=(
                f"signed-warmup-{index}"
            ),
            amount_usd="0.01",
        )
    )

    if (
        receipt[
            "policy_decision"
        ]
        != "allow"
    ):
        raise RuntimeError(
            "Signed warmup unexpectedly denied"
        )


signed_values = []


for index in range(
    SIGNED_SAMPLES
):

    start = time.perf_counter_ns()

    receipt = (
        signed_gate.evaluar_gasto(
            agent_did=SIGNED_AGENT,
            operation="benchmark_signed",
            tool_call_id=(
                f"signed-final-{index}"
            ),
            amount_usd="0.01",
        )
    )

    end = time.perf_counter_ns()

    if (
        receipt[
            "policy_decision"
        ]
        != "allow"
    ):
        raise RuntimeError(
            "Signed benchmark unexpectedly denied"
        )

    if (
        receipt.get("cached")
        is not False
    ):
        raise RuntimeError(
            "Fresh authorization unexpectedly cached"
        )

    signed_values.append(
        end - start
    )


signed_stats = print_metric(
    "3. FULL SIGNED AUTHORIZATION PATH",
    signed_values
)


# ==============================================================================
# L3 RECEIPT GENERATOR
# ==============================================================================

def prepare_l3_receipts(
    prefix,
    samples
):

    gate = AegisLocalPolicyGate()

    buyer = (
        f"did:key:{prefix}-buyer"
    )

    seller = (
        f"did:key:{prefix}-seller"
    )

    gate.ledger_data[
        buyer
    ] = Decimal(
        "1000000.00"
    )

    receipts = []

    total = (
        samples
        + L3_WARMUP
    )

    for index in range(total):

        receipt = gate.evaluar_gasto(
            agent_did=buyer,
            operation=(
                f"l3_transfer:{seller}"
            ),
            tool_call_id=(
                f"{prefix}-{index}"
            ),
            amount_usd="0.01",
        )

        if (
            receipt[
                "policy_decision"
            ]
            != "allow"
        ):
            raise RuntimeError(
                "Unable to prepare L3 authorization"
            )

        receipts.append(
            receipt
        )

    return (
        gate,
        buyer,
        seller,
        receipts
    )


# ==============================================================================
# 4. L3 SQLITE :MEMORY: SETTLEMENT
#
# IMPORTANT:
#
# Authorization generation is deliberately OUTSIDE the measured region.
#
# We measure only:
#
# signed receipt verification
# -> SQLite BEGIN IMMEDIATE
# -> account reads
# -> debit
# -> credit
# -> immutable settlement INSERT
# -> COMMIT
# ==============================================================================

(
    l3_memory_gate,
    l3_memory_buyer,
    l3_memory_seller,
    l3_memory_receipts,
) = prepare_l3_receipts(
    "memory-l3",
    L3_SAMPLES
)


l3_memory = (
    AegisL3Settlement(
        ":memory:"
    )
)


l3_memory.seed_account(
    l3_memory_buyer,
    "1000.00"
)

l3_memory.seed_account(
    l3_memory_seller,
    "0.01"
)


for index in range(
    L3_WARMUP
):

    result = (
        l3_memory.settle(
            l3_memory_receipts[
                index
            ],
            l3_memory_gate.public_key
        )
    )

    if (
        result["status"]
        != "SETTLED"
    ):
        raise RuntimeError(
            "L3 memory warmup failed"
        )


l3_memory_values = []


for index in range(
    L3_WARMUP,
    L3_WARMUP
    + L3_SAMPLES
):

    start = time.perf_counter_ns()

    result = (
        l3_memory.settle(
            l3_memory_receipts[
                index
            ],
            l3_memory_gate.public_key
        )
    )

    end = time.perf_counter_ns()

    if (
        result["status"]
        != "SETTLED"
    ):
        raise RuntimeError(
            "L3 memory settlement failed"
        )

    l3_memory_values.append(
        end - start
    )


l3_memory_stats = print_metric(
    "4. L3 SQLITE IN-MEMORY SETTLEMENT",
    l3_memory_values
)


l3_memory.close()


# ==============================================================================
# 5. L3 SQLITE FILE-BACKED SETTLEMENT
#
# Uses a real temporary SQLite database file.
#
# This is a persistence benchmark.
#
# It still does NOT equal:
#
# - Render network latency
# - remote database latency
# - distributed settlement
# ==============================================================================

(
    l3_file_gate,
    l3_file_buyer,
    l3_file_seller,
    l3_file_receipts,
) = prepare_l3_receipts(
    "file-l3",
    L3_SAMPLES
)


temporary_database = tempfile.NamedTemporaryFile(
    suffix=".sqlite3",
    delete=False
)

temporary_database_path = (
    temporary_database.name
)

temporary_database.close()


try:

    l3_file = AegisL3Settlement(
        temporary_database_path
    )


    l3_file.seed_account(
        l3_file_buyer,
        "1000.00"
    )

    l3_file.seed_account(
        l3_file_seller,
        "0.01"
    )


    for index in range(
        L3_WARMUP
    ):

        result = (
            l3_file.settle(
                l3_file_receipts[
                    index
                ],
                l3_file_gate.public_key
            )
        )

        if (
            result["status"]
            != "SETTLED"
        ):
            raise RuntimeError(
                "L3 file warmup failed"
            )


    l3_file_values = []


    for index in range(
        L3_WARMUP,
        L3_WARMUP
        + L3_SAMPLES
    ):

        start = (
            time.perf_counter_ns()
        )

        result = (
            l3_file.settle(
                l3_file_receipts[
                    index
                ],
                l3_file_gate.public_key
            )
        )

        end = (
            time.perf_counter_ns()
        )

        if (
            result["status"]
            != "SETTLED"
        ):
            raise RuntimeError(
                "L3 file settlement failed"
            )

        l3_file_values.append(
            end - start
        )


    l3_file_stats = print_metric(
        "5. L3 SQLITE FILE-BACKED SETTLEMENT",
        l3_file_values
    )


    l3_file.close()


finally:

    try:
        os.remove(
            temporary_database_path
        )

    except OSError:
        pass


# ==============================================================================
# 6. PRINT OVERHEAD
#
# We deliberately DO NOT print 10,000 benchmark lines to the user's terminal.
#
# Instead we compare:
#
# - a no-op
# - Python print formatting/write directed to os.devnull
#
# This demonstrates that print is work and belongs OUTSIDE hot-path timing.
#
# It does NOT claim to measure every terminal/console implementation.
# ==============================================================================

def no_print():
    return None


with open(
    os.devnull,
    "w",
    encoding="utf-8"
) as devnull:

    def print_to_devnull():
        print(
            "AEGIS_BENCHMARK_EVENT",
            file=devnull
        )


    no_print_values = measure(
        no_print,
        PRINT_SAMPLES
    )


    print_values = measure(
        print_to_devnull,
        PRINT_SAMPLES
    )


no_print_stats = print_metric(
    "6A. NO-PRINT BASELINE",
    no_print_values
)


print_stats = print_metric(
    "6B. PRINT WRITE TO DEVNULL",
    print_values
)


print_overhead_median = (
    print_stats["median"]
    - no_print_stats["median"]
)


print()
print(
    "PRINT MEDIAN ADDED COST:",
    f"{print_overhead_median:.0f} ns | "
    f"{ns_to_us(print_overhead_median):.3f} us | "
    f"{ns_to_ms(print_overhead_median):.6f} ms"
)


# ==============================================================================
# 7. SLEEP CONTAMINATION
#
# Intentional sleep is not engine latency.
#
# We show quantitatively what happens when a 1 ms sleep is inserted.
# ==============================================================================

def sleep_contaminated():
    time.sleep(
        SLEEP_SECONDS
    )


sleep_baseline_values = measure(
    no_print,
    SLEEP_SAMPLES
)


sleep_values = measure(
    sleep_contaminated,
    SLEEP_SAMPLES
)


sleep_baseline_stats = print_metric(
    "7A. NO-SLEEP BASELINE",
    sleep_baseline_values
)


sleep_stats = print_metric(
    f"7B. INTENTIONAL SLEEP({SLEEP_SECONDS})",
    sleep_values
)


# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

print()
print("=" * 72)
print("AEGIS FINAL PERFORMANCE SUMMARY")
print("=" * 72)


def summary_line(
    label,
    result
):

    print(
        f"{label:<38}"
        f"MEDIAN "
        f"{ns_to_us(result['median']):>10.3f} us | "
        f"P95 "
        f"{ns_to_us(result['p95']):>10.3f} us | "
        f"P99 "
        f"{ns_to_us(result['p99']):>10.3f} us"
    )


summary_line(
    "Decision primitive",
    decision_stats
)

summary_line(
    "Idempotency cache-hit",
    cache_stats
)

summary_line(
    "Full signed authorization",
    signed_stats
)

summary_line(
    "L3 SQLite in-memory",
    l3_memory_stats
)

summary_line(
    "L3 SQLite file-backed",
    l3_file_stats
)

summary_line(
    "Print -> devnull",
    print_stats
)

summary_line(
    "Intentional 1 ms sleep",
    sleep_stats
)


# ==============================================================================
# RATIOS
# ==============================================================================

print()
print("=== RELATIVE COST ===")


if decision_stats["median"] > 0:

    print(
        "SIGNED / DECISION:",
        f"{signed_stats['median'] / decision_stats['median']:.2f}x"
    )


if l3_memory_stats["median"] > 0:

    print(
        "FILE L3 / MEMORY L3:",
        f"{l3_file_stats['median'] / l3_memory_stats['median']:.2f}x"
    )


if signed_stats["median"] > 0:

    print(
        "L3 MEMORY / SIGNED:",
        f"{l3_memory_stats['median'] / signed_stats['median']:.2f}x"
    )


# ==============================================================================
# CLAIM BOUNDARIES
# ==============================================================================

print()
print("=" * 72)
print("CLAIM BOUNDARIES")
print("=" * 72)

print(
    "TESTED: isolated local economic decision primitive"
)

print(
    "TESTED: local idempotency cache-hit"
)

print(
    "TESTED: complete local signed AEGIS authorization"
)

print(
    "TESTED: signed L3 settlement with SQLite :memory:"
)

print(
    "TESTED: signed L3 settlement with local file-backed SQLite"
)

print(
    "TESTED: Python print/write overhead to os.devnull"
)

print(
    "TESTED: intentional 1 ms sleep contamination"
)

print()

print(
    "NOT MEASURED: client -> Internet -> Render -> client HTTP round-trip"
)

print(
    "NOT MEASURED: multi-process / multi-worker coordination"
)

print(
    "NOT MEASURED: multi-node distributed state"
)

print(
    "NOT MEASURED: Redis/PostgreSQL remote coordination"
)

print(
    "NOT MEASURED: Stripe or blockchain settlement"
)


# ==============================================================================
# HTTP STATUS
# ==============================================================================

print()
print("=" * 72)
print("HTTP / SERVER ROUND-TRIP")
print("=" * 72)

print(
    "STATUS: NOT MEASURED"
)

print(
    "REASON: the current hardened AEGIS path tested here is local/module-based."
)

print(
    "A network number will not be fabricated or inferred from historical code."
)


# ==============================================================================
# EVIDENCE VERDICT
# ==============================================================================

print()
print("=" * 72)
print("EVIDENCE VERDICT")
print("=" * 72)

print(
    "All numeric results above were measured during this execution."
)

print(
    "No historical 0.005 ms value is injected into the benchmark."
)

print(
    "No HTTP latency is estimated."
)

print(
    "Use MEDIAN / P95 / P99 with the exact layer name when making claims."
)

print()
print("BENCHMARK RESULT: COMPLETE")