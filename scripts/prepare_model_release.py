#!/usr/bin/env python3
"""Fail-closed MethodBridge model release preparation.

This tool never chooses a model. It can update release metadata only when the
model-selection state, release authorization, exact GGUF, and required evidence
references all agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_gate(root: Path = ROOT) -> tuple[dict, dict, list[str]]:
    release = yaml.safe_load((root / "config/release_authorization.yml").read_text(encoding="utf-8"))
    state = yaml.safe_load((root / "config/model_selection_state.yml").read_text(encoding="utf-8"))
    schema = json.loads((root / "schemas/release_authorization.schema.json").read_text(encoding="utf-8"))
    errors = [f"{error.json_path}:{error.message}" for error in Draft202012Validator(schema).iter_errors(release)]
    if state.get("status") != release.get("candidate_status_required"):
        errors.append("model selection is not a human-approved finalist")
    final = state.get("final_selection", {})
    artifact = release.get("final_artifact", {})
    human = release.get("human_authorization", {})
    if release.get("status") != "human_approved_release":
        errors.append("release authorization remains blocked")
    if human.get("status") != "recorded":
        errors.append("accountable human release authorization is absent")
    for key in ("actor", "timestamp", "decision_reference", "rationale"):
        if not human.get(key):
            errors.append(f"human authorization missing {key}")
    for key, value in release.get("required_evidence", {}).items():
        if not value:
            errors.append(f"required evidence missing: {key}")
    for key in ("candidate_id", "source_model", "source_revision", "quantization", "gguf_sha256"):
        if artifact.get(key) != final.get(key):
            errors.append(f"release artifact disagrees with final selection: {key}")
    return release, state, errors


def render_model_card(release: dict, state: dict) -> str:
    artifact = release["final_artifact"]
    return (
        "---\nlanguage:\n- en\n"
        f"license: {artifact['license_identifier']}\n"
        f"base_model: {artifact['source_model']}\n"
        "tags:\n- gguf\n- llama.cpp\n- scientific-reasoning\n- research-methods\n- offline-ai\n"
        "pipeline_tag: text-generation\n---\n\n# MethodBridge Local\n\n"
        "## Release identity\n\n"
        f"- Candidate: `{artifact['candidate_id']}`\n"
        f"- Source model: `{artifact['source_model']}`\n"
        f"- Source revision: `{artifact['source_revision']}`\n"
        f"- Licence: `{artifact['license_identifier']}`\n"
        f"- Quantization: `{artifact['quantization']}`\n"
        f"- GGUF SHA-256: `{artifact['gguf_sha256']}`\n"
        f"- Byte size: `{artifact['byte_size']}`\n"
        "- Runtime: `llama.cpp`\n\n## Evidence and authority\n\n"
        "This card was generated only after the model selection state reached `human_approved_finalist` and the separate release authorization reached `human_approved_release`. The release remains limited by the evidence references, licence terms, qualified semantic review, official reference profile, and public claims review named in `config/release_authorization.yml`.\n\n"
        "MethodBridge provides educational research-methods support. It does not approve protocols, analysis plans, ethics, legal compliance, clinical care, or institutional decisions.\n"
    )


def prepare_release(root: Path, gguf: Path, public_url: str, write: bool) -> dict:
    release, state, errors = load_gate(root)
    artifact = release.get("final_artifact", {})
    gguf = gguf.expanduser().resolve()
    if not gguf.is_file():
        errors.append("GGUF file does not exist")
    elif gguf.suffix.lower() != ".gguf":
        errors.append("release artifact is not a GGUF")
    else:
        observed = sha256_file(gguf)
        if observed != artifact.get("gguf_sha256"):
            errors.append("GGUF SHA-256 does not match release authorization")
        if gguf.stat().st_size != artifact.get("byte_size"):
            errors.append("GGUF byte size does not match release authorization")
    if not public_url.startswith("https://"):
        errors.append("public model URL must use HTTPS")
    if public_url != artifact.get("public_https_url"):
        errors.append("public URL does not match release authorization")
    if errors:
        return {"ready": False, "errors": errors, "written": False}
    metadata_path = root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["model"] = {
        "name": artifact["source_model"],
        "runtime": "llama.cpp",
        "quantization": artifact["quantization"],
        "parameters_estimate": state["final_selection"].get("parameters_estimate", "reviewed in model card"),
        "packaging": "binary_bundle",
        "url": public_url,
        "sha256": artifact["gguf_sha256"],
    }
    metadata.setdefault("_runtime", {})
    metadata["_runtime"]["model_path"] = "model/methodbridge-local-final.gguf"
    metadata["_runtime"]["model_url"] = public_url
    metadata["_runtime"]["model_sha256"] = artifact["gguf_sha256"]
    card = render_model_card(release, state)
    if write:
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        (root / "model/README.md").write_text(card, encoding="utf-8")
    return {"ready": True, "errors": [], "written": write, "gguf_sha256": artifact["gguf_sha256"], "public_url": public_url}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--model-file", type=Path)
    parser.add_argument("--public-url")
    args = parser.parse_args()
    if args.write and (not args.model_file or not args.public_url):
        parser.error("--write requires --model-file and --public-url")
    if args.check and not args.model_file:
        _, _, errors = load_gate(ROOT)
        print(json.dumps({"ready": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 1
    if not args.model_file or not args.public_url:
        parser.error("provide --check alone, or provide --model-file and --public-url")
    result = prepare_release(ROOT, args.model_file, args.public_url, args.write)
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
