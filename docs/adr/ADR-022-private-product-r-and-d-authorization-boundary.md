# ADR-022: Private product R&D authorization boundary

**Status:** accepted.

## Context

Contest eligibility and registration remain unresolved. The accountable owner
has directed MethodBridge to continue as private product development without
turning that direction into organizer approval, entrant eligibility, public
evidence, release authority, or submission authority.

## Decision

Record `EXEC-001`, approved by Marothi Peter Letsoalo at
`2026-08-20T12:33:58+02:00`, as a development-only authorization. It permits:

- acquisition of only the exact candidate revisions already admitted by the
  reviewed allowlist, with an approved licence and public access that requires
  no credentials;
- Docker simulation, which remains a non-measured plumbing test; and
- local `llama.cpp` execution only when the model artifact is bound to an exact
  digest and the pinned campaign/runtime/evidence controls remain satisfied.

The contest eligibility gate remains `unresolved`. `EXEC-001` does not select a
finalist or final quantization and does not authorize official profiler claims,
public claims, hosting, release, registration, rules acceptance, or submission.
It records no organizer decision.

## Evidence boundary

Simulation remains `simulation_proxy` and cannot support model selection or
public claims. Digest-bound local execution may create
`local_real_model_output`, but it still requires qualified semantic review and
an accountable later decision before model selection. Official performance
claims still require `official_reference_profile` evidence on a qualifying
reference host. Raw prompts, responses, private challenger material, weights,
credentials, and machine-specific paths remain outside source control.

## Consequences

- Development execution no longer depends on contest eligibility passing.
- Contest, release, and submission gates remain independent and fail closed.
- Any candidate outside the reviewed licence, access, revision, or admission
  policy stops the campaign.
- ADR-021 remains controlling except for its former coupling of local R&D
  execution authorization to a passed eligibility gate.
- A material scope, candidate-policy, data-boundary, evidence-class, public-use,
  release, or submission change requires a new attributable human decision.
