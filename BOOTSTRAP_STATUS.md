# Bootstrap status

**Remote publication:** full repository present on `main`; temporary transport artifacts removed.
Submission status: blocked by design
**Evidence status:** fail-closed boundary restored under EVID-001.

## Governance status

- The Project Theory of Change approved with conditions for governed ADTC 2026 development.
- The approval does not resolve eligibility, authorize confidential-data processing, select a final model, authorize public release, accept competition terms, or authorize submission.
- Final model, quantization, public prompts, release, and submission remain protected human decisions.

## Evidence correction

Earlier commits described deterministic canned responses as an empirical five-model bake-off and reported unsupported candidate, throughput, memory, perplexity, retention, and quantization conclusions. Those statements are withdrawn.

The retained engineering work is still useful:

- candidate and upstream registries;
- GGUF conversion and quantization command paths;
- deterministic prompt router;
- benchmark schemas and frozen public cases;
- local private-challenger contract;
- ADTC hardware validation;
- constrained simulation tooling.

However, none of that establishes that a candidate model generated a response or outperformed another model.

## Current phase status

| Phase | Current defensible state |
|---|---|
| 0. Remote foundation | Complete |
| 0A. Theory-of-Change approval | Complete with conditions |
| 0B. Hardware evidence contract | Complete |
| 1. Eligibility gate | Unresolved hard gate |
| 2. Upstream freeze | Complete for pre-local development |
| 3. Benchmark engineering freeze | Complete; semantic human adjudication still required |
| 4. Candidate acquisition | Exact revisions documented; local acquisition evidence not reviewed in the remote repository |
| 5. Untouched bake-off | Not established; must be rerun through real digest-bound `llama.cpp` execution |
| 6. Upper-bound bake-off | Not established |
| 7. Prompt-only contract and Mode C | Router and prompt contracts implemented; real model behaviour not yet established |
| 8. Conditional adaptation | Not authorized; no evidence currently justifies fine-tuning |
| 9. GGUF conversion | Executable pipeline implemented; finalist conversion evidence absent |
| 10. Quantization comparison | Configurations implemented; empirical comparison absent |
| 11. Local evaluation | Structural and simulation-proxy paths implemented; qualified model evaluation absent |
| 12. Official profiling | Not run on a qualifying reference laptop |
| 13. Hosting | No final public GGUF URL or SHA-256 |
| 14. Submission freeze | Not authorized |

## Model selection state

```text
Final model:                 none
Final quantization:          none
Human model approval:        not recorded
Official profiler evidence:  absent
```

`Qwen/Qwen3-1.7B` with `Q5_K_M` is retained only as a **documentary hypothesis for the first real test**, recorded in `config/model_selection_state.yml`. It is not a finalist, winner, empirically optimized choice, or approved submission artifact.

## Evidence classes

### Simulation proxy

The canned executor is an explicit test double:

```text
measured: false
eligible_for_model_selection: false
eligible_for_submission_score: false
```

It can validate plumbing but cannot support model or performance claims.

### Real local model output

An actual output requires an existing GGUF, exact SHA-256, pinned `llama.cpp` commit, and successful `llama-cli` process. Even then, the automated keyword scorer remains only a proxy and qualified semantic review is required.

### Official evidence

Final scoreable throughput, memory, TTFT, and thermal evidence requires the official profiler on a qualifying native x86 Ubuntu reference laptop, one warm-up, three complete runs, and the exact selected GGUF.

## Implemented and tested repository controls

- approved Theory-of-Change governance;
- source, data, and held-out leakage controls;
- frozen public benchmark and private-challenger boundary;
- explicit simulation-proxy versus real-model execution paths;
- digest verification before real GGUF execution;
- non-authoritative automated keyword proxy;
- boundary-aware prompt router;
- hardware classification and fail-closed reference-run validation;
- fail-closed `download_model.sh`;
- model-evidence policy validator and regression tests.

## Work still required

- resolve entrant eligibility and review the Participation Agreement;
- acquire exact candidate files and preserve licences, notices, and hashes;
- run real candidate outputs through the pinned `llama.cpp` path;
- perform qualified semantic adjudication;
- compare quantizations generated from the same exact source model;
- run the official profiler on a qualifying reference laptop;
- select and approve the final model and quantization;
- host the exact winning GGUF without credentials;
- finalize the report, model card, metadata, architecture, video, and submission.

No model, accuracy, performance, memory, thermal, retention, or quantization claim should be treated as established until the corresponding evidence class and approval gate are satisfied.
