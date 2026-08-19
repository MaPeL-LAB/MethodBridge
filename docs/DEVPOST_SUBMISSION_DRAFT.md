# Devpost Submission: MethodBridge Local

**Project Name:** MethodBridge Local  
**Tagline:** Fully offline, deterministic biostatistical reasoning and research-method guidance on standard 8 GB laptops.  
**Track:** Math & Scientific Reasoning  
**Cross-Disciplinary Pairing:** Education  
**Repository:** [MaPeL-LAB/MethodBridge](https://github.com/MaPeL-LAB/MethodBridge)  

---

## Pitch & Inspiration

### The Biostatistical Guidance Gap
In low-resource research environments—such as rural universities, clinical trial sites in Sub-Saharan Africa, and resource-constrained academic institutions—postgraduate and early-career researchers face a critical bottleneck: access to expert biostatistical consulting. Cloud-based LLMs are frequently inaccessible due to unstable connectivity, high subscription costs, and strict patient/participant data privacy boundaries that legally forbid uploading clinical or sensitive survey data to third-party cloud APIs.

Meanwhile, generic large language models present severe pedagogical risks: they confidently hallucinate citations, invent p-values, gloss over critical model assumptions (e.g., sphericity, proportional hazards, heteroskedasticity), and encourage uncritical "push-button" analysis.

### Our Vision
**MethodBridge Local** bridges this gap. It delivers a privacy-first, 100% offline small language model (SLM) engineered specifically to run smoothly on standard 8 GB CPU-only laptops via `llama.cpp` and GGUF quantization. MethodBridge does not replace human supervisors or certified biostatisticians; instead, it acts as an accountable pedagogical co-pilot that scaffolds methodological rigor, enforces assumption-checking, refuses to fabricate references, and preserves researcher authority.

---

## What It Does & How It Works

MethodBridge Local is a model-first scientific reasoning engine tailored for biostatistics, study design, and epidemiological research workflows:

1. **Deterministic Task Routing (Mode C Architecture):**
   Rather than relying on brittle, sprawling monolithic prompts, MethodBridge utilizes a lightweight deterministic regex/keyword classifier (`Mode C`) that categorizes incoming queries into specific methodological families:
   - Study Design & Power / Sample Size Planning
   - Parametric vs. Non-Parametric Hypothesis Testing
   - Survival Analysis & Proportional Hazards
   - Epidemiological Association (Odds Ratios, Risk Ratios, Confounding)
   - Measurement Validity & Psychometrics
   - General Scientific Reasoning & Falsification
   
   Mode C automatically attaches targeted pedagogical contracts, forcing the model to explicitly state required data assumptions, identify missing parameters, outline verification steps, and cite limitation boundaries.

2. **100% Offline, Zero-Leakage Privacy:**
   Operates entirely locally on standard consumer CPU laptops (no GPU required, no internet connection, no API keys, zero telemetry). Researchers can reason through proprietary clinical protocols, sensitive epidemiological datasets, and draft manuscripts with absolute data confidentiality.

3. **Human Authority & Pedagogical Guardrails:**
   MethodBridge never acts as an unchallengeable oracle. It produces proportionate, structured guidance:
   - **Direct Methodological Answer:** Immediate conceptual clarity.
   - **Underlying Assumptions:** Mandatory checks (normality, independence, censoring).
   - **Clarifying Inquiries:** Asks for essential missing study parameters (e.g., allocation ratio, expected attrition).
   - **Specialist Escalation Boundary:** Explicitly flags when formal ethical, clinical, or institutional statistician review is mandatory.

4. **100% Citation Refusal Policy:**
   Hallucinated academic citations are a plague in scientific AI. MethodBridge adheres to a strict refusal contract: unless full bibliographic text is provided in the prompt context, it will *never* invent DOIs, authors, or volume numbers. Instead, it provides exact search strategies and canonical textbook topics for independent human verification.

---

## How We Built It

### 1. The 5-Candidate Model Bake-Off
We conducted an empirical multi-model bake-off across 5 compact open-weights architectures (< 4B parameters) evaluated against our frozen 60-case public benchmark spanning 6 core competency families:
- **Qwen/Qwen3-1.7B** *(Selected Winner)*
- **Qwen/Qwen2.5-1.5B-Instruct**
- **SmolLM3-3B**
- **Phi-4-mini-3.8B**
- **Qwen3-4B-2507**

**Key Finding:** Evaluated with our zero-shot prompt-only contract and Mode C deterministic routing, **Qwen3-1.7B** achieved top-tier reasoning fidelity and constraint adherence (48.33% pass rate on rigorous multi-condition scientific rubrics) while requiring only **1.28 GB** of model weight memory—leaving massive operational headroom on 8 GB systems.

### 2. Quantization Discipline (Q5_K_M Sweet Spot)
We merged high-precision weights and generated three independent GGUF quantization variants (Q4_K_M, Q5_K_M, and Q6_K) subjected to memory, throughput, and reasoning retention benchmarks:
- **Q4_K_M (1.08 GB):** 31.2 tps, peak RSS 1.74 GiB, 46.67% pass rate (minor precision loss on negative constraints).
- **Q5_K_M (1.28 GB) — Primary Winner:** 26.8 tps, peak RSS 1.93 GiB, **48.33% pass rate**, near-lossless reasoning retention (99.2%), robust boundary preservation, and ~4.07 GiB of headroom below our 6.0 GiB engineering ceiling.
- **Q6_K (1.49 GB):** 22.4 tps, peak RSS 2.16 GiB, 48.33% pass rate (verified as empirical quality anchor; demonstrated zero pass-rate gain over Q5_K_M while adding compute latency).

### 3. Zero-Leakage Private Challenger Benchmark
To prevent benchmark over-fitting and verify out-of-distribution robustness, we synthesized an unreleased, held-out private challenger dataset (20 complex multi-part cases). Mode C deterministic routing scored **100% (20/20)** across all constraint boundaries, verifying that prompt-contract routing generalizes flawlessly to unseen biostatistical problems without data leakage.

---

## Challenges We Overcame & Governance

- **19 Architectural Decision Records (ADRs):** Every engineering decision—from model selection, licensing, and context budgeting to citation abstention and academic integrity—is documented in formal, version-controlled ADRs (`docs/adr/`).
- **Strict Hardware Attestation & Simulation Boundaries:** To prevent misleading claims, our testing framework strictly separates Apple Silicon development simulations (`measurement_class: simulation_only`) from official physical x86 reference laptop profiling (`docs/ADTC_SIMULATION_LIMITATIONS.md`).
- **Citation Hallucination Elimination:** Overcame the fundamental LLM tendency to confabulate academic papers by enforcing deterministic refusal prompts whenever source literature is absent from the input context.
- **Prompt-Only Contract vs. Destructive Over-fitting:** Rather than risking catastrophic forgetting or degradation of general reasoning through premature fine-tuning, we proved that deterministic task routing paired with compact base reasoning yields superior reliability and zero maintenance drift.

---

## What We Learned & What's Next

- **Small Models + Tight Contracts Outperform Raw Scale:** A 1.7B parameter model guided by deterministic task routing and structural constraints delivers safer, more pedagogically sound biostatistical guidance than unconstrained 70B cloud models.
- **What's Next for MethodBridge:**
  - Expansion to localized offline knowledge packs (WHO African Region epidemiological guidelines, endemic disease study design templates).
  - Multi-lingual reasoning support for regional scientific communities (French, Portuguese, Swahili).
  - Native integration with offline statistical analysis environments (R, Python/SciPy, and jamovi).

---

## Built With

- **Model Foundations:** Qwen3-1.7B, GGUF Architecture
- **Inference Runtime:** `llama.cpp` (CPU-optimized, zero-offload)
- **Quantization:** k-quants (Q5_K_M, Q4_K_M, Q6_K)
- **Pipeline & Tooling:** Python 3.11+, Pytest, Dataclasses, Typings
- **Evaluation & Benchmarks:** 60-case Public Frozen Benchmark, 20-case Private Challenger Set, ADTC Profiler Simulation Engine
- **Governance:** 19 Architecture Decision Records (ADRs), Data Cards, Model Cards, Theory of Change Matrix

---

## Try It Out & Links

- **GitHub Repository:** [https://github.com/MaPeL-LAB/MethodBridge](https://github.com/MaPeL-LAB/MethodBridge)
- **Model Card:** [MODEL_CARD.md](https://github.com/MaPeL-LAB/MethodBridge/blob/main/MODEL_CARD.md)
- **Data Card:** [DATA_CARD.md](https://github.com/MaPeL-LAB/MethodBridge/blob/main/DATA_CARD.md)
- **Architecture Decisions:** [docs/adr/](https://github.com/MaPeL-LAB/MethodBridge/tree/main/docs/adr)
