# Devpost submission draft — evidence gated

**Project:** MethodBridge Local  
**Domain:** Math & Scientific Reasoning  
**Cross-disciplinary pairing:** Education  
**Submission status:** **BLOCKED**

## Evidence-safe pitch

MethodBridge Local is being developed as a compact, fully offline
scientific-reasoning and research-methods assistant for postgraduate students and
early-career researchers who may have unreliable connectivity or limited access
to specialist support. The repository implements governance, evaluation,
digest-bound `llama.cpp` execution, GGUF conversion and quantization tooling,
hardware validation, and fail-closed release controls.

No final model or quantization has been selected. No accuracy, throughput, memory,
TTFT, thermal, perplexity, retention, or winner claim is currently authorized.

## Fields still required

```text
REQUIRES_HUMAN_ENTRANT_IDENTITY
REQUIRES_ELIGIBILITY_RESOLUTION
REQUIRES_HUMAN_MODEL_SELECTION
REQUIRES_EMPIRICAL_SELECTION
REQUIRES_FINAL_GGUF_SHA256
REQUIRES_OFFICIAL_REFERENCE_PROFILE
REQUIRES_PUBLIC_MODEL_URL
REQUIRES_TWO_HUMAN_APPROVED_PROMPTS
REQUIRES_FINAL_ARCHITECTURE_ASSET
REQUIRES_PUBLIC_VIDEO_URL
REQUIRES_RULES_ACCEPTANCE
REQUIRES_FINAL_SUBMISSION_AUTHORIZATION
```

## Permitted current claims

- The public benchmark is frozen for engineering comparison and excluded from training.
- The simulation proxy is explicitly non-empirical.
- A real local output requires an exact GGUF digest and pinned `llama.cpp`.
- Official performance and thermal claims require the qualifying reference-laptop profiler path.
- MethodBridge preserves human authority and does not approve research, ethics,
  clinical, legal, regulatory, or institutional decisions.

Update this draft only after `scripts/validate_public_claims.py` passes and the
corresponding evidence and human decision are recorded.
