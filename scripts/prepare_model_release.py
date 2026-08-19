#!/usr/bin/env python3
"""Automate model release preparation, model card generation, and metadata updating for MethodBridge."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MODEL_CARD_TEMPLATE = """---
language:
- en
license: apache-2.0
base_model: Qwen/Qwen3-1.7B
tags:
- gguf
- llama.cpp
- scientific-reasoning
- research-methods
- education
- offline-ai
- adtc-2026
pipeline_tag: text-generation
library_name: gguf
---

# MethodBridge: Offline Scientific Reasoning & Research-Methods Tutor (Qwen3-1.7B Q5_K_M GGUF)

## Summary

**MethodBridge** is an offline, privacy-first scientific reasoning and research-methods assistant engineered for postgraduate students and early-career researchers running on standard consumer laptops. MethodBridge delivers rigorous methodological feedback, causal inference critique, statistical interpretation, and pedagogical scaffolding without requiring internet access or cloud infrastructure.

## Model Details

- **Base Model:** `Qwen/Qwen3-1.7B`
- **Base Revision:** `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`
- **Quantization:** `Q5_K_M` (5-bit medium quantization with optimal perplexity/memory balance)
- **Format:** GGUF (v3)
- **Parameters:** ~1.7 Billion
- **Runtime:** `llama.cpp` (pinned commit: `0329fcdac8c2477c2dda1d5e43fd2e3616b99655`, CPU-only baseline)
- **Context Length:** 32,768 tokens (inference benchmark baseline: 2,048–4,096 tokens)
- **License:** Apache-2.0

## Domain & Intended Use

- **Primary Domain:** Scientific and mathematical reasoning, research methodology, study design critique, causal inference, and statistical interpretation.
- **Cross-Disciplinary Pairing:** Scientific Reasoning + Education (pedagogical scaffolding for postgraduate researchers).
- **Intended Use:**
  - Critiquing observational study designs and identifying confounding / selection bias.
  - Interpreting statistical effect sizes, confidence intervals, and p-values beyond binary significance testing.
  - Guiding students in structuring robust scientific inquiry and pre-registration hypotheses.
  - Offline tutoring in bandwidth-constrained, resource-limited academic environments.

## Hardware Target & Efficiency Contract

Engineered to strictly conform with the **Africa Deep Tech Challenge (ADTC) 2026 Standard Laptop** specification:
- **Architecture:** x86-64 (Intel Core i5 10th–12th Gen or AMD Ryzen 5 3000–5000)
- **System Memory:** ~8 GiB installed RAM
- **Graphics:** Integrated graphics only (0 GPU layers offloaded; CPU-only execution)
- **Storage:** >= 256 GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Memory Envelope:** Peak RSS target <= 6.0 GiB (Strict ceiling: 7.0 GiB)
- **Thermal Envelope:** Operating temperature <= 80 °C (Strict throttling boundary: 85 °C)
- **Network Isolation:** Fully functional with networking disabled during inference.
- **Swap Policy:** Operates safely with zero swap enabled.

## Download and Verification

### Download via Repository Script
```bash
# Set public model environment variables if not already baked in
export METHODBRIDGE_MODEL_URL="https://huggingface.co/MaPeL-LAB/MethodBridge-Qwen3-1.7B-Q5_K_M-GGUF/resolve/main/methodbridge-local-final.gguf"
export METHODBRIDGE_MODEL_SHA256="<SHA256_HEX>"

./download_model.sh
```

### Direct Download & Verification
```bash
mkdir -p model
curl --fail --location --proto '=https' --tlsv1.2 \\
  "$METHODBRIDGE_MODEL_URL" \\
  -o model/methodbridge-local-final.gguf

echo "$METHODBRIDGE_MODEL_SHA256  model/methodbridge-local-final.gguf" | sha256sum -c -
```

## Running Inference with llama.cpp

Execute with pinned `llama.cpp` CPU-only binary:

