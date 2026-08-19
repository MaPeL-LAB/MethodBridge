# Reference Run Execution Guide (Phase 12)

**Status:** Official Physical Execution Protocol  
**Target Hardware Profile:** `adtc-standard-laptop-2026` (`config/adtc_standard_laptop.yml`)  
**Applicability:** Phase 12 (Authoritative Physical Profiling on Native x86-64 Laptop)

---

## 1. Executive Purpose & Governance Boundary

MethodBridge strictly distinguishes between development simulations and official submission-grade evidence:
- **Simulation Hosts (macOS, Docker, Cloud VMs):** Useful for preliminary prompt debugging, GGUF conversion, and pipeline testing, but classified strictly as `simulation_only`.
- **Physical Reference Laptop:** Only native execution on a qualified x86-64 laptop running Ubuntu 22.04 LTS producing `reference_match` hardware classification can generate authoritative evidence for the Africa Deep Tech Challenge (ADTC) 2026 scoring.

This guide provides the complete, step-by-step physical execution protocol for running the **1 non-scoreable warm-up** and **3 official measured reference runs** required for Phase 12.

---

## 2. Hardware Qualification Envelope

The target physical machine must conform to `config/adtc_standard_laptop.yml`:

| Subsystem | Specification / Requirement | Verification Command / Check |
|---|---|---|
| **Architecture** | x86-64 (`x86_64` / `amd64`) | `uname -m` |
| **CPU Model** | Intel Core i5 10th–12th Gen OR AMD Ryzen 5 3000–5000 | `lscpu` or `cat /proc/cpuinfo` |
| **System Memory** | 7.5 GiB – 8.5 GiB installed RAM | `free -h` |
| **Graphics** | Integrated GPU only (no discrete GPU) | `lspci \| grep -i vga` |
| **Storage** | >= 256 GB SSD | `lsblk` |
| **Operating System**| Ubuntu 22.04 LTS (x86-64) | `lsb_release -a` |
| **Kernel** | Linux >= 5.15 | `uname -r` |
| **Runtime Engine** | `llama.cpp` (Commit `0329fcdac8c2477c2dda1d5e43fd2e3616b99655`) | `llama-cli --version` |
| **Profiler Engine** | `adtc-profiler` (Commit `ac2e137dca65ea3b09d997774f17dd8907b489fb`) | `adtc-profiler --version` |

---

## 3. Pre-Flight Preparation & Environment Setup

### 3.1 Toolchain and Binary Installation
Ensure all pinned upstream dependencies are compiled and installed:

```bash
# Update and install required build dependencies
sudo apt-get update && sudo apt-get install -y \
  build-essential cmake git python3 python3-pip lm-sensors pciutils lshw

# Verify thermal sensor availability
sudo sensors-detect --auto
sensors

# Build pinned llama.cpp commit (CPU-only, no CUDA / OpenCL / Vulkan offload)
git clone https://github.com/ggml-org/llama.cpp.git /opt/adtc/llama.cpp
cd /opt/adtc/llama.cpp
git checkout 0329fcdac8c2477c2dda1d5e43fd2e3616b99655
cmake -B build -DGGML_NATIVE=OFF -DGGML_CPU=ON
cmake --build build --config Release -j"$(nproc)"
sudo cp build/bin/llama-* /usr/local/bin/

# Install pinned adtc-profiler
pip install git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git@ac2e137dca65ea3b09d997774f17dd8907b489fb
```

### 3.2 Candidate Model Weights Download & Verification
Pre-cache the candidate GGUF (`Qwen/Qwen3-1.7B` at `Q5_K_M`) into `model/methodbridge-local-final.gguf` before isolating the system from the network:

```bash
cd /path/to/MethodBridge

# Download model weights using repository script
./download_model.sh

# Verify GGUF magic header
python3 scripts/validate_gguf.py model/methodbridge-local-final.gguf
```

---

## 4. Operating Isolation Protocol

Strict adherence to operating isolation guarantees non-interference and test reproducibility.

### 4.1 Strict Swap Disabling
ADTC rules require that memory measurements reflect true physical RAM without swap buffering:
```bash
# Disable all swap
sudo swapoff -a

# Verify no active swap partitions
swapon --show
# (Output must be empty)
```

### 4.2 Network Isolation
Inference must run with all network interfaces disabled:
```bash
# Disable network manager connectivity
sudo nmcli networking off

# Verify complete network isolation
ping -c 1 -W 1 8.8.8.8 || echo "Network disabled successfully"
```

