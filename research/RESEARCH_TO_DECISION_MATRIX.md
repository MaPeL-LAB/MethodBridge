# Research-to-decision matrix

| Finding | Decision | ADR | Artifact | Verification | Status |
|---|---|---|---|---|---|
| Official path is GGUF + llama.cpp | Reject incompatible candidates | ADR-010 | conversion/runtime scripts | exact load test | specified |
| Public access is not training permission | Source allowlist and record-level licence | ADR-006 | source registry/schema | dataset validator | implemented |
| Hidden prompts require breadth | Retention suite and no public-prompt training | ADR-013 | 60 cases/leakage test | held-out evaluation | implemented |
| 8 GB leaves little headroom | Internal 6 GB target | ADR-012 | inference config | profiler | requires empirical test |
| Non-reference hosts cannot establish native x86 performance or thermals (`docs/ADTC_SIMULATION_LIMITATIONS.md`) | Classify runs as `reference_match`, `simulation_only`, or `invalid_environment`; reserve final participant claims for qualifying native evidence | ADR-019 | `config/adtc_standard_laptop.yml`; hardware protocol and run records | hardware tests and `scripts/verify_adtc_reference_run.py` | contract implemented; official evidence absent |
| A canned response or keyword proxy is not model-quality evidence (`docs/MODEL_EVIDENCE_BOUNDARY.md`) | Enforce separate simulation, digest-bound local-output, and official-reference evidence classes; retain qualified human review | ADR-020 | `config/model_evidence_policy.yml`; inference and review evidence contracts | `scripts/validate_model_evidence_boundary.py` and evidence-boundary tests | control implemented; empirical comparison absent |
| Campaign preparation does not authorize downloads or execution (`config/local_model_campaign.yml`) | Require resolved eligibility and attributable execution authorization; keep release authorization separate and exclude raw text and local paths from shareable evidence | ADR-021 | campaign/release configs and shareable evidence schemas | campaign, handoff, and release-gate tests | prepared; execution and release unauthorized |
| Public claims require the matching immutable evidence class and human decision (`docs/PUBLIC_CLAIMS_POLICY.md`) | Keep report, model card, demo, Devpost, metadata, and release writes blocked until evidence and authority agree | ADR-021 / Phase 0E | public-claims validator and human-controlled release tooling | `scripts/validate_public_claims.py`; `scripts/prepare_model_release.py --check` | control implemented; release expected to remain blocked |

## Recovery note

This document was recreated from the retained Deep Research report and controlling specification; it is not claimed to be byte-identical to the inaccessible original artifact.
