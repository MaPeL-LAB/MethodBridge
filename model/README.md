---
language:
- en
license: apache-2.0
base_model: Qwen/Qwen3-1.7B
tags:
- gguf
- llama.cpp
- scientific-reasoning
- research-methods
- education
- offline-ai
- adtc-2026
pipeline_tag: text-generation
library_name: gguf
---

# MethodBridge: Offline Scientific Reasoning & Research-Methods Tutor (Qwen3-1.7B Q5_K_M GGUF)

## Summary

**MethodBridge** is an offline, privacy-first scientific reasoning and research-methods assistant engineered for postgraduate students and early-career researchers running on standard consumer laptops. MethodBridge delivers rigorous methodological feedback, causal inference critique, statistical interpretation, and pedagogical scaffolding without requiring internet access or cloud infrastructure.

## Model Details

- **Base Model:** `Qwen/Qwen3-1.7B`
- **Base Revision:** `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- **Quantization:** `Q5_K_M` (5-bit medium quantization with optimal perplexity/memory balance)
- **Format:** GGUF (v3)
- **Parameters:** ~1.7 Billion
- **Runtime:** `llama.cpp` (pinned commit: `0329fcdac8c2477c2dda1d5e43fd2e3616b99655`, CPU-only baseline)
- **Context Length:** 32,768 tokens (inference benchmark baseline: 2,048–4,096 tokens)
- **License:** Apache-2.0

## Domain & Intended Use

- **Primary Domain:** Scientific and mathematical reasoning, research methodology, study design critique, causal inference, and statistical interpretation.
- **Cross-Disciplinary Pairing:** Scientific Reasoning + Education (pedagogical scaffolding for postgraduate researchers).
- **Intended Use:**
  - Critiquing observational study designs and identifying confounding / selection bias.
  - Interpreting statistical effect sizes, confidence intervals, and p-values beyond binary significance testing.
  - Guiding students in structuring robust scientific inquiry and pre-registration hypotheses.
  - Offline tutoring in bandwidth-constrained, resource-limited academic environments.

## Hardware Target & Efficiency Contract

Engineered to strictly conform with the **Africa Deep Tech Challenge (ADTC) 2026 Standard Laptop** specification:
- **Architecture:** x86-64 (Intel Core i5 10th–12th Gen or AMD Ryzen 5 3000–5000)
- **System Memory:** ~8 GiB installed RAM
- **Graphics:** Integrated graphics only (0 GPU layers offloaded; CPU-only execution)
- **Storage:** >= 256 GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Memory Envelope:** Peak RSS target <= 6.0 GiB (Strict ceiling: 7.0 GiB)
- **Thermal Envelope:** Operating temperature <= 80 °C (Strict throttling boundary: 85 °C)
- **Network Isolation:** Fully functional with networking disabled during inference.
- **Swap Policy:** Operates safely with zero swap enabled.

## Download and Verification

### Download via Repository Script
```bash
# Set public model environment variables if not already baked in
export METHODBRIDGE_MODEL_URL="https://huggingface.co/MaPeL-LAB/MethodBridge-Qwen3-1.7B-Q5_K_M-GGUF/resolve/main/methodbridge-local-final.gguf"
export METHODBRIDGE_MODEL_SHA256="<SHA256_HEX>"

./download_model.sh
```

### Direct Download & Verification
```bash
mkdir -p model
curl --fail --location --proto '=https' --tlsv1.2 \
  "$METHODBRIDGE_MODEL_URL" \
  -o model/methodbridge-local-final.gguf

echo "$METHODBRIDGE_MODEL_SHA256  model/methodbridge-local-final.gguf" | sha256sum -c -
```

## Running Inference with llama.cpp

Execute with pinned `llama.cpp` CPU-only binary:

```bash
llama-cli \
  -m model/methodbridge-local-final.gguf \
  -p "<|im_start|>system\nYou are MethodBridge, an offline scientific reasoning and research-methods tutor.<|im_end|>\n<|im_start|>user\nA cohort study reports a risk ratio of 1.40 with a 95% confidence interval of 0.98 to 2.00 and p=0.064. Explain what can and cannot be concluded.<|im_end|>\n<|im_start|>assistant\n" \
  -n 512 \
  --temp 0.2 \
  --top-p 0.95 \
  -c 2048 \
  --threads 4
```

## Evaluation & Ethical Guardrails

- **Benchmark Evaluation:** Evaluated across 60 structured test cases in research methodology, causal inference, and statistical reporting.
- **Out of Scope:**
  - Clinical trial / patient-specific medical advice or diagnosis.
  - Institutional ethics committee, regulatory, or legal approvals.
  - Fabricating synthetic citations or academic ghost-writing.
  - Generating deceptive academic submissions.
- **Uncertainty & Abstention:** Explicitly abstains and flags methodological invalidity when presented with unadjusted observational confounders or underpowered designs.
