#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBMISSION_DIR="${SUBMISSION_DIR:-$ROOT}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$ROOT/artifacts/adtc-simulation}"
PROFILER_IMAGE="${ADTC_PROFILER_IMAGE:-methodbridge-adtc-profiler:local}"

command -v docker >/dev/null 2>&1 || {
  echo "docker is required" >&2
  exit 2
}

mkdir -p "$ARTIFACT_DIR"

cat >"$ARTIFACT_DIR/simulation_metadata.json" <<'JSON'
{
  "measurement_class": "simulation_only",
  "eligible_for_submission_score": false,
  "limitation": "linux/amd64 emulation or a constrained container is development evidence only; it cannot establish native x86 throughput or thermal performance."
}
JSON

docker run --rm \
  --platform linux/amd64 \
  --cpus=4 \
  --memory=7.5g \
  --memory-swap=7.5g \
  --network=none \
  --pids-limit=512 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=512m \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  -e METHODBRIDGE_MEASUREMENT_CLASS=simulation_only \
  -v "$SUBMISSION_DIR:/submission:ro" \
  -v "$ARTIFACT_DIR:/artifacts:rw" \
  "$PROFILER_IMAGE" \
  adtc-profiler run \
    --submission /submission \
    --mode participant \
    --output /artifacts/submission-simulation.json

echo "Simulation evidence written to: $ARTIFACT_DIR"
echo "This output is not eligible for final ADTC performance or efficiency claims."
