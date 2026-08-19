# ADTC project report — evidence-gated draft

## Problem and context

MethodBridge Local explores whether a compact, offline model can provide useful research-methods and scientific-reasoning support to postgraduate and early-career researchers using ordinary laptops. The narrower user need and outcome pathway remain hypotheses requiring later user research.

## Constraints

The judged path is fully offline, uses GGUF and `llama.cpp`, targets an 8 GB laptop, and must retain headroom below the effective 7 GB memory limit. The internal engineering target is peak RSS at or below 6.0 GB; this is stricter than, and not a replacement for, the official rule.

## Architecture

The repository contains traceable source and dataset controls, candidate and upstream registries, a frozen public benchmark, a private-challenger boundary, GGUF conversion and quantization tooling, explicit simulation-proxy and real `llama.cpp` executors, hardware attestation, and fail-closed submission validation.

## Evidence status

No final model or quantization has been selected. No authoritative candidate accuracy, reasoning-retention, throughput, TTFT, peak RAM, steady RAM, perplexity, thermal, or official profiler result is available.

Earlier simulation/canned outputs were incorrectly described as empirical candidate and quantization findings. Those claims are withdrawn. The simulation proxy now states `measured: false` and cannot support ranking or submission evidence. The built-in keyword-overlap score is labelled `automated_keyword_proxy_pass_rate` and requires qualified semantic review.

`Qwen/Qwen3-1.7B` with `Q5_K_M` is only a provisional first-test hypothesis. It must not be described as a finalist until exact files, hashes, real `llama.cpp` output, semantic adjudication, quantization comparison, reference-laptop profiling, licence review, and human approval exist.

## Theory-of-Change boundary

The model may contribute educational and methodological support. It does not prove scientific validity, cause improved research quality by itself, replace qualified supervision, or establish social impact.
