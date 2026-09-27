# CalScope protocol specification

## Proof obligation

For one facility job, prove that an approved calibrator's exact certificate semantically covers the facility QA's exact measurement requirement, then issue one operator-bound capability.

## Three authorities

| Authority | Source | Contract duty |
|---|---|---|
| Evidence authority | Registered calibrator and facility QA senders | Authenticate who may issue each evidence role |
| Judgment authority | GenLayer validator consensus | Classify certificate-to-requirement applicability |
| Execution authority | Deterministic contract state | Create, invalidate and consume the capability |

## Evidence identity

Every evidence object binds repository, immutable commit URL, SHA-256, byte count, sender, registry revision, device serial and domain object ID. Certificate and requirement must come from distinct wallets and repositories.

## State transitions

```text
REGISTRY CONFIGURED
  -> CERTIFICATE ISSUED + REQUIREMENT SEALED
  -> APPLICABLE | OUT_OF_SCOPE | CONDITIONAL
  -> AUTHORIZATION CREATED only for APPLICABLE
  -> AUTHORIZATION CONSUMED once by assigned operator
```

`INSUFFICIENT_EVIDENCE` stores no terminal assessment and creates no capability. The exact committed pair may be retried after a transient source or model failure.

## Non-goals

- Legal accreditation discovery
- Payment or escrow
- Certificate expiry derived from caller-supplied time
- General-purpose claims or disputes
- Frontend