```bash
llama-cli \\
  -m model/methodbridge-local-final.gguf \\
  -p "<|im_start|>system\\nYou are MethodBridge, an offline scientific reasoning and research-methods tutor.<|im_end|>\\n<|im_start|>user\\nA cohort study reports a risk ratio of 1.40 with a 95% confidence interval of 0.98 to 2.00 and p=0.064. Explain what can and cannot be concluded.<|im_end|>\\n<|im_start|>assistant\\n" \\
  -n 512 \\
  --temp 0.2 \\
  --top-p 0.95 \\
  -c 2048 \\
  --threads 4
```

## Evaluation & Ethical Guardrails

- **Benchmark Evaluation:** Evaluated across 60 structured test cases in research methodology, causal inference, and statistical reporting.
- **Out of Scope:**
  - Clinical trial / patient-specific medical advice or diagnosis.
  - Institutional ethics committee, regulatory, or legal approvals.
  - Fabricating synthetic citations or academic ghost-writing.
  - Generating deceptive academic submissions.
- **Uncertainty & Abstention:** Explicitly abstains and flags methodological invalidity when presented with unadjusted observational confounders or underpowered designs.
"""


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_model_card(output_path: Path | None = None) -> str:
    """Generate standardized Hugging Face Hub model card."""
    content = MODEL_CARD_TEMPLATE.strip() + "\n"
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    return content


def validate_download_script(script_path: Path) -> tuple[bool, list[str]]:
    """Validate download_model.sh integrity and fail-closed structure."""
    issues: list[str] = []
    if not script_path.is_file():
        return False, [f"Missing script: {script_path}"]

    text = script_path.read_text(encoding="utf-8")

    # Check strict bash safety
    if "set -euo pipefail" not in text:
        issues.append("Missing 'set -euo pipefail' bash strict mode")

    # Check fail-closed condition on empty URL/SHA
    if "NOT SUBMISSION READY" not in text or "exit 2" not in text:
        issues.append("Missing fail-closed check for empty MODEL_URL or MODEL_SHA256 (exit code 2)")

    # Check HTTPS security flags
    if "--proto '=https'" not in text or "--tlsv1.2" not in text:
        issues.append("Missing secure curl transport flags (--proto '=https' --tlsv1.2)")

    # Check SHA256 integrity verification
    if "shasum -a 256" not in text and "sha256sum" not in text:
        issues.append("Missing SHA-256 checksum verification")

    # Check atomic rename via tmp file
    if ".tmp" not in text or "mv " not in text:
        issues.append("Missing atomic rename via temporary download file")

    return (len(issues) == 0), issues


def update_release_metadata(
    root: Path,
    model_url: str,
    sha256: str,
    dry_run: bool = False,
) -> dict:
    """Update metadata.json and download_model.sh with public release URL and SHA-256."""
    sha256 = sha256.lower().strip()
    if not re.match(r"^[0-9a-f]{64}$", sha256):
        raise ValueError(f"Invalid SHA-256 hex digest: {sha256}")

    if not model_url.startswith("https://"):
        raise ValueError(f"Model URL must be a secure HTTPS URL: {model_url}")

    metadata_path = root / "metadata.json"
    download_script_path = root / "download_model.sh"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.setdefault("model", {})
    metadata["model"]["url"] = model_url
    metadata["model"]["sha256"] = sha256
    metadata.setdefault("_runtime", {})
    metadata["_runtime"]["model_url"] = model_url
    metadata["_runtime"]["model_sha256"] = sha256

    new_metadata_json = json.dumps(metadata, indent=2) + "\n"

    # Update download_model.sh defaults
    script_text = download_script_path.read_text(encoding="utf-8")
    
    # Replace MODEL_URL line
    script_text = re.sub(
        r'MODEL_URL="\$\{METHODBRIDGE_MODEL_URL:-[^}]*\}"',
        f'MODEL_URL="${{METHODBRIDGE_MODEL_URL:-{model_url}}}"',
        script_text,
    )
    # Replace MODEL_SHA256 line
    script_text = re.sub(
        r'MODEL_SHA256="\$\{METHODBRIDGE_MODEL_SHA256:-[^}]*\}"',
        f'MODEL_SHA256="${{METHODBRIDGE_MODEL_SHA256:-{sha256}}}"',
        script_text,
    )

    release_artifact = {
        "model_name": metadata.get("model", {}).get("name", "Qwen/Qwen3-1.7B"),
        "url": model_url,
        "sha256": sha256,
        "quantization": metadata.get("model", {}).get("quantization", "Q5_K_M"),
    }
    release_artifact_path = root / "artifacts/model_release.json"

    if not dry_run:
        metadata_path.write_text(new_metadata_json, encoding="utf-8")
        download_script_path.write_text(script_text, encoding="utf-8")
        release_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        release_artifact_path.write_text(json.dumps(release_artifact, indent=2) + "\n", encoding="utf-8")

    return {
        "status": "updated" if not dry_run else "dry_run",
        "model_url": model_url,
        "sha256": sha256,
        "updated_files": [
            str(metadata_path.relative_to(root)),
            str(download_script_path.relative_to(root)),
            str(release_artifact_path.relative_to(root)),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare model release, generate model card, and update metadata.")
    parser.add_argument("--generate-card", action="store_true", help="Generate model/README.md Hugging Face model card")
    parser.add_argument("--validate-download", action="store_true", help="Validate download_model.sh script integrity")
    parser.add_argument("--update", action="store_true", help="Update metadata.json and download_model.sh with release info")
    parser.add_argument("--model-url", type=str, help="Public HTTPS URL of GGUF weights")
    parser.add_argument("--sha256", type=str, help="SHA-256 checksum of GGUF weights")
    parser.add_argument("--model-file", type=Path, help="Local GGUF file to verify/calculate SHA-256")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes to disk")
    parser.add_argument("--all", action="store_true", help="Execute all generation and validation steps")

    args = parser.parse_args()

    # Default to --all if no specific action provided
    if not (args.generate_card or args.validate_download or args.update or args.all):
        args.all = True

    results: dict = {}

    # 1. Model Card Generation
    if args.generate_card or args.all:
        card_path = ROOT / "model/README.md"
        if not args.dry_run:
            generate_model_card(card_path)
            results["model_card"] = {"status": "generated", "path": str(card_path.relative_to(ROOT))}
        else:
            results["model_card"] = {"status": "dry_run", "path": str(card_path.relative_to(ROOT))}

    # 2. Validate download_model.sh
    if args.validate_download or args.all:
        script_path = ROOT / "download_model.sh"
        valid, issues = validate_download_script(script_path)
        results["download_script_validation"] = {
            "valid": valid,
            "issues": issues,
            "path": str(script_path.relative_to(ROOT)),
        }
        if not valid:
            print(json.dumps(results, indent=2), file=sys.stderr)
            return 1

    # 3. Update release metadata if requested or arguments provided
    if args.update or (args.all and (args.model_url or args.sha256 or args.model_file)):
        sha256 = args.sha256
        if args.model_file:
            if not args.model_file.is_file():
                print(f"Error: model file not found: {args.model_file}", file=sys.stderr)
                return 2
            calculated_hash = compute_sha256(args.model_file)
            if sha256 and sha256.lower() != calculated_hash:
                print(f"Error: Provided SHA-256 ({sha256}) does not match file ({calculated_hash})", file=sys.stderr)
                return 3
            sha256 = calculated_hash

        if args.model_url and sha256:
            update_res = update_release_metadata(
                ROOT,
                model_url=args.model_url,
                sha256=sha256,
                dry_run=args.dry_run,
            )
            results["release_metadata"] = update_res
        elif args.update:
            print("Error: --update requires --model-url and --sha256 (or --model-file)", file=sys.stderr)
            return 4

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
