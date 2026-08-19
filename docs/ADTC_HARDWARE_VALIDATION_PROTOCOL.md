# ADTC Hardware Validation Protocol

**Status:** implemented contract; empirical reference-laptop evidence not yet collected.

## Purpose

MethodBridge separates development convenience from submission-grade evidence.
A host can be useful for model development without matching the hardware used for
ADTC scoring. The repository therefore classifies every run as:

```text
reference_match
simulation_only
invalid_environment
```

Only `reference_match` evidence may support the final self-reported performance,
memory, and thermal results. The organizer's audit remains controlling.

## Reference profile

The machine-readable source is `config/adtc_standard_laptop.yml`.

| Component | Contract |
|---|---|
| Architecture | x86-64 |
| CPU | Intel Core i5 10th–12th generation or AMD Ryzen 5 3000–5000 |
| RAM | approximately 8 GiB installed |
| Graphics | integrated only; no discrete GPU |
| Storage | at least 256 GB SSD |
| OS | Ubuntu 22.04 LTS |
| Runtime | pinned `llama.cpp`, GGUF, CPU-only baseline |
| Scored RAM ceiling | 7.0 GiB peak RSS |
| Internal RAM target | no more than 6.0 GiB peak RSS |
| Thermal penalty boundary | more than 85 °C or throttling |
| Internal thermal target | no more than 80 °C |
| Network | disabled during inference |
| Strict swap policy | disabled |
| Repetition | one warm-up and three complete measured runs |

Reverify the official challenge pages, submission template, profiler, and scoring
rules immediately before final profiling. A repository contract cannot override
a later official rule.

## Evidence classes

### Development host

Native macOS, Apple Silicon, Linux workstations, cloud machines, and other
non-reference systems may be used for:

- acquisition and conversion;
- prompt and chat-template debugging;
- functional `llama.cpp` smoke tests;
- benchmark-harness development;
- preliminary memory stress testing;
- offline and no-network testing.

Their results must be marked `simulation_only`.

### Constrained simulation

`scripts/run_adtc_simulated_profile.sh` runs a CPU-only `linux/amd64` container
with four vCPUs, 7.5 GiB memory, no additional swap, no network, no GPU exposure,
a read-only submission mount, and bounded writable artifacts.

It can detect packaging, load, memory, prompt-template, and runtime failures. It
cannot establish native x86 throughput, first-token latency, memory bandwidth,
or thermal behaviour because emulation and the host kernel remain different.

### Native reference host

Authoritative participant evidence requires a native qualifying x86 laptop.
`scripts/run_adtc_reference_profile.sh` fails closed unless:

- the host classifier returns `reference_match`;
- the ADTC profiler and `llama-bench` are installed;
- strict swap is disabled;
- the operator has independently disabled and verified inference networking.

The wrapper runs one non-scoreable warm-up followed by three full participant
runs. The final run record must pass
`scripts/verify_adtc_reference_run.py`.

## Acceptance rules

A reference record is rejected when any of the following is true:

- the host is not `reference_match`;
- the model is not GGUF;
- the model, profiler, or `llama.cpp` digest is malformed or inconsistent;
- GPU offload is enabled;
- inference networking was available;
- swap was enabled;
- the accuracy stage was skipped in a measured run;
- fewer than three complete measured runs exist;
- a run crashed or reported OOM;
- peak RSS exceeds 7.0 GiB;
- temperature exceeds 85 °C;
- throttling occurred;
- model or toolchain identifiers differ between runs.

Peak RSS above 6.0 GiB and temperature above 80 °C produce warnings even when
the official limits are not exceeded.

## Conservative reporting

Preserve all raw runs. Summarize with:

- maximum observed peak RSS;
- maximum observed temperature;
- any throttling event;
- median generation throughput;
- median first-token latency;
- exact GGUF SHA-256;
- exact profiler and `llama.cpp` commits.

Do not select only the most favourable run.

## Evidence location

Runtime evidence remains ignored under:

```text
artifacts/adtc-simulation/
artifacts/adtc-reference/
```

After review, commit only sanitized summaries that contain no credentials,
private paths, participant information, or unsupported performance claims.
