# ADTC project report — evidence-gated draft

## Problem and context

MethodBridge Local explores whether a compact, offline model can provide useful research-methods and scientific-reasoning support to postgraduate and early-career researchers using ordinary laptops. The narrower user need and outcome pathway remain hypotheses requiring user research.

## Constraints

The judged path is completely offline, uses GGUF and `llama.cpp`, targets an 8 GB laptop, and must retain headroom below the effective memory limit. The internal engineering target is peak RSS at or below 6.0 GB; this is stricter than, and not a replacement for, the official rule.

## Architecture

Authoritative licensed sources and project-authored synthetic examples feed a versioned dataset. Five compact candidates are evaluated before any tuning. Tuning is conditional. The finalist is converted once and independently quantized to Q4_K_M, Q5_K_M, and Q6_K. The same quality, retention, safety, and profiler protocol governs selection.

## Results

No final model, GGUF, profiler, TPS, TTFT, RAM, thermal, or accuracy result is available. This section must remain blocked until real measurements exist.

## Theory-of-Change boundary

The model may contribute educational and methodological support. It does not prove scientific validity, cause improved research quality by itself, replace qualified supervision, or establish social impact.
