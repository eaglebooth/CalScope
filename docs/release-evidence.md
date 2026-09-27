# Release evidence

Current status: **DEPLOYED — LIVE LIFECYCLE NOT YET EXECUTED**

- Network: GenLayer Studionet
- Chain ID: `61999`
- Contract: [`0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956`](https://explorer-studio.genlayer.com/address/0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956)
- RPC readback: `{"name":"CalScope","schema":"calibration-applicability-capability-v1","version":1}`
- Initial stats: `{"assessments":0,"certificates":0,"consumed":0,"requirements":0}`

| Gate | Evidence | Status |
|---|---|---|
| Production source | `contracts/calscope.py` | PASS |
| Behavioral suite | `python -m pytest -q -p no:cacheprovider` — 13 passed | PASS |
| Authority separation | Wrong sender and same-authority tests | PASS |
| Integrity failure | Changed content cannot authorize; same pair remains retryable | PASS |
| Replay/finality | Wrong operator and duplicate consumption revert | PASS |
| Authority rotation | Stale certificate rejected after registry revision changes | PASS |
| Studio schema | Loaded by `gltest` direct deployment | PASS |
| Studionet deployment | Address and schema readback recorded above | PASS |
| Live lifecycle | No finalized Studionet transactions yet | BLOCKED |

Do not describe this revision as submission-ready until a fresh live evidence artifact records successful and rejected transactions plus authoritative readback.

