# Model evidence boundary

**Status:** active fail-closed policy  
**Decision reference:** EVID-001 / GitHub issue #15

## Purpose

MethodBridge distinguishes code-path validation from model evidence. A deterministic canned response can prove that a CLI, schema, router, or report pipeline is wired correctly; it cannot prove that any candidate model produced the response, achieved a quality score, retained reasoning, met a memory target, or outperformed another candidate.

## Evidence classes

### 1. `simulation_proxy`

The simulation proxy loads no model. It is disabled unless the caller explicitly supplies the simulation flag or acknowledgement. Its results must state:

```text
measured: false
eligible_as_model_output_evidence: false
eligible_for_model_selection: false
eligible_for_submission_score: false
```

It may be used for CI, prompt-contract plumbing, router regression, JSON shape checks, and failure handling. It may never support candidate ranking, quantization selection, performance claims, or public submission claims.

### 2. `local_real_model_output`

This class requires an actual `.gguf`, its exact SHA-256, the pinned `llama.cpp` commit, an executable `llama-cli`, and a successful subprocess result. It establishes that the digest-bound model generated a particular output under the recorded local configuration.

It does not by itself establish:

- expert-rated methodological correctness;
- superiority over another model;
- official ADTC throughput or memory efficiency;
- target-laptop thermal behaviour;
- final-model approval.

The built-in keyword scorer remains a non-authoritative automated proxy. Qualified semantic adjudication is required before model selection.

### 3. `official_reference_profile`

Scoreable performance, memory, TTFT, and thermal evidence requires the pinned official profiler on a qualifying native x86 Ubuntu host, with the exact selected GGUF and required repeated runs. The hardware contract in `config/adtc_standard_laptop.yml` and `docs/ADTC_HARDWARE_VALIDATION_PROTOCOL.md` remains controlling.

## Automated scoring boundary

`keyword_overlap_v1` is intentionally lightweight. It checks coarse overlap between response text and expected concepts and looks for limited prohibited patterns. It is useful for smoke testing and regression detection. It must be labelled:

```text
automated_keyword_proxy_pass_rate
```

It must not be labelled accuracy, reasoning quality, reasoning retention, expert score, or hidden-prompt readiness.

## Final-model gate

The root `metadata.json` remains a development draft with `REQUIRES_*` values until all of the following exist:

1. real candidate outputs bound to exact model digests;
2. qualified semantic review against the frozen benchmark and a private challenger set;
3. independently produced quantization comparison on the same source model;
4. official reference-laptop profiler evidence;
5. licence and redistribution review;
6. attributable human approval of the model and quantization.

A script, benchmark, CI job, or agent cannot promote a candidate to final status.

## Private challenger boundary

Private challenger prompts, responses, expected key points, and prohibited-error text remain local. Shareable results may contain only case identifiers, broad categories, counts, hashes, review status, and aggregate results. Response previews are prohibited because they may reproduce distinctive private prompt content.

## Correction record

Earlier repository commits contained simulation/canned output described as an empirical multi-model bake-off and published unsupported performance, perplexity, retention, and quantization claims. This policy withdraws those claims without discarding the useful conversion, quantization, router, and evaluation scaffolding. The affected features must be rerun through real `llama.cpp` execution and reviewed evidence before they can be reclassified.
