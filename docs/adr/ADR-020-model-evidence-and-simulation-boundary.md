# ADR-020: Model evidence and simulation boundary

- **Status:** Accepted
- **Date:** 2026-08-19
- **Decision authority:** Repository evidence correction under EVID-001; final model authority remains human

## Context

MethodBridge needs credential-free CI and deterministic plumbing tests before large GGUF files are available. A canned executor was introduced for this purpose, but later status records described its outputs as empirical results from multiple candidate models and quantizations. The same code also populated static timing and memory values and used a lightweight keyword-overlap scorer as if it established model quality.

This violated the repository’s original fail-closed evidence policy and created contradictions between the status file, report, model card, and submission metadata.

## Options considered

1. **Delete all simulation tooling.**  
   Rejected because deterministic no-weight tests are useful for CI, schemas, routing, and failure handling.

2. **Keep one inference function and distinguish results only in documentation.**  
   Rejected because prose does not prevent accidental promotion of canned output.

3. **Separate explicit simulation and digest-bound real execution, with machine-enforced evidence classes.**  
   Accepted.

## Decision

MethodBridge will maintain three evidence classes:

```text
simulation_proxy
local_real_model_output
official_reference_profile
```

The simulation proxy:

- is disabled unless explicitly acknowledged;
- loads no model;
- records no fabricated timing, throughput, RSS, or thermal values;
- is never eligible for model selection or submission scoring.

Real local output requires:

- an existing `.gguf`;
- exact SHA-256 verification;
- the pinned `llama.cpp` commit;
- successful `llama-cli` execution.

Real local output may enter a review packet, but the built-in keyword-overlap proxy cannot select a model. Qualified semantic adjudication remains mandatory.

Official ADTC performance, efficiency, TTFT, and thermal evidence requires the pinned official profiler on a qualifying native reference host. Final model and quantization selection remains an attributable human decision.

Private challenger shareable output excludes prompts, responses, previews, and rubric text.

## Consequences

### Positive

- CI can retain deterministic test doubles without creating false model evidence.
- Real model output becomes cryptographically bound to the tested GGUF.
- Status and submission metadata remain unresolved until evidence and approval exist.
- Automated proxy scores can support regression testing without being mistaken for accuracy.
- Private challenger content has a clearer disclosure boundary.

### Costs

- Existing local commands must choose an explicit executor.
- Earlier claimed model and quantization results must be rerun.
- Final candidate selection now requires both real execution and qualified review.
- The tracked manifest must be regenerated after the correction.

## Implementation impact

Controlling artifacts include:

- `config/model_evidence_policy.yml`;
- `config/model_selection_state.yml`;
- `src/methodbridge/inference/runner.py`;
- `src/methodbridge/evaluation.py`;
- `scripts/validate_model_evidence_boundary.py`;
- `docs/MODEL_EVIDENCE_BOUNDARY.md`;
- the dedicated CI workflow and regression tests.

## Review triggers

Revisit this ADR if:

- the official ADTC profiler changes its evidence contract;
- the runtime moves away from `llama.cpp`;
- a new automated evaluator is proposed as a selection authority;
- private challenger evidence needs a different disclosure model;
- the final model-selection workflow changes materially.
