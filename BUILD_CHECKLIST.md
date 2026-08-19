# Build checklist

Each phase must produce evidence, acceptance criteria, and a rollback path. A
checked item means the evidence is present and reviewable—not merely that code
scaffolding exists.

- [x] **0. Remote foundation** — full repository published; transport removed; integrity controls added.
- [x] **0A. Theory-of-Change approval** — attributable approval recorded with bounded conditions.
- [x] **0B. Hardware evidence contract** — reference profile, simulation boundary, attestation, strict-run validation, scripts, tests, and CI implemented.
- [x] **0C. Model-evidence correction** — simulation and real execution separated; unsupported claims withdrawn.
- [x] **0D. Local empirical campaign contract** — campaign schema, execution authorization fields, shareable run evidence, semantic review, stopping rules, and local handoff implemented.
- [x] **0E. Public claims and release gate** — model card, demo, Devpost, metadata, and release tooling remain blocked until immutable evidence and human authorization agree.
- [ ] **1. Eligibility gate** — resolve entrant identity, team age, funding, product stage, and Participation Agreement.
- [x] **2. Upstream freeze** — official template, profiler, `llama.cpp`, governance, and conditional adaptation toolchain pinned to reviewed commits.
- [x] **3. Benchmark engineering freeze** — 60 public training-excluded cases reviewed and hashed; qualified semantic adjudication remains required.
- [ ] **4. Candidate acquisition** — acquire exact licensed revisions locally; archive licence/model-card evidence; record complete file hashes.
- [ ] **5. Untouched bake-off** — run real candidate GGUFs through digest-bound `llama.cpp`; retain raw outputs locally; create shareable run evidence; obtain qualified semantic review.
- [ ] **6. Upper-bound bake-off** — admit larger candidates only after licence, compatibility, memory, and thermal smoke gates pass.
- [ ] **7. Prompt-only comparison** — compare native, MethodBridge contract, and Mode C using actual model output under one campaign configuration.
- [ ] **8. Conditional adaptation** — authorize LoRA/QLoRA only after repeated learnable gaps remain under real prompt-only comparison.
- [ ] **9. GGUF conversion** — convert the human-approved source candidate through the pinned toolchain and bind output to SHA-256.
- [ ] **10. Quantization comparison** — independently generate Q4_K_M, Q5_K_M, and Q6_K from the same source model; compare real quality and resource evidence.
- [ ] **11. Local evaluation** — complete real outputs, private challenger, safety, retention, robustness, and attributable semantic adjudication.
- [ ] **12. Official profiling** — on a native `reference_match` laptop, collect one warm-up and three complete participant-mode runs.
- [ ] **13. Hosting** — publish the exact approved GGUF without credentials; verify byte identity, hash, idempotent download, and clean `llama.cpp` load.
- [ ] **14. Submission freeze** — finalize metadata, report, cards, prompts, architecture, video, clean-clone evidence, reference-run evidence, eligibility, rules review, and accountable authorization.

## Immediate local handoff

```bash
make gate
make prelocal
python scripts/prepare_model_release.py --check
```

The release check is expected to remain blocked. The empirical authorization
field is also expected to remain false until eligibility and a named human
decision are recorded.

## Evidence rules

- A simulation proxy can validate plumbing only.
- `automated_keyword_proxy_pass_rate` is not accuracy or expert judgment.
- Local real model output requires an exact GGUF digest and pinned runtime.
- Qualified semantic review is mandatory before candidate comparison.
- Official performance and thermal claims require the official profiler on a qualifying native reference host.
- An unresolved or failed eligibility, licence, load, memory, crash, thermal, leakage, toolchain, evidence, or critical-quality gate stops the candidate.
- CI and agents may validate evidence but may never select the final model or authorize release or submission.
