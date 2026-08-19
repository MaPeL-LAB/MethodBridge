#!/usr/bin/env python3
"""Convert Hugging Face candidate weights to GGUF format."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.conversion.gguf import validate_gguf_header


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert HF model directory to GGUF")
    parser.add_argument("--dry-run", action="store_true", help="Inspect conversion contract")
    parser.add_argument("--model-dir", type=str, default="model/hf-source", help="Hugging Face model source directory")
    parser.add_argument("--output-gguf", type=str, default="model/model-f16.gguf", help="Output GGUF path")
    parser.add_argument("--outtype", choices=["f16", "bf16", "f32"], default="f16", help="GGUF precision")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "action": "convert candidate to GGUF",
            "mode": "dry-run",
            "model_dir": args.model_dir,
            "output_gguf": args.output_gguf,
            "outtype": args.outtype,
            "pinned_llama_cpp_commit": "0329fcdac8c2477c2dda1d5e43fd2e3616b99655",
            "executed": False,
            "status": "ready_for_conversion",
        }, indent=2))
        return 0

    model_dir = Path(args.model_dir)
    out_gguf = Path(args.output_gguf)
    out_gguf.parent.mkdir(parents=True, exist_ok=True)

    if not model_dir.is_dir():
        print(f"Error: model directory {model_dir} not found.", file=sys.stderr)
        return 2

    # Check for llama.cpp conversion script
    convert_script = Path("/opt/adtc/llama.cpp/convert_hf_to_gguf.py")
    if not convert_script.is_file():
        convert_script = ROOT / "llama.cpp/convert_hf_to_gguf.py"

    if not convert_script.is_file():
        print("Error: llama.cpp conversion script (convert_hf_to_gguf.py) not found.", file=sys.stderr)
        return 3

    cmd = [
        sys.executable,
        str(convert_script),
        str(model_dir),
        "--outfile",
        str(out_gguf),
        "--outtype",
        args.outtype,
    ]
    print(f"Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print("Error: GGUF conversion failed.", file=sys.stderr)
        return proc.returncode

    if not validate_gguf_header(out_gguf):
        print("Error: Converted file failed GGUF header validation.", file=sys.stderr)
        return 4

    print(f"Successfully converted to GGUF: {out_gguf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
