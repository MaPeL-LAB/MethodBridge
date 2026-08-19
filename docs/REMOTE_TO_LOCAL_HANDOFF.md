# Remote-to-local implementation handoff

**Status:** ready for local execution after the governance and eligibility gates.

The remote repository now contains the complete credential-free foundation.
Work should remain remote-first until a step requires model downloads, sustained
compute, target-device measurement, private credentials, or desktop video capture.

## What is complete remotely

- product and domain boundary;
- Theory-of-Change draft and protected human decisions;
- source/licence register and synthetic fixtures;
- 60 held-out evaluation specifications;
- base-model and quantization experiment contracts;
- conversion, evaluation, and readiness scaffolding;
- fail-closed model download contract;
- CI, data-governance, link, and security checks.

## What must happen before large local work

1. Obtain a written organizer response on the entrant/team-age interpretation.
2. Record the accountable entrant and Theory-of-Change decision.
3. Recheck and freeze the exact ADTC template, profiler, `llama.cpp`, and model revisions.
4. Have a qualified reviewer inspect all 60 cases and freeze the private split.
5. Confirm every candidate model licence and redistribution condition.

## Local empirical sequence

```text
untouched model acquisition and hashes
        ↓
same-device baseline bake-off
        ↓
prompt-only MethodBridge response contract
        ↓
conditional LoRA/QLoRA only for repeated learnable gaps
        ↓
merge and convert the finalist to GGUF
        ↓
Q4_K_M / Q5_K_M / Q6_K comparison
        ↓
llama.cpp quality, retention, safety, memory, and thermal tests
        ↓
official ADTC participant profiler
        ↓
public credential-free model hosting and repeated download
        ↓
final metadata, REPORT.md, two prompts, video, and clean-clone review
```

## Local stopping rules

Stop and return to governance review when:

- eligibility is rejected or remains materially ambiguous;
- a candidate licence is unclear or incompatible;
- a model cannot load through the pinned `llama.cpp` path;
- peak memory approaches the 7 GB official ceiling without adequate headroom;
- the process crashes, overheats, or throttles;
- specialization materially degrades general scientific reasoning;
- a dataset or evaluation split shows contamination;
- a model invents citations or fails critical human-authority tests;
- public hosting cannot be made credential-free and reproducible.

## Required local return envelope

For each experiment return:

```text
branch and commit
candidate and exact revision
licence and source record
configuration and random seed
commands executed
hardware and OS
quality and retention results
TPS, TTFT, peak RSS, and thermals
failures and skipped checks
artifacts and hashes
recommendation and rollback
unresolved human decisions
```
