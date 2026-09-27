# Threat model

## Authority boundary

Markdown is evidence, never authority. The registry authority approves an exact calibrator wallet/repository and an exact facility QA wallet/repository. Only those senders can create their respective evidence roles.

The registry is a governance root, not an accreditation oracle. A deployment claiming real accreditation must document how the registry authority authenticates calibrators. This repository does not claim the synthetic fixture issuer is accredited.

## Protected properties

- An unregistered sender cannot issue a certificate or facility requirement.
- A URL outside the authority's registered repository is rejected.
- Validators fetch and hash the exact committed bytes before semantic judgment.
- Calibrator and facility QA must use different wallets and repositories.
- Certificate and requirement bind the same device serial before model execution.
- Each evidence object binds the issuing authority's repository and registry revision; rotation invalidates stale evidence.
- Only `APPLICABLE` creates an authorization.
- Authorization binds both evidence revisions, job, device and operator.
- Revocation invalidates an unconsumed authorization.
- Only the assigned operator can consume, once.

## Safe failure

Unavailable, changed, oversized or malformed evidence produces retryable `INSUFFICIENT_EVIDENCE`; no terminal assessment or authorization is stored. Malformed model output follows the same route. `CONDITIONAL` is recorded for audit but does not authorize measurement.

## Explicit limitations

- No payment or asset custody.
- No claim that a GitHub account proves legal identity.
- No automated certificate expiry because this version avoids caller-supplied time as authority.
- No frontend; verification is contract, test and Explorer based.

