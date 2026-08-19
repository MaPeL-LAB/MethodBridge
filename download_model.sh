#!/usr/bin/env bash
set -euo pipefail

MODEL_URL="${METHODBRIDGE_MODEL_URL:-}"
MODEL_SHA256="${METHODBRIDGE_MODEL_SHA256:-}"
MODEL_PATH="${METHODBRIDGE_MODEL_PATH:-model/methodbridge-local-final.gguf}"

if [[ -z "$MODEL_URL" || -z "$MODEL_SHA256" ]]; then
  echo "NOT SUBMISSION READY: set METHODBRIDGE_MODEL_URL and METHODBRIDGE_MODEL_SHA256" >&2
  exit 2
fi

mkdir -p "$(dirname "$MODEL_PATH")"

if [[ -f "$MODEL_PATH" ]]; then
  current="$(shasum -a 256 "$MODEL_PATH" | awk '{print $1}')"
  if [[ "$current" == "$MODEL_SHA256" ]]; then
    echo "Model already present and verified: $MODEL_PATH"
    exit 0
  fi
  echo "Existing model hash mismatch; refusing silent overwrite" >&2
  exit 3
fi

curl --fail --location --proto '=https' --tlsv1.2 "$MODEL_URL" -o "$MODEL_PATH.tmp"
actual="$(shasum -a 256 "$MODEL_PATH.tmp" | awk '{print $1}')"
if [[ "$actual" != "$MODEL_SHA256" ]]; then
  rm -f "$MODEL_PATH.tmp"
  echo "Downloaded model SHA-256 mismatch" >&2
  exit 4
fi
mv "$MODEL_PATH.tmp" "$MODEL_PATH"
echo "Downloaded and verified: $MODEL_PATH"
