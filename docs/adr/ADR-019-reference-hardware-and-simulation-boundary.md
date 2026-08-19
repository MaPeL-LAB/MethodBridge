# ADR-019: Reference hardware and simulation boundary

- **Status:** accepted
- **Date:** 2026-08-19
- **Authority:** MethodBridge governed development under GOV-001
- **Review trigger:** official ADTC hardware or profiler contract changes

## Context

MethodBridge is developed primarily on an Apple Silicon Mac, while ADTC scores
submissions against a native x86-64 Ubuntu laptop class. Artificially reducing
RAM on the Mac does not reproduce the target CPU, memory hierarchy, integrated
graphics, operating system, or thermals. Treating those measurements as
equivalent would create misleading performance and efficiency claims.

## Decision

The repository will distinguish:

1. `reference_match` — native qualifying x86 Ubuntu host;
2. `simulation_only` — useful non-reference development or constrained
   simulation host;
3. `invalid_environment` — incomplete or prohibited environment.

Only a `reference_match` record that passes the hardware, runtime, repetition,
memory, network, swap, accuracy, crash, and thermal gates may support final
participant profiler claims.

Apple Silicon and other non-reference hosts may run a constrained CPU-only
`linux/amd64` simulation, but those results are never eligible for the final
self-reported ADTC score.

## Consequences

- Hardware identity becomes a machine-readable input to every measured run.
- Mac simulation can reject unsafe candidates early but cannot select the final
  candidate on performance or thermals.
- A native reference laptop must be secured before the final profiling window.
- Internal targets are stricter than official boundaries: no more than 6 GiB
  peak RSS and no more than 80 °C.
- Final evidence requires one warm-up and three complete measured runs.
- The organizer audit remains authoritative.

## Rejected alternatives

### Treat the M4 Max as equivalent after setting a memory limit

Rejected because CPU architecture, memory bandwidth, caches, scheduling, GPU
sharing, and thermals remain materially different.

### Use only a cloud x86 VM

Rejected as final evidence because it does not reproduce the published commodity
laptop and integrated-graphics thermal profile.

### Use a single successful run

Rejected because one run cannot establish stability or protect against
favourable-run selection.

## Implementation

- `config/adtc_standard_laptop.yml`
- `src/methodbridge/hardware.py`
- `scripts/check_adtc_host.py`
- `scripts/run_adtc_simulated_profile.sh`
- `scripts/run_adtc_reference_profile.sh`
- `scripts/verify_adtc_reference_run.py`
- `.github/workflows/hardware-contract.yml`
- `tests/hardware/`
