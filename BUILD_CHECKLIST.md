# Build checklist

Each phase must produce evidence, acceptance criteria, and a rollback path.

- [x] **0. Remote foundation** — full repository published, transport removed, integrity checks and local handoff added.
- [x] **0A. Theory-of-Change approval** — accountable review completed and approved with conditions under GOV-001; approval is limited to governed ADTC development and does not authorize release or submission.

- [ ] **1. Eligibility gate** — resolve entrant identity, team age, funding, product stage, and Participation Agreement.
- [ ] **2. Upstream freeze** — reverify and pin ADTC template, profiler, `llama.cpp`, governance, training, conversion, and quantization commits.
- [ ] **3. Benchmark review** — qualified human review of all 60 cases and final held-out freeze.
- [ ] **4. Candidate acquisition** — download exact licensed model revisions; record hashes and licences.
- [ ] **5. Untouched bake-off** — run the first approved compact-model candidates under one fixed benchmark and runtime contract.
- [ ] **6. Upper-bound bake-off** — add larger candidates only if time, licence, memory, and thermal headroom permit.
- [ ] **7. Prompt-only contract** — compare untouched models with and without the MethodBridge response contract.
- [ ] **8. Conditional adaptation** — LoRA/QLoRA only if repeated learnable gaps justify it.
- [ ] **9. GGUF conversion** — convert the finalist through the pinned toolchain.
- [ ] **10. Quantization comparison** — independently produce and compare Q4_K_M, Q5_K_M, and Q6_K or a documented replacement.
- [ ] **11. Local evaluation** — run MethodBridge, retention, safety, robustness, and abstention suites.
- [ ] **12. Official profiling** — collect TPS, TTFT, peak RSS, steady RSS, thermals, and profiler scores.
- [ ] **13. Hosting** — publish the exact winning GGUF without credentials; verify hash and idempotency.
- [ ] **14. Submission freeze** — finalize metadata, report, two prompts, architecture, video, clean-clone evidence, and accountable authorization.

A failed eligibility, licence, load, memory, crash, thermal, leakage, or critical-quality gate stops the candidate. The Theory-of-Change approval must be reopened after a material change to the primary user, causal pathway, contribution boundary, protected decisions, data boundary, or intended deployment.
