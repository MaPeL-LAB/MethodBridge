# Changelog

## Unreleased — 2026-08-19

### Restored fail-closed model evidence boundary

- Withdrew unsupported empirical candidate, throughput, memory, perplexity, retention, and quantization claims that had been derived from a canned simulation path.
- Split inference into an explicit `simulation_proxy` and a digest-bound real `llama.cpp` executor.
- Made the simulation proxy opt-in and permanently ineligible for model selection or submission scoring.
- Added exact GGUF SHA-256 and pinned `llama.cpp` commit checks before real model execution.
- Relabelled the built-in scorer as `automated_keyword_proxy_pass_rate`; it now requires qualified semantic adjudication and cannot select a model automatically.
- Reclassified Qwen3-1.7B with Q5_K_M as a documentary first-test hypothesis, not a finalist.
- Removed response previews and rubric text from shareable private-challenger output.
- Added boundary-aware router matching, ambiguity reporting, and false-positive regression tests.
- Reconciled README, status, checklist, report, model card, metadata, selection state, and Codex instructions.
- Added machine-readable evidence policy, validation script, tests, and a dedicated CI workflow.

### Earlier governed foundation

- Recorded Marothi Peter Letsoalo's attributable approval of the MethodBridge Local Theory of Change for governed ADTC 2026 development.
- Preserved the contribution boundary, licensed/synthetic data policy, human-authority controls, held-out evaluation boundary, and separate eligibility, release, rules, and submission gates.
- Added the machine-readable ADTC Standard Laptop profile and ADR-019.
- Added host classification, hardware attestation, constrained simulation, native reference-run wrappers, and fail-closed reference evidence validation.

## v0.1.0-bootstrap — 2026-08-19

- Replaced the temporary repository transport with the complete MethodBridge tree.
- Added deterministic manifest-generation tooling and Markdown-link validation.
- Added CODEOWNERS, main-branch governance guidance, and the remote-to-local handoff.
- Expanded the Theory-of-Change draft and organizer-clarification request.
- Preserved empirical, eligibility, licence, model, profiler, and submission gates.

## v0.1.0-recovered — 2026-08-18

- Recovered a directly downloadable MethodBridge Local repository bootstrap from retained research artifacts.
- Recreated the governance, model-selection, data, evaluation, scripts, tests, CI, release, and submission-readiness foundation.
- Preserved unresolved empirical and human gates.
