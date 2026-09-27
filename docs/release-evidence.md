# Release evidence

Current status: **DEPLOYED — LIVE LIFECYCLE VERIFIED**

- Network: GenLayer Studionet
- Chain ID: `61999`
- Contract: [`0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956`](https://explorer-studio.genlayer.com/address/0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956)
- RPC readback: `{"name":"CalScope","schema":"calibration-applicability-capability-v1","version":1}`
- Initial stats: `{"assessments":0,"certificates":0,"consumed":0,"requirements":0}`

## Finalized authority configuration

| Action | Transaction | Result |
|---|---|---|
| Register calibrator `0xeb57…81f8` for `eaglebooth/calscope` | [`0xda2f8724…f6db`](https://explorer-studio.genlayer.com/tx/0xda2f8724e525d45545a5ead0d981cd92a37b399b2ac5e2248427f8f54683f6db) | FINALIZED; 3 agree/SUCCESS |
| Register facility QA `0x2da5…843f` for `eaglebooth/claimanchor` | [`0x967647c4…2461`](https://explorer-studio.genlayer.com/tx/0x967647c4b7d925509b592165882ee7600369ece2e3e25c2c0c03d804d4c72461) | FINALIZED; 3 agree/SUCCESS |

## Commit-pinned live inputs

| Role | Immutable source | SHA-256 | Bytes |
|---|---|---|---:|
| Calibrator certificate | [`CalScope@e0805c2/fixtures/CERTIFICATE.md`](https://raw.githubusercontent.com/eaglebooth/CalScope/e0805c2361acecee24127176e0a15c3a52fe47d7/fixtures/CERTIFICATE.md) | `54bcaba189b96b90004c31c98cce27dec2477a0155ccc7908391491fdc764cf7` | 443 |
| Facility requirement | [`ClaimAnchor@b91162f/CALSCOPE_REQUIREMENT_JOB_204.md`](https://raw.githubusercontent.com/eaglebooth/ClaimAnchor/b91162fe9973e252ca9016430893d4c7b19d6296/CALSCOPE_REQUIREMENT_JOB_204.md) | `c091dd2a343f46c36e529e8057dde8572d8c278594fc3ffa5ba2ca9316ca66e3` | 673 |

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
| Live lifecycle | [`docs/LIVE_STUDIONET_EVIDENCE.md`](LIVE_STUDIONET_EVIDENCE.md) and machine-readable [`docs/live-evidence/studionet-run.json`](live-evidence/studionet-run.json) | PASS |

The lifecycle evidence covers authenticated certificate issuance, facility requirement sealing, semantic applicability assessment, one-time consumption, wrong issuer, wrong QA, wrong operator and replay rejection. No frontend is part of this contribution.

