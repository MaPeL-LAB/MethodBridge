# Build checklist

Each phase must produce evidence, acceptance criteria, and a rollback path. A checked item means the evidence is present and reviewable—not merely that code scaffolding exists.

- [x] **0. Remote foundation** — full repository published; transport removed; integrity controls added.
- [x] **0A. Theory-of-Change approval** — attributable approval recorded with bounded conditions.
- [x] **0B. Hardware evidence contract** — reference profile, simulation boundary, attestation, strict-run validation, scripts, tests, and CI implemented.
- [ ] **1. Eligibility gate** — resolve entrant identity, team age, funding, product stage, and Participation Agreement.
- [x] **2. Upstream freeze** — official template, profiler, `llama.cpp`, governance, and conditional adaptation toolchain pinned to reviewed commits.
- [x] **3. Benchmark engineering freeze** — 60 public training-excluded cases reviewed and hashed for consistent comparison; qualified semantic adjudication remains required.
- [ ] **4. Candidate acquisition** — acquire exact licensed revisions locally; archive licence/model-card evidence; record complete file hashes. The remote documentary registry alone does not complete this phase.
- [ ] **5. Untouched bake-off** — run real candidate GGUFs through digest-bound `llama.cpp`; retain raw outputs locally; compare under one frozen configuration; obtain qualified semantic review.
- [ ] **6. Upper-bound bake-off** — admit larger candidates only after licence, compatibility, memory, and thermal smoke gates pass.
- [ ] **7. Prompt-only comparison** — compare native, MethodBridge contract, and Mode C using actual model output. Router plumbing is implemented; its model effect is not yet established.
- [ ] **8. Conditional adaptation** — authorize LoRA/QLoRA only after repeated learnable gaps remain under real prompt-only comparison.
- [ ] **9. GGUF conversion** — convert the human-approved source candidate through the pinned toolchain and bind the output to its SHA-256.
- [ ] **10. Quantization comparison** — independently generate Q4_K_M, Q5_K_M, and Q6_K from the same source model; compare real quality and resource evidence. No quantization is currently selected.
- [ ] **11. Local evaluation** — complete real outputs, private challenger, safety, retention, robustness, and attributable semantic adjudication. Simulation-proxy and keyword-proxy results cannot complete this phase.
- [ ] **12. Official profiling** — on a native `reference_match` laptop, collect one warm-up and three complete participant-mode runs covering accuracy, TPS, TTFT, peak/steady RSS, thermals, crashes, OOM, network, swap, and digests.
- [ ] **13. Hosting** — publish the exact approved GGUF without credentials; verify byte identity, hash, idempotent download, and clean `llama.cpp` load.
- [ ] **14. Submission freeze** — finalize metadata, report, model/data cards, two human-approved prompts, architecture, video, clean-clone evidence, reference-run evidence, eligibility, rules review, and accountable authorization.

## Evidence rules

- A simulation proxy can validate plumbing only.
- `automated_keyword_proxy_pass_rate` is not accuracy or expert judgment.
- Local real model output requires an exact GGUF digest and pinned runtime.
- Official performance and thermal claims require the official profiler on a qualifying native reference host.
- An unresolved or failed eligibility, licence, load, memory, crash, thermal, leakage, toolchain, evidence, or critical-quality gate stops the candidate.
- CI and agents may validate evidence but may never select the final model or authorize release/submission.
