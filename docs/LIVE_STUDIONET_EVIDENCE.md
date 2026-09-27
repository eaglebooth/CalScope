# Live Studionet evidence

## Deployment

- Network: GenLayer Studionet (`61999`)
- Contract: [`0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956`](https://explorer-studio.genlayer.com/address/0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956)
- Deployed schema: `calibration-applicability-capability-v1`, version `1`
- Contract source commit used by the run: [`e0805c2`](https://github.com/eaglebooth/CalScope/commit/e0805c2361acecee24127176e0a15c3a52fe47d7)
- Complete sanitized output: [`live-evidence/studionet-run.json`](live-evidence/studionet-run.json)

Private keys were supplied only to the live process through stdin. They are absent from the repository and evidence artifacts.

## Actors and authority

| Role | Address | Registered source |
|---|---|---|
| Registry/deployer | deployment sender | On-chain registry authority only |
| Calibrator | `0xeb57…81f8` | `eaglebooth/calscope` |
| Facility QA and assigned operator | `0x2da5…843f` | `eaglebooth/claimanchor` |

Authority configuration finalized successfully before the lifecycle:

- [`set_calibrator`](https://explorer-studio.genlayer.com/tx/0xda2f8724e525d45545a5ead0d981cd92a37b399b2ac5e2248427f8f54683f6db)
- [`set_facility`](https://explorer-studio.genlayer.com/tx/0x967647c4b7d925509b592165882ee7600369ece2e3e25c2c0c03d804d4c72461)

## Immutable evidence

| Role | Commit-pinned source | SHA-256 | Bytes |
|---|---|---|---:|
| Certificate | [`CERTIFICATE.md`](https://raw.githubusercontent.com/eaglebooth/CalScope/e0805c2361acecee24127176e0a15c3a52fe47d7/fixtures/CERTIFICATE.md) | `54bcaba189b96b90004c31c98cce27dec2477a0155ccc7908391491fdc764cf7` | 443 |
| Requirement | [`CALSCOPE_REQUIREMENT_JOB_204.md`](https://raw.githubusercontent.com/eaglebooth/ClaimAnchor/b91162fe9973e252ca9016430893d4c7b19d6296/CALSCOPE_REQUIREMENT_JOB_204.md) | `c091dd2a343f46c36e529e8057dde8572d8c278594fc3ffa5ba2ca9316ca66e3` | 673 |

The sources come from separately registered repositories and senders. Markdown supplies bounded evidence; the registered transaction sender supplies authority.

## Finalized transaction matrix

| Scenario | Transaction | Expected GenVM result | Observed |
|---|---|---|---|
| Unregistered wallet attempts certificate issuance | [`0x2c832183…155c7`](https://explorer-studio.genlayer.com/tx/0x2c832183dda6f14136a877e928bea3ec628076037e9d25239393f75cc71155c7) | ERROR | FINALIZED / ERROR |
| Registered calibrator issues certificate | [`0xd30eab82…b863d`](https://explorer-studio.genlayer.com/tx/0xd30eab82d23d0745c20bcbb6e539537fdc1fb59549d5f75515f057b85feb863d) | SUCCESS | FINALIZED / SUCCESS |
| Wrong wallet attempts requirement sealing | [`0x3246ce94…5d2e7`](https://explorer-studio.genlayer.com/tx/0x3246ce945241f1d65b457e6a08959f0a7f7ba3b4be5461b816c1586adf75d2e7) | ERROR | FINALIZED / ERROR |
| Registered facility QA seals requirement | [`0xf227d342…9787e`](https://explorer-studio.genlayer.com/tx/0xf227d3424a6f73a2ee973ebcb4601fafe520fcb9eba60c9e40deb99f65b9787e) | SUCCESS | FINALIZED / SUCCESS |
| Validators assess exact evidence pair | [`0x4b566df3…5798e`](https://explorer-studio.genlayer.com/tx/0x4b566df3885ff6dde9ec22c91087085e05ca5122d42861cd30dfb5076205798e) | SUCCESS | FINALIZED / `APPLICABLE` |
| Wrong operator attempts consumption | [`0x180c2c83…72c64`](https://explorer-studio.genlayer.com/tx/0x180c2c8393334128f7b45b6395dc2dfb5cb3b9d388498d9312523efb43d72c64) | ERROR | FINALIZED / ERROR |
| Assigned operator consumes once | [`0x6f78b340…e8195`](https://explorer-studio.genlayer.com/tx/0x6f78b34074f72bd545753ba3547ce026bcf6c7118b474919fa67851be64e8195) | SUCCESS | FINALIZED / SUCCESS |
| Assigned operator attempts replay | [`0xe17bdfc9…b2876`](https://explorer-studio.genlayer.com/tx/0xe17bdfc947863b2777f6ffd8e204efe76d44fa1d484fab46f303797ce8cb2876) | ERROR | FINALIZED / ERROR |

## Canonical final state

```json
{
  "verdict": "APPLICABLE",
  "assessment_id": "d539ec67b9fed659d70cbe4c79e4e174d3b6e8e85a95decb1836277698c46269",
  "authorization_id": "f6fa908fcc00e458f3e0987097d2be8175425146cd3841264c041d9f2cd8aea3",
  "consumed": true,
  "receipt": "656d599b729efe38fc8b6d83c95f75efac668b34d4e1768c40aedd30596c71f4",
  "stats": {
    "certificates": 1,
    "requirements": 1,
    "assessments": 1,
    "consumed": 1
  }
}
```

The authorization binds certificate revision `1`, requirement revision `1`, device `BAL-17`, job `JOB-204`, and the assigned operator. The rejected replay left this state unchanged.
