# MethodBridge Local

**Repository:** `MaPeL-LAB/MethodBridge`  
**Product:** MethodBridge Local  
**Release status:** recovered implementation bootstrap `v0.1.0-recovered`  
**ADTC domain:** `math_scientific_reasoning`  
**Cross-disciplinary pairing:** education  
**Submission ready:** **No**

MethodBridge Local is a compact, fully offline scientific-reasoning and research-methods model intended for postgraduate students and early-career researchers who need immediate methodological guidance on ordinary laptops. The judged product is the model itself: GGUF weights, `llama.cpp`, CPU-first execution, a public credential-free download, and evidence of quality, throughput, memory use, and thermal stability.

This repository is a **populated engineering foundation**, not a trained model release. It includes governance, a draft Theory of Change, 18 architecture decisions, five candidate model families, three quantization plans, 60 held-out evaluation specifications, four safe synthetic dataset fixtures, source/licensing controls, validation scripts, CI workflows, and a fail-closed submission contract.

## Current truth

| Area | State |
|---|---|
| Product and domain scope | Accepted with conditions |
| Theory of Change | Populated draft; accountable approval pending |
| Entrant eligibility | Unresolved |
| Final base model | Requires empirical bake-off |
| Fine-tuning | Conditional; not assumed |
| Final GGUF | Not built |
| Official profiler | Not run |
| Public model URL and SHA-256 | Unresolved |
| Video and final submission | Not completed |

## Engineering sequence

```text
eligibility and upstream recheck
        ↓
freeze held-out benchmark
        ↓
untouched model bake-off
        ↓
prompt-only response contract
        ↓
LoRA/QLoRA only if justified
        ↓
GGUF conversion
        ↓
Q4_K_M / Q5_K_M / Q6_K comparison
        ↓
llama.cpp + ADTC profiler
        ↓
public credential-free model hosting
        ↓
final report, prompts, video, submission
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
python scripts/run_evaluation.py --dry-run
python -m pytest -q
python scripts/verify_submission_readiness.py
```

The final command is expected to return a **blocked** status until eligibility, the final GGUF, the public download, and official profiler evidence exist.

## Non-negotiable boundaries

MethodBridge may explain and critique research methods. It may not approve protocols, analysis plans, ethics, clinical care, legal compliance, or institutional decisions. It must not fabricate citations or facilitate deceptive assessed work. Real participant data, confidential documents, credentials, model weights, and private held-out prompts must not be committed.

See `BOOTSTRAP_STATUS.md`, `GOVERNANCE.md`, `BUILD_CHECKLIST.md`, and `docs/SUBMISSION_READINESS_CHECKLIST.md` before implementation.
