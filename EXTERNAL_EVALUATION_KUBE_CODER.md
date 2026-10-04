# Independent External Technical Evaluation — kube-coder Issue #573

**AEGIS Core version evaluated:** 3.4.0  
**External project:** [kube-coder](https://github.com/imran31415/kube-coder)  
**Public evaluation date:** 20 September 2026  
**Evaluation thread:** [kube-coder issue #573](https://github.com/imran31415/kube-coder/issues/573)  
**Evaluator in the public thread:** `umi-appcoder[bot]` (project-side contributor/author automation)

> This document records the external evidence exactly as it exists. It is not an adoption claim, production certification, maintainer endorsement, or integration result.

## Status at a glance

| Evidence | Status |
|---|---|
| External inspection of published AEGIS 3.4.0 artifacts | **Completed** |
| External source-level review | **Completed** |
| External local benchmark | **Completed** |
| External fit assessment for kube-coder Phase 4 | **Completed** |
| AEGIS adopted by kube-coder | **No** |
| AEGIS integrated into kube-coder | **No** |
| Production validation | **No** |
| Design patterns from AEGIS reused in kube-coder Phase 4 notes | **Yes** |

The external evaluator explicitly recommended **not adopting AEGIS as a dependency for kube-coder Phase 4**. The reason was architectural fit, not package safety. The same evaluation also identified several AEGIS design patterns worth carrying into kube-coder's own implementation.

## What was independently inspected

The evaluator did not rely only on AEGIS documentation. According to the public evaluation, they:

- downloaded the published AEGIS Core 3.4.0 artifacts;
- verified artifact hashes;
- inspected the published source;
- reviewed package metadata and dependencies;
- imported the extracted module directly rather than installing it with `pip`;
- inspected the test suite;
- measured the relevant local execution paths.

The evaluator described the package as a **real, readable, non-malicious package** and reported no hidden network calls, subprocess execution, or unexpected filesystem writes outside the SQLite path explicitly supplied by the caller.

Source: [external evaluation comment](https://github.com/imran31415/kube-coder/issues/573#issuecomment-5752986929).

## Independent benchmark results

The project-side evaluation reported these measurements from its own environment over 2,000 iterations:

| Path | Median | p95 | p99 |
|---|---:|---:|---:|
| Process-local signed gate | **0.0582 ms** | **0.1042 ms** | **0.1260 ms** |
| File-backed settlement, end-to-end | **1.1349 ms** | **3.2434 ms** | **4.6677 ms** |

These are **external local measurements**, not network, hosted-API, blockchain-confirmation, or distributed-system latencies.

The evaluator also noted that its ~1.13 ms file-backed measurement was directionally consistent with the file-backed local measurement documented by AEGIS at the time. Environment and benchmark-path differences should be expected; the external numbers above are preserved as reported.

## What the review verified about AEGIS 3.4.0

The review correctly separated the product's actual behavior from earlier overstatements:

- `AegisLocalPolicyGate` is a class the integration calls explicitly; it is **not automatically installed as a pre-tool hook**.
- A denial does not kill a worker or thread. The gate returns a decision and the caller must execute the external tool **only when `execution_permitted` is true**.
- The process-local authorization state uses a Python lock around local in-memory state.
- The process-local gate is not a distributed or restart-durable shared budget service.
- The SQLite-backed settlement component is persistent, but it is a separate component from the process-local gate.
- Signed receipts and Ed25519 verification are meaningful when an authorization crosses a real trust boundary; they may be unnecessary when both policy and enforcement live in the same trusted process.

These points match AEGIS's current public scope: local, single-process authorization is not presented as multiprocess coordination, crash recovery, or exactly-once external settlement.

## Why kube-coder did not adopt AEGIS for Phase 4

The external review identified three main fit mismatches.

### 1. The gate expects a known amount before execution

AEGIS 3.4.0 authorizes a supplied `amount_usd` before the protected action executes.

For kube-coder's LLM-agent workload, the final cost of a turn is known only after usage arrives. Output tokens and other usage classes are not fully known at turn start.

That means kube-coder first needs a pricing/estimation model or a different cap semantics. AEGIS does not create that missing price signal.

### 2. kube-coder needs shared durable budget state

The AEGIS local gate is process-local.

kube-coder can run multiple agent processes. A per-process budget would create independent limits and would reset on restart. Their Phase 4 requirement instead points toward a shared ledger already available to their workload.

### 3. The cryptographic trust boundary is different

AEGIS signed receipts are useful when one component must later verify an authorization issued across a trust boundary.

In kube-coder's planned Phase 4, the decision and enforcement point live in the same trusted server process. For that architecture, append-only durable decision records can provide the needed audit trail without adding signature/key-management machinery.

## The design value kube-coder kept from AEGIS

A second project-side note explicitly recorded design ideas “salvaged from the AEGIS scoping.”

Source: [Phase 4 design notes](https://github.com/imran31415/kube-coder/issues/573#issuecomment-5753002672).

The patterns retained were:

### 1. Durable decision receipts

Every allow and deny should leave a durable, machine-readable record explaining the outcome.

### 2. Idempotency with conflict detection

A retry using the same logical identity and the same economics can reuse the existing decision.

The same identity carrying **different economic parameters must be treated as a conflict**, not silently served from cache.

### 3. Integer monetary units

Persist monetary values as integer units rather than binary floating point, with decimal conversion at the boundaries.

### 4. Commit ordering

The design discipline is:

```text
evaluate
  ↓
build durable decision record
  ↓
commit/mutate economic state
```

A failure before the commit should not leave a partial economic state transition.

### 5. Fail-closed internal behavior

Unexpected internal failures in the authorization path should deny rather than fall through to allow.

### 6. Attenuated decisions

A policy result can be richer than binary allow/deny. A single decision model can represent:

```text
allow
allow-attenuated
deny
```

kube-coder connected this directly to its own soft-cap versus hard-cap requirements.

## AEGIS scoping also clarified two enforcement models

The project-side design note used the AEGIS evaluation to make the pre-execution cost problem explicit.

### Model A — check then measure

At turn/task start:

- compare already accumulated spend against the cap;
- refuse if the cap is already exceeded;
- measure the new turn after completion.

This is simpler but permits bounded overshoot by one turn.

### Model B — reserve then reconcile

At turn/task start:

- reserve a conservative estimate;
- execute the turn;
- reconcile the reservation to actual usage afterward.

This can bound overshoot more tightly, but requires:

- a per-model estimator;
- reconciliation;
- durable reservation state;
- crash recovery for orphaned reservations.

kube-coder recommended Model A for its current architecture and documented Model B as the more complex alternative.

This is a useful external result for AEGIS because it identifies where reservation-style authorization is valuable and where a simpler accumulated-spend gate is sufficient.

## What this evidence does — and does not — establish

### It establishes

- A third-party project-side evaluator independently inspected AEGIS Core 3.4.0.
- The published package was source-reviewed and benchmarked outside the AEGIS author's own environment.
- The evaluator did not identify malicious package behavior.
- Independent latency measurements were produced for the local signed gate and file-backed settlement paths.
- The evaluation identified concrete architectural limitations.
- Multiple AEGIS design patterns were explicitly carried into kube-coder's Phase 4 design notes.

### It does not establish

- kube-coder adoption;
- kube-coder integration;
- production readiness;
- production certification;
- multiprocess or distributed atomicity;
- crash-recovery guarantees for the process-local gate;
- exactly-once external side effects;
- institutional endorsement of AEGIS by kube-coder.

## Public correction by the AEGIS author

After the external review, the AEGIS author publicly corrected earlier claims and accepted the fit assessment.

The correction withdraws claims that AEGIS automatically installs a pre-tool hook, kills rogue threads, provides in-memory ACID settlement, or completes full authorization/settlement in under 0.005 ms.

It also states the current scope directly: AEGIS Core 3.4.0 provides a Python process-local authorization gate; the caller supplies a known amount, reuses the logical call ID, and invokes the protected tool only when `execution_permitted` is true.

Source: [author correction in kube-coder #573](https://github.com/imran31415/kube-coder/issues/573#issuecomment-5198491584).

## Reusable public summary

The following is an accurate short description of this result:

> AEGIS Core 3.4.0 received an external source-level evaluation and benchmark in kube-coder issue #573. The evaluator did not recommend AEGIS as the dependency for kube-coder Phase 4 because the process-local budget model, pre-known amount requirement, and cryptographic trust boundary did not match that deployment. The evaluator nevertheless independently benchmarked the package and carried several AEGIS patterns — durable decision receipts, idempotency conflict detection, integer money units, commit ordering, fail-closed behavior, and attenuated policy decisions — into its Phase 4 design notes.

That is the strongest claim supported by the public evidence.

## Primary sources

- External evaluation and benchmark: https://github.com/imran31415/kube-coder/issues/573#issuecomment-5752986929
- Phase 4 design notes derived from the AEGIS scoping: https://github.com/imran31415/kube-coder/issues/573#issuecomment-5753002672
- AEGIS author correction / scope clarification: https://github.com/imran31415/kube-coder/issues/573#issuecomment-5198491584
- AEGIS Core repository: https://github.com/LortuArte/aegis-sdk
