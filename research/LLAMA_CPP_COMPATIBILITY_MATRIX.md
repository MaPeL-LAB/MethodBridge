# llama.cpp compatibility matrix

**Pinned bake-off runtime:** `ggml-org/llama.cpp@0329fcdac8c2477c2dda1d5e43fd2e3616b99655`

| Candidate | Documentary support position | Empirical admission |
|---|---|---|
| Qwen2.5-1.5B-Instruct | mature qwen2 conversion family | primary |
| Qwen3-1.7B | qwen3 GGUFs are used publicly; backend/quantization behavior still varies | primary |
| SmolLM3-3B | decoder-only GQA/NoPE; conversion and chat-template fidelity must be verified | primary |
| Phi-4-mini-instruct | public GGUF use exists; backend-specific failure history requires target-device smoke testing | conditional |
| Qwen3-4B-Instruct-2507 | qwen3 non-thinking upper-bound; BF16 source is larger than the scored memory budget | conditional, quantized only |
| Qwen3.5-2B | llama.cpp can run Qwen3.5-family GGUFs, but public issue history includes crashes, backend failures, multi-turn reprocessing and quant-specific problems | documentary watch only |

For every empirical candidate, compatibility means all of the following on the pinned source:

1. source revision can be acquired and hashed;
2. conversion completes without unsupported tensors or tokenizer loss;
3. GGUF metadata and chat template are inspectable;
4. Q4_K_M, Q5_K_M, and Q6_K load where generated;
5. one-shot and repeated-turn inference terminate correctly;
6. benchmark answers contain no leaked hidden reasoning when the response contract forbids it;
7. peak memory, throughput, TTFT and thermals are measured;
8. the official profiler accepts the exact artifact.

Documentary compatibility is never promoted to measured compatibility.
