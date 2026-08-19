# Build checklist

Each phase must produce evidence, acceptance criteria, and a rollback path.

- [x] **0. Remote foundation** — full repository published, transport removed, integrity checks and local handoff added.
- [x] **0A. Theory-of-Change approval** — accountable review completed and approved with conditions under GOV-001; approval is limited to governed ADTC development and does not authorize release or submission.
- [x] **0B. Hardware evidence contract** — reference-laptop profile, simulation boundary, host attestation, strict-run validation, scripts, tests, and CI implemented. No empirical reference result is claimed.

- [ ] **1. Eligibility gate** — resolve entrant identity, team age, funding, product stage, and Participation Agreement.
- [x] **2. Upstream freeze** — ADTC template, profiler, `llama.cpp`, governance, training, and adaptation toolchain pinned to reviewed immutable commits.
- [x] **3. Benchmark engineering freeze** — all 60 public training-excluded cases reviewed, hashed, and frozen for consistent comparison; attributable semantic adjudication remains required for final model decisions.
- [x] **4. Candidate acquisition** — download exact licensed model revisions; record hashes, notices, and licences.
- [x] **5. Untouched bake-off** — run the first approved compact-model candidates under one fixed benchmark, prompt, runtime, and hardware-evidence contract.
- [x] **6. Upper-bound bake-off** — add larger candidates only if time, licence, memory, and thermal headroom permit.
- [x] **7. Prompt-only contract** — compare untouched models with and without the MethodBridge response contract.
- [x] **8. Conditional adaptation** — LoRA/QLoRA only if repeated learnable gaps justify it.
- [x] **9. GGUF conversion** — convert the finalist through the pinned toolchain.
- [x] **10. Quantization comparison** — independently produce and compare Q4_K_M, Q5_K_M, and Q6_K or a documented replacement.
- [x] **11. Local evaluation** — run MethodBridge, retention, safety, robustness, abstention, and constrained simulation suites.
- [ ] **12. Official profiling** — on a native `reference_match` laptop, collect one warm-up and three complete runs covering TPS, TTFT, peak RSS, steady RSS, thermals, crashes, OOM, network, swap, and toolchain/model digests.
- [ ] **13. Hosting** — publish the exact winning GGUF without credentials; verify hash and idempotency.
- [ ] **14. Submission freeze** — finalize metadata, report, two prompts, architecture, video, clean-clone evidence, reference-run evidence, and accountable authorization.

A failed eligibility, licence, load, memory, crash, thermal, leakage, hardware,
toolchain, or critical-quality gate stops the candidate. A `simulation_only`
result can reject a candidate but can never establish final ADTC performance,
efficiency, or thermal claims. The Theory-of-Change approval must be reopened
after a material change to the primary user, causal pathway, contribution
boundary, protected decisions, data boundary, or intended deployment.
