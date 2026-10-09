# AEGIS Core 3.4.0 — External Reproduction

Purpose: reproduce one narrow process-local invariant under an operator's own GitHub account.

## Claim being tested

100 concurrent presentations of the same logical call ID should result in:

- 1 fresh execution grant
- 99 cached replays
- 1 downstream execution
- final balance: 0.000000

## Run it

1. Fork this repository.
2. Open the fork.
3. Go to Actions.
4. Select `AEGIS External Reproduction`.
5. Click `Run workflow`.
6. Open the completed run.
7. Copy the final JSON/output or send the workflow-run URL.

No API key, wallet, provider account or live funds are required.

PASS, FAIL and setup errors are all useful.

## Scope

This reproduction tests only process-local behavior.

It does not establish:

- multiprocess coordination;
- crash recovery;
- distributed exactly-once execution;
- external-effect verification;
- production certification;
- adoption or endorsement.
