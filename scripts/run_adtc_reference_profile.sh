#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ARTIFACT_DIR:-$ROOT/artifacts/adtc-reference}"
SUBMISSION_DIR="${SUBMISSION_DIR:-$ROOT}"
NETWORK_DISABLED_AT_INFERENCE="${NETWORK_DISABLED_AT_INFERENCE:-false}"

command -v adtc-profiler >/dev/null 2>&1 || {
  echo "adtc-profiler is required on PATH" >&2
  exit 2
}
command -v llama-bench >/dev/null 2>&1 || {
  echo "llama-bench is required on PATH" >&2
  exit 2
}

python "$ROOT/scripts/check_adtc_host.py" \
  --require-reference \
  --output "$OUT/hardware_attestation.json"

if [[ "$NETWORK_DISABLED_AT_INFERENCE" != "true" ]]; then
  echo "Set NETWORK_DISABLED_AT_INFERENCE=true only after disabling and verifying network access." >&2
  exit 2
fi

if command -v swapon >/dev/null 2>&1 && [[ -n "$(swapon --noheadings --show 2>/dev/null)" ]]; then
  echo "Strict reference runs require swap to be disabled." >&2
  exit 2
fi

mkdir -p "$OUT"
bash "$ROOT/scripts/capture_adtc_hardware_evidence.sh" "$OUT/hardware"

echo "Running one non-scoreable warm-up..."
adtc-profiler run \
  --submission "$SUBMISSION_DIR" \
  --mode participant \
  --skip-accuracy \
  --output "$OUT/warmup.json"

for run in 1 2 3; do
  echo "Running full participant measurement $run of 3..."
  adtc-profiler run \
    --submission "$SUBMISSION_DIR" \
    --mode participant \
    --output "$OUT/submission-run-$run.json"
done

cat >"$OUT/README.txt" <<'TEXT'
The three raw profiler reports are evidence inputs, not a final accepted record.
Assemble a schema-valid adtc_reference_run record containing the exact model,
llama.cpp and profiler digests, then run:

  python scripts/verify_adtc_reference_run.py /path/to/reference-run.json

Do not promote this evidence if any run used swap, GPU offload, network access,
--skip-accuracy, a different model digest, a different toolchain commit, or
reported OOM, crash, thermal throttling, temperature above 85 C, or peak RSS
above 7 GiB.
TEXT

echo "Raw reference evidence written to: $OUT"
