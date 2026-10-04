# External Engineering Impact — PayMCP

## Classification

This record documents **external engineering impact**, not AEGIS adoption.

- External project: [PayMCP/paymcp](https://github.com/PayMCP/paymcp)
- Upstream pull request: [PayMCP/paymcp#52](https://github.com/PayMCP/paymcp/pull/52)
- PR title: **Return the paid result on retry instead of running the tool twice**
- Upstream author / merger: `blustAI`
- Merged: **2026-09-28**
- Public attribution in the upstream PR: **"Reported by Iraitz / LortuArte."**

## What the upstream project confirmed

PayMCP's merged PR #52 documents a retry/disconnect failure mode in its paid-tool execution path.

Before the fix, a paid tool could execute successfully, the client could disconnect before receiving the result, and a later retry could enter the flow again and execute the underlying tool a second time.

The upstream PR summarizes the failure as:

> One payment, two executions.

It also states that all five payment flows were affected.

For tools with external side effects, that creates the possibility that the paid action itself happens twice even though the buyer made one payment.

## What PayMCP changed

The merged fix stores the tool result when the client disconnects and serves that stored result on the retry instead of automatically re-executing the paid tool.

The upstream implementation uses flow-specific result keys / session state and, where applicable, argument fingerprints so that a retry can receive the result associated with the original paid execution.

## Why this matters to AEGIS research

This upstream fix is independent evidence that retry ambiguity around economically consequential agent/tool execution is a real engineering problem.

It supports the problem statement behind AEGIS work on:

- stable logical action identity;
- replay handling;
- preventing accidental duplicate execution;
- binding authorization state to the consequential execution boundary.

It does **not** prove that PayMCP uses or needs AEGIS.

## Evidence classification

| Evidence class | Status |
|:---|:---:|
| External project independently documented the failure mode | ✅ YES |
| Upstream fix merged | ✅ YES |
| Iraitz / LortuArte explicitly credited in merged PR | ✅ YES |
| Supports the duplicate-execution / retry-risk problem statement | ✅ YES |
| AEGIS dependency used by PayMCP | ❌ NO |
| AEGIS integrated into PayMCP | ❌ NO |
| PayMCP adoption of AEGIS | ❌ NO |
| Production validation of AEGIS | ❌ NO |
| Commercial endorsement of AEGIS | ❌ NO |

## Primary source

- [PayMCP PR #52 — Return the paid result on retry instead of running the tool twice](https://github.com/PayMCP/paymcp/pull/52)

The evidence should be cited using the classification above. It must not be upgraded into an AEGIS integration, adoption, production-validation, or endorsement claim.
