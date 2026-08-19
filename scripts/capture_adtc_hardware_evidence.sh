#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/artifacts/adtc-reference/hardware}"
mkdir -p "$OUT"

python "$ROOT/scripts/check_adtc_host.py" \
  --output "$OUT/hardware_attestation.json"

{
  printf 'captured_at_utc='
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  uname -a
} >"$OUT/uname.txt"

if command -v lscpu >/dev/null 2>&1; then
  lscpu >"$OUT/lscpu.txt"
fi
if command -v free >/dev/null 2>&1; then
  free -b >"$OUT/memory.txt"
fi
if command -v lsblk >/dev/null 2>&1; then
  lsblk -b -o NAME,TYPE,SIZE,ROTA,MODEL >"$OUT/storage.txt"
fi
if command -v lspci >/dev/null 2>&1; then
  lspci >"$OUT/pci.txt"
fi
if command -v swapon >/dev/null 2>&1; then
  swapon --show --bytes >"$OUT/swap.txt" || true
fi
if command -v sensors >/dev/null 2>&1; then
  sensors >"$OUT/sensors.txt" || true
fi

echo "Hardware evidence written to: $OUT"
