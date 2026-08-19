# MethodBridge Local

**Repository:** `MaPeL-LAB/MethodBridge`  
**Product:** MethodBridge Local  
**Release status:** governed implementation bootstrap `v0.1.0-bootstrap`  
**ADTC domain:** `math_scientific_reasoning`  
**Cross-disciplinary pairing:** education  
**Submission ready:** **No**

MethodBridge Local is intended to become a compact, fully offline scientific-reasoning and research-methods model for postgraduate students and early-career researchers using ordinary laptops. The judged product will be the model itself: GGUF weights, `llama.cpp`, CPU-first execution, a public credential-free download, and reproducible evidence of quality, throughput, memory use, and thermal stability.

This repository is the authoritative engineering and governance foundation—not a trained model release. It includes the approved-with-conditions Theory of Change, architecture decisions, candidate and upstream registries, a frozen public benchmark, private-challenger boundary, safe synthetic fixtures, data/licensing controls, conversion and quantization tooling, hardware validation, CI, and a fail-closed submission contract.

## Current truth

| Area | State |
|---|---|
| Product and domain scope | Accepted with conditions |
| Theory of Change | Approved with conditions for governed ADTC development |
| Entrant eligibility | Unresolved hard gate |
| Public benchmark | Engineering-frozen; qualified semantic adjudication still required |
| Upstream toolchain | Reviewed and pinned for pre-local development |
| Simulation proxy | Explicit test double; `measured: false` |
| Real model outputs | Not established in the remote evidence record |
| Final base model | None selected |
| Fine-tuning | Conditional; not authorized |
| Final GGUF | Not built or approved |
| Official profiler | Not run on a qualifying reference laptop |
| Public model URL and SHA-256 | Unresolved |
| Video and final submission | Not completed |

Earlier canned/simulation output was incorrectly described as an empirical candidate and quantization comparison. Those claims are withdrawn. The retained pipelines and router remain useful, but they must be rerun through actual digest-bound `llama.cpp` execution and qualified review. See `docs/MODEL_EVIDENCE_BOUNDARY.md`.

## Evidence classes

```text
simulation_proxy
    plumbing and regression tests only
    no model loaded
    never eligible for selection or submission evidence

local_real_model_output
    actual GGUF + SHA-256 + pinned llama.cpp process
    useful as raw model-output evidence
    still requires qualified semantic review

official_reference_profile
    qualifying native x86 Ubuntu host + official profiler
    required for scoreable performance, memory, TTFT, and thermal claims
```

The built-in lightweight scorer is always labelled:

```text
automated_keyword_proxy_pass_rate
```

It is not accuracy or expert judgment.

## Engineering sequence

```text
eligibility resolution
        ↓
exact licensed candidate acquisition and hashing
        ↓
real untouched llama.cpp outputs
        ↓
qualified semantic review
        ↓
native / contract / Mode C comparison
        ↓
conditional adaptation only if justified
        ↓
GGUF conversion and independent quantization
        ↓
reference-laptop official profiler
        ↓
human model and quantization approval
        ↓
credential-free hosting
        ↓
final report, prompts, video, and submission authorization
```

## First commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'

python scripts/validate_repository.py
python scripts/validate_sources.py
python scripts/validate_dataset.py
python scripts/detect_train_eval_leakage.py
python scripts/validate_model_evidence_boundary.py
python scripts/run_evaluation.py --dry-run
python -m pytest -q
python scripts/verify_submission_readiness.py
```

To exercise only the canned test double, an explicit flag is required:

```bash
python scripts/run_local_inference.py \
  --simulation-proxy \
  --mode contract \
  --prompt "Explain why association is not necessarily causation."
```

That result is not model evidence. Real local inference requires an existing GGUF, its exact SHA-256, and the pinned `llama-cli` path.

## Non-negotiable boundaries

MethodBridge may explain and critique research methods. It may not approve protocols, analysis plans, ethics, clinical care, legal compliance, or institutional decisions. It must not fabricate citations or facilitate deceptive assessed work. Real participant data, confidential documents, credentials, model weights, private held-out prompts, and raw private-challenger outputs must not be committed.

Read `BOOTSTRAP_STATUS.md`, `GOVERNANCE.md`, `BUILD_CHECKLIST.md`, `docs/MODEL_EVIDENCE_BOUNDARY.md`, and `docs/SUBMISSION_READINESS_CHECKLIST.md` before implementation.
