#!/usr/bin/env bash
# Build the local ADTC profiler simulation container image
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${ADTC_PROFILER_IMAGE:-methodbridge-adtc-profiler:local}"
DOCKERFILE="$ROOT/infra/container/Dockerfile"

command -v docker >/dev/null 2>&1 || {
  echo "Error: docker is not installed or not in PATH." >&2
  exit 2
}

if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Please start Docker Desktop and retry." >&2
  exit 3
fi

echo "Building simulation container: $IMAGE_NAME (platform linux/amd64)..."
docker build \
  --platform linux/amd64 \
  -t "$IMAGE_NAME" \
  -f "$DOCKERFILE" \
  "$ROOT/infra/container"

echo "Successfully built $IMAGE_NAME"
echo "You can now run: bash scripts/run_adtc_simulated_profile.sh"
