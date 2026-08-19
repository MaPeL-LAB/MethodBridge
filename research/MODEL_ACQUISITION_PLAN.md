# Model acquisition plan

Acquire models only after `scripts/validate_upstream_and_candidates.py` passes and an accountable human authorizes the download window.

For each admitted candidate:

1. create a candidate-specific local directory outside Git;
2. download the exact revision without credentials where possible;
3. save the licence, model card, config, tokenizer and file inventory;
4. compute SHA-256 for every acquired file;
5. record acquisition time, command, tool version and source revision;
6. convert with the pinned llama.cpp checkout;
7. retain the original source artifact until GGUF comparison is complete;
8. never upload source weights or derived GGUFs to Git;
9. stop on changed upstream content, authentication requirement, unclear licence, incomplete download or hash mismatch.

The first empirical wave is Qwen2.5-1.5B-Instruct, Qwen3-1.7B and SmolLM3-3B. Conditional upper-bound candidates follow only when the first wave is stable. Qwen3.5-2B remains deferred until a dedicated compatibility smoke test passes.
