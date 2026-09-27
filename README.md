# CalScope

CalScope is a contract-only GenLayer Intelligent Contract for one narrow decision: whether an issuer-authenticated calibration certificate covers one facility-authenticated measurement requirement.

**Studionet contract:** [`0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956`](https://explorer-studio.genlayer.com/address/0x89c65F2c7999CC55Ee8E21A35768CD9B1269e956) on chain `61999`.

**Live verification:** [successful applicability lifecycle and finalized rejection matrix](docs/LIVE_STUDIONET_EVIDENCE.md).

It is not a claim registry, challenge court or remediation workflow. Its output is a single-use capability bound to an exact device, job, operator, certificate revision and requirement revision.

## Why GenLayer

Calibration certificates and measurement requirements often express range, uncertainty, method and environmental constraints in heterogeneous prose. Validators perform this bounded semantic comparison. Deterministic contract logic retains authority, integrity, revocation and replay decisions.

## Authority and evidence

1. The deployment registry approves a calibrator wallet and its evidence repository.
2. The registry approves a facility QA wallet and its separate requirement repository.
3. The calibrator issues a certificate for an exact device serial.
4. Facility QA seals a job requirement and assigned operator.
5. Validators fetch both commit-pinned Markdown files, verify SHA-256 and byte length, then return a bounded verdict.
6. Only `APPLICABLE` creates an authorization. The assigned operator may consume it once.

Markdown cannot grant a role. A correct digest proves content integrity, not issuer identity; issuer authority comes from the registered transaction sender. See [the threat model](docs/THREAT_MODEL.md).

## Verdicts

- `APPLICABLE` — all required dimensions are clearly covered.
- `OUT_OF_SCOPE` — at least one required dimension is incompatible.
- `CONDITIONAL` — possible only under an explicit certificate condition; no authorization is issued.
- `INSUFFICIENT_EVIDENCE` — required facts, sources, integrity or model output are unavailable or unsafe; no terminal assessment is stored, so the same committed pair can be retried.

## Public methods

- `set_calibrator`
- `set_facility`
- `issue_certificate`
- `revoke_certificate`
- `seal_requirement`
- `assess`
- `consume_authorization`
- `get_certificate`
- `get_requirement`
- `get_assessment`
- `get_authorization`
- `get_stats`
- `get_contract_version`

## Test

```bash
python -m pytest -q -p no:cacheprovider
```

The suite executes the production contract with `gltest`. It covers sender authority, repository scoping, device binding, all bounded verdicts, content mutation, malformed model output, wrong operator, replay and post-assessment certificate revocation.

The live runner is `scripts/live-e2e.mjs`. It reads two test-only wallet keys from stdin, never writes them to disk, and produces a sanitized machine-readable result in `docs/live-evidence/studionet-run.json`.

## Deploy

Deploy `contracts/calscope.py` with no constructor arguments in Studio Next. The deployer becomes the registry authority. The address above was read back through Studionet RPC as schema `calibration-applicability-capability-v1`, version `1`. The included Markdown documents are synthetic test fixtures and must not be represented as real-world calibration evidence.

