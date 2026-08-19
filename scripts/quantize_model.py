#!/usr/bin/env python3
"""Quantize high-precision GGUF models into target quantization formats (Q4_K_M, Q5_K_M, Q6_K)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.conversion.gguf import validate_gguf_header


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantize GGUF model")
    parser.add_argument("--dry-run", action="store_true", help="Inspect quantization contract")
    parser.add_argument("--src-gguf", type=str, default="model/model-f16.gguf", help="Source GGUF path")
    parser.add_argument("--dest-gguf", type=str, default="model/model-q5_k_m.gguf", help="Destination GGUF path")
    parser.add_argument("--quant-type", choices=["Q4_K_M", "Q5_K_M", "Q6_K", "q4_k_m", "q5_k_m", "q6_k"], default="Q5_K_M", help="Target quantization format")
    args = parser.parse_args()

    quant_type = args.quant_type.upper()

    if args.dry_run:
        print(json.dumps({
            "action": "quantize GGUF candidate",
            "mode": "dry-run",
            "src_gguf": args.src_gguf,
            "dest_gguf": args.dest_gguf,
            "quant_type": quant_type,
            "pinned_llama_cpp_commit": "0329fcdac8c2477c2dda1d5e43fd2e3616b99655",
            "executed": False,
            "status": "ready_for_quantization",
        }, indent=2))
        return 0

    src_gguf = Path(args.src_gguf)
    dest_gguf = Path(args.dest_gguf)
    dest_gguf.parent.mkdir(parents=True, exist_ok=True)

    if not src_gguf.is_file():
        print(f"Error: Source GGUF {src_gguf} not found.", file=sys.stderr)
        return 2

    quant_bin = shutil.which("llama-quantize") or "/usr/local/bin/llama-quantize"
    if not shutil.which(str(quant_bin)):
        print(f"Error: llama-quantize binary not found on PATH.", file=sys.stderr)
        return 3

    cmd = [
        str(quant_bin),
        str(src_gguf),
        str(dest_gguf),
        quant_type,
    ]
    print(f"Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print("Error: Quantization failed.", file=sys.stderr)
        return proc.returncode

    if not validate_gguf_header(dest_gguf):
        print("Error: Quantized output failed GGUF header validation.", file=sys.stderr)
        return 4

    print(f"Successfully quantized to {quant_type}: {dest_gguf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
