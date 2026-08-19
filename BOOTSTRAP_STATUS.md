# Bootstrap status

## Implemented and tested in this recovered release

- populated documentation and governance structure;
- 18 ADRs;
- five base-model candidate records;
- Q4_K_M, Q5_K_M, and Q6_K experiment configurations;
- 16-entry source registry;
- four project-authored synthetic training fixtures;
- 60 held-out evaluation specifications, of which 40 are bootstrap-executable structural checks;
- ten public-prompt candidates;
- repository, source, dataset, leakage, evaluation, packaging, and readiness validators;
- seven-plus automated repository tests;
- fail-closed `download_model.sh`.

## Requires empirical execution

- model download and untouched baseline runs;
- any LoRA or QLoRA training;
- GGUF conversion and `llama.cpp` load tests;
- quantization quality comparison;
- ADTC profiler throughput, TTFT, RAM, and thermal measurements;
- public model hosting and repeated credential-free download.

## Requires accountable human decision

- entrant identity and eligibility evidence;
- Theory-of-Change approval;
- final model and quantization;
- dataset admission and licensing decisions;
- final two public prompts;
- African-language claim;
- release and submission authorization.

**Submission status: BLOCKED BY DESIGN.**
