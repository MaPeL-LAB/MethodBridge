# Bootstrap status

**Remote publication:** full repository present on `main`; temporary transport artifacts removed.

## Governance status

- Project Theory of Change approved with conditions for ADTC 2026 governed development.
- Approved by Marothi Peter Letsoalo at `2026-08-19T06:46:08+02:00` under GOV-001.
- The approval authorizes bounded research, benchmark, upstream-verification, candidate-comparison, and implementation work.
- The approval does not resolve eligibility or authorize confidential-data processing, a final model release, rules acceptance, public release, or submission.

## Implemented and tested in this release

- populated documentation and governance structure;
- attributable and bounded Theory-of-Change approval record;
- 19 ADRs, including the native-reference-versus-simulation hardware boundary;
- exact base-model candidate records and pinned upstream toolchain;
- Q4_K_M, Q5_K_M, and Q6_K experiment configurations;
- 16-entry source registry;
- four project-authored synthetic training fixtures;
- 60 training-excluded evaluation specifications, of which 40 are bootstrap-executable structural checks;
- ten public-prompt candidates;
- repository, source, dataset, leakage, evaluation, packaging, and readiness validators;
- machine-readable ADTC Standard Laptop profile;
- host classification as `reference_match`, `simulation_only`, or `invalid_environment`;
- fail-closed reference-run validation for model, toolchain, memory, thermal, network, swap, crash, and accuracy boundaries;
- constrained `linux/amd64` simulation wrapper that cannot be promoted to final score evidence;
- native reference-laptop evidence capture and three-run profiling wrapper;
- hardware-contract tests and a dedicated GitHub Actions workflow;
- governance regression tests for the approved scope and retained human authority;
- fail-closed `download_model.sh`.

## Requires empirical execution

- model download and untouched baseline runs;
- any LoRA or QLoRA training;
- GGUF conversion and `llama.cpp` load tests;
- quantization quality comparison;
- constrained Mac simulation with real candidate GGUFs;
- native ADTC-class x86 laptop profiling;
- ADTC profiler throughput, TTFT, RAM, and thermal measurements;
- public model hosting and repeated credential-free download.

The hardware contract is implemented, but no Mac simulation result or native
reference-laptop measurement is claimed by this repository change.

## Requires accountable human decision

- entrant identity and eligibility evidence;
- source and dataset admission and licensing decisions;
- final model and any adaptation strategy;
- final quantization and runtime configuration;
- final two public prompts;
- African-language claim;
- public hosting, release, rules acceptance, and submission authorization.

**Submission status: BLOCKED BY DESIGN.**
