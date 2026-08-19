# Build checklist

Each phase must produce evidence, acceptance criteria, and a rollback path.

- [x] **0. Remote foundation** — full repository published, transport removed, integrity checks and local handoff added.

- [ ] **1. Eligibility gate** — resolve entrant identity, team age, funding, product stage, and Participation Agreement.
- [ ] **2. Upstream freeze** — reverify and pin ADTC template, profiler, `llama.cpp`, and governance commits.
- [ ] **3. Benchmark review** — qualified human review of all 60 cases and final held-out freeze.
- [ ] **4. Candidate acquisition** — download exact licensed model revisions; record hashes and licences.
- [ ] **5. Untouched bake-off** — run Qwen3-1.7B, Qwen3.5-2B, and SmolLM3-3B first.
- [ ] **6. Upper-bound bake-off** — add Phi-4-mini and Qwen3-4B if time and resources permit.
- [ ] **7. Prompt-only contract** — compare untouched versus MethodBridge response contract.
- [ ] **8. Conditional adaptation** — LoRA/QLoRA only if repeated learnable gaps justify it.
- [ ] **9. GGUF conversion** — convert the finalist through the pinned toolchain.
- [ ] **10. Quantization comparison** — independently produce Q4_K_M, Q5_K_M, and Q6_K.
- [ ] **11. Local evaluation** — run MethodBridge, retention, safety, and robustness suites.
- [ ] **12. Official profiling** — collect TPS, TTFT, peak RSS, steady RSS, thermals, and profiler scores.
- [ ] **13. Hosting** — publish the exact winning GGUF without credentials; verify hash and idempotency.
- [ ] **14. Submission freeze** — finalize metadata, report, two prompts, architecture, video, and clean-clone evidence.

A failed eligibility, licence, load, memory, crash, thermal, or critical-quality gate stops the candidate.
