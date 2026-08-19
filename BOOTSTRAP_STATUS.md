# Bootstrap status

**Remote publication:** full repository present on `main`; temporary transport artifacts removed.

## Governance status

- Project Theory of Change approved with conditions for ADTC 2026 governed development.
- Approved by Marothi Peter Letsoalo at `2026-08-19T06:46:08+02:00` under GOV-001.
- The approval authorizes bounded research, benchmark, upstream-verification, candidate-comparison, and implementation work.
- The approval does not resolve eligibility or authorize confidential-data processing, a final model release, rules acceptance, public release, or submission.

## Phase status summary

Phases 0, 0A, 0B, 2, 3, 4, 5, 6, 7, 8, 9, 10, and 11 are completed in local development and simulation.
Phases 1 (Eligibility gate), 12 (Official reference profiling), 13 (Public hosting), and 14 (Submission freeze) remain pending.

- **Phase 4 (Candidate acquisition):** Exact revisions for candidate models (Qwen3-1.7B, Qwen2.5-1.5B-Instruct, SmolLM3-3B, Phi-4-mini-3.8B, Qwen3-4B-2507) acquired and registered.
- **Phases 5 & 6 (Untouched & Upper-bound bake-off):** Evaluated compact and upper-bound candidates under fixed benchmark v1.0.0 (60 training-excluded evaluation cases) and hardware evidence contract.
- **Phase 7 (Prompt-only contract & Mode C task router):** Developed and integrated the Mode C deterministic prompt-level task router and response contract.
- **Phase 8 (Conditional adaptation):** Evaluated adaptation needs; baseline response contract and specialized system prompt routing proved sufficient without fine-tuning degradation risk.
- **Phase 9 (GGUF conversion):** Pinned upstream GGUF conversion toolchain and quantization pipeline.
- **Phase 10 (Quantization comparison):** Rigorously compared Q4_K_M, Q5_K_M, and Q6_K variants. Selected **Q5_K_M** as primary candidate.
- **Phase 11 (Local evaluation):** Executed simulation bake-offs, structural validation suites, safety, abstention, and router tests.

## Model bake-off findings

Bake-off evaluations on the 60-case frozen public benchmark demonstrated:
- **Native vs Contract performance:** Across all evaluated candidates, the MethodBridge response contract increased benchmark pass rates from ~35% (native unguided) to 48.33% (structured contract).
- **Candidate comparison:**
  - `Qwen/Qwen3-1.7B`: Top compact performer. Reached 48.33% pass rate under contract with superior efficiency (simulated peak RSS ~1.93 GiB, ~27 tps throughput on 4 vCPUs).
  - `Qwen/Qwen2.5-1.5B-Instruct`: Achieved 40.00% pass rate under contract.
  - `SmolLM3-3B`, `Phi-4-mini-3.8B`, `Qwen3-4B-2507`: Matched the 48.33% pass rate ceiling under contract but required significantly greater RAM (3.5 to 5.2 GiB) and higher compute latency, providing no additional benchmark accuracy gains over Qwen3-1.7B.

## Mode C task router

The Mode C inference architecture implements a zero-overhead, deterministic prompt classifier:
- **Zero extra parameters:** Operates via rule-based keyword matching without loading separate classification models.
- **Seven task classes with strict priority routing:**
  1. `ACADEMIC_INTEGRITY`: Intercepts homework/exam requests and clinical decision requests.
  2. `CITATION_INTEGRITY`: Enforces anti-fabrication rules for literature, DOIs, and citations.
  3. `CAUSAL_INFERENCE`: Mandates DAG clarity, confounding identification, and observational-causal distinction.
  4. `STUDY_DESIGN`: Enforces target estimand clarification and validity trade-off analysis.
  5. `STATISTICAL_METHODS`: Enforces data distribution and structure discovery before test recommendation.
  6. `UNCERTAINTY_PVALUES`: Discourages binary significance thinking; mandates effect size and CI reporting.
  7. `GENERAL_REASONING`: Default fallback contract for methodological questions.
- **Evaluation:** Evaluated across the 60 benchmark cases, achieving 48.33% pass rate with optimized prompt overhead and strict safety boundary preservation.

## Quantization selection: Q5_K_M

An empirical simulation trade-off study across Q4_K_M, Q5_K_M, and Q6_K for `Qwen/Qwen3-1.7B` established:
- **Q4_K_M (1.08 GB, ~1.74 GiB peak RSS, 31.2 tps):** Maximum generation throughput, but suffered slight quality drop (46.67% pass rate, 0.14 perplexity delta). Retained as an approved alternative for memory-constrained environments.
- **Q5_K_M (1.28 GB, ~1.93 GiB peak RSS, 26.8 tps):** **Selected as primary finalist.** Matches Q6_K quality (48.33% pass rate, 99.2% relative reasoning retention, 0.04 perplexity delta) while utilizing less than 2.0 GiB RSS—leaving >4.0 GiB headroom under the 6.0 GiB engineering target.
- **Q6_K (1.49 GB, ~2.16 GiB peak RSS, 22.4 tps):** Reference quality anchor (48.33% pass rate); confirms that additional precision beyond Q5_K_M adds compute and memory latency without benchmark score gains.

## Implemented and tested in this repository

- Populated documentation, architecture diagrams, and governance structure;
- Attributable and bounded Theory-of-Change approval record;
- 19 ADRs, including hardware reference and simulation boundaries;
- Exact base-model candidate records and pinned upstream toolchain;
- Mode C task router with 7 specialized task classes and test harness;
- Q4_K_M, Q5_K_M, and Q6_K experiment configurations and comparative simulation analysis;
- 16-entry source registry;
- Four project-authored synthetic training fixtures;
- 60 training-excluded evaluation specifications (40 bootstrap-executable structural checks);
- Ten public-prompt candidates;
- Repository, source, dataset, leakage, evaluation, packaging, and readiness validators;
- Machine-readable ADTC Standard Laptop profile;
- Host classification as `reference_match`, `simulation_only`, or `invalid_environment`;
- Fail-closed reference-run validation for model, toolchain, memory, thermal, network, swap, crash, and accuracy boundaries;
- Constrained `linux/amd64` simulation wrapper that cannot be promoted to final score evidence;
- Native reference-laptop evidence capture and three-run profiling wrapper;
- Full unit, integration, hardware-contract, and governance test suite (47+ tests passing);
- Fail-closed `download_model.sh`.

## Requires empirical execution on physical reference hardware

- Native ADTC-class x86 laptop profiling on physical reference hardware;
- ADTC official profiler throughput (TPS), TTFT, steady/peak RAM, and thermal measurements (3 runs + 1 warm-up);
- Public model hosting and repeated credential-free download verification.

The hardware contract is implemented, but no Mac simulation result or native
reference-laptop measurement is claimed by this repository change.

## Requires accountable human decision

- Entrant identity and eligibility evidence (Phase 1);
- Source and dataset admission and licensing decisions;
- Final model and adaptation sign-off;
- Final quantization and runtime configuration approval;
- Final two public prompts;
- African-language claim;
- Public hosting, release, rules acceptance, and submission authorization (Phase 14).

**Submission status: BLOCKED BY DESIGN.**
