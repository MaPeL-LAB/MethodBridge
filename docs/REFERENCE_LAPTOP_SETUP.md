# Reference Laptop Setup

**Purpose:** prepare one native ADTC-class laptop for authoritative participant
profiling. This is an operational checklist, not proof that a machine qualifies.

## Required class

- Intel Core i5 10th–12th generation or AMD Ryzen 5 3000–5000;
- x86-64;
- approximately 8 GiB DDR4;
- integrated graphics only;
- at least 256 GB SSD;
- Ubuntu 22.04 LTS.

## Preparation

1. Install or verify Ubuntu 22.04 LTS.
2. Apply ordinary security updates, then freeze the evaluation environment.
3. Install `git`, Python, a C/C++ toolchain, CMake, `lm-sensors`, and the
   challenge-required profiler dependencies.
4. Build the pinned `llama.cpp` commit from `governance/upstream.lock.json`.
5. Install the pinned ADTC profiler commit from the same lock.
6. Confirm `llama-bench` and `adtc-profiler` are on `PATH`.
7. Pre-download the exact candidate GGUF and accuracy resources.
8. Verify model and dependency hashes.
9. Use stable AC power and record the power profile.
10. Close browsers, IDEs, synchronization clients, and unrelated background
    workloads.
11. Disable swap for the strict run.
12. Disable Wi-Fi, Ethernet, VPN, and other inference networking after all
    required artifacts are local.
13. Verify thermal sensors are readable.
14. Capture hardware evidence:

```bash
python scripts/check_adtc_host.py --require-reference
bash scripts/capture_adtc_hardware_evidence.sh
```

## Profiling

```bash
NETWORK_DISABLED_AT_INFERENCE=true \
  bash scripts/run_adtc_reference_profile.sh
```

The wrapper runs one warm-up and three full participant measurements.

## Review

Create a schema-valid reference-run record and validate it:

```bash
python scripts/verify_adtc_reference_run.py \
  artifacts/adtc-reference/reference-run.json
```

A failure is a stopping condition. Do not edit evidence to create a pass.