### 4.3 Background Workload Termination
Close all desktop web browsers, IDEs, background indexing daemons, and sync utilities:
```bash
# Check running services and stop heavy background tasks
sudo systemctl stop snapd.service || true
```

### 4.4 Thermal & Power Stabilization
1. Connect laptop to AC mains power (battery operation is prohibited).
2. Set CPU power governor to `performance` or default standard.
3. Place laptop on a hard, flat surface with unblocked fan vents.
4. Allow system to cool to idle temperature (< 45 °C) before triggering profiling.

---

## 5. Official Profiling Execution Protocol

### 5.1 Hardware Attestation Capture
Verify host qualification and capture forensic hardware snapshots:

```bash
mkdir -p artifacts/adtc-reference

# Validate host against adtc-standard-laptop-2026 profile
python3 scripts/check_adtc_host.py \
  --require-reference \
  --output artifacts/adtc-reference/hardware_attestation.json

# Capture low-level hardware evidence (lshw, lscpu, lspci, dmidecode, memory)
bash scripts/capture_adtc_hardware_evidence.sh artifacts/adtc-reference/hardware
```

### 5.2 Executing the Reference Profiling Suite
Execute the 1 warm-up and 3 official participant runs using the verified execution harness:

```bash
NETWORK_DISABLED_AT_INFERENCE=true \
  bash scripts/run_adtc_reference_profile.sh
```

#### Run Breakdown:
1. **Warm-Up Run (`warmup.json`):**
   - Single non-scoreable invocation executed with `--skip-accuracy`.
   - Primes OS file cache, initializes memory mappings, and validates binary execution paths.
2. **Official Measured Runs (`submission-run-1.json`, `submission-run-2.json`, `submission-run-3.json`):**
   - 3 consecutive, identical participant-mode runs.
   - Evaluates full accuracy benchmark suite (all 60 evaluation cases).
   - Records continuous memory RSS, tokens/sec generation throughput, first-token latency, CPU load, and package temperatures.

---

## 6. Acceptance Criteria & Failure Boundaries

Every measured run must strictly satisfy the following thresholds:

| Metric | Target / Requirement | Hard Blocker Boundary |
|---|---|---|
| **Host Classification** | `reference_match` | Any classification other than `reference_match` |
| **Completion Status** | `completed: true` | Any crash, process termination, or unhandled exception |
| **Out-Of-Memory (OOM)** | `oom: false` | Any OOM killer event or allocation failure |
| **Peak RAM (RSS)** | <= 6.0 GiB (Target) | > 7.0 GiB (Official Scored Limit) |
| **Peak Temperature** | <= 80.0 °C (Target) | > 85.0 °C (Official Penalty Boundary) |
| **Thermal Throttling** | `thermal_throttled: false` | Any CPU clock throttling event |
| **GPU Offload** | `gpu_layers: 0` | Any GPU layers allocated or offloaded |
| **Swap Usage** | Disabled (`swap_enabled: false`) | Any swap active during inference |
| **Network State** | Disabled (`network_disabled: true`) | Network active or accessible during inference |
| **Accuracy Stage** | Complete (`accuracy_skipped: false`) | `--skip-accuracy` used on measured run |

---

## 7. Evidence Assembly and Validation

### 7.1 Assemble Reference Record
Aggregate the 3 measured profiler runs and hardware attestation into `artifacts/adtc-reference/reference-run.json` adhering to `schemas/adtc_reference_run.schema.json`.

### 7.2 Run Automated Verification Gate
Validate the compiled evidence record against the official schema and hardware profile:

```bash
python3 scripts/verify_adtc_reference_run.py \
  artifacts/adtc-reference/reference-run.json
```

**Verification Output Contract:**
- `accepted`: `true`
- `eligible_for_submission_score`: `true`
- `blockers`: `[]`

If any blockers are reported, the evidence cannot be submitted. Do not hand-edit or fabricate profiling metrics.

---

## 8. Conservative Reporting Policy

When synthesizing final metrics for `REPORT.md` and the ADTC submission portal:
- **Peak RSS:** Report the **maximum** peak RSS observed across the 3 runs.
- **Peak Temperature:** Report the **maximum** temperature observed across the 3 runs.
- **Throughput:** Report the **median** generation tokens per second.
- **Latency:** Report the **median** time-to-first-token in milliseconds.
- **Digests:** Explicitly cite the exact GGUF SHA-256, `llama.cpp` commit, and `adtc-profiler` commit.
