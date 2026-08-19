# Changelog

## Unreleased — 2026-08-19

### Completed pre-local empirical-campaign boundary

- Added a machine-validatable local model campaign with explicit eligibility and human execution authorization.
- Added privacy-preserving real-run and qualified semantic-review schemas.
- Added a local handoff validator that distinguishes setup readiness from execution authorization.
- Added a public claims gate covering the README, report, model cards, demo storyboard, Devpost draft, and status record.
- Replaced provisional release automation with a fail-closed, human-controlled release authorization gate.
- Removed unsupported metrics and finalist language from the model release card, Devpost draft, and video storyboard.
- Added ADR-021, campaign tests, release tests, and public-claims regressions.
- Preserved the rule that no model, quantization, performance result, release, or submission is established before immutable evidence and accountable human authorization exist.

### Earlier fail-closed model evidence restoration

- Withdrew unsupported empirical candidate, throughput, memory, perplexity, retention, and quantization claims derived from a canned simulation path.
- Split inference into explicit `simulation_proxy` and digest-bound real `llama.cpp` execution.
- Made the simulation proxy opt-in and permanently ineligible for selection or submission scoring.
- Relabelled the built-in scorer as `automated_keyword_proxy`.
- Reclassified Qwen3-1.7B with Q5_K_M as a documentary first-test hypothesis.
- Removed private response previews and hardened routing.

### Governed foundation

- Recorded bounded Theory-of-Change approval.
- Added the ADTC Standard Laptop profile, host classification, constrained simulation, native reference wrappers, and fail-closed reference validation.

## v0.1.0-bootstrap — 2026-08-19

- Replaced the temporary repository transport with the complete MethodBridge tree.
- Added deterministic manifest generation, CODEOWNERS, governance, candidate and source registries, benchmark fixtures, and CI.
