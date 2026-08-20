from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


def test_real_cli_forwards_validated_prompt_template(repo_root: Path, tmp_path: Path):
    model = tmp_path / "candidate.gguf"
    model.write_bytes(b"GGUF\x03\x00\x00\x00")
    model_sha256 = hashlib.sha256(model.read_bytes()).hexdigest()
    llama_cli = tmp_path / "llama-cli"
    llama_cli.write_text(
        "#!/bin/sh\n"
        "found_threads=false\n"
        "while [ \"$#\" -gt 0 ]; do\n"
        "  if [ \"$1\" = \"--threads\" ] && [ \"${2:-}\" = \"3\" ]; then\n"
        "    found_threads=true\n"
        "    break\n"
        "  fi\n"
        "  shift\n"
        "done\n"
        "[ \"$found_threads\" = true ] || exit 41\n"
        "printf 'bounded test response\\n'\n",
        encoding="utf-8",
    )
    llama_cli.chmod(0o755)

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts/run_local_inference.py"),
            "--model-path",
            str(model),
            "--expected-model-sha256",
            model_sha256,
            "--llama-cli",
            str(llama_cli),
            "--prompt-template",
            "chatml",
            "--threads",
            "3",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["executor_kind"] == "llama_cpp"
    assert payload["prompt_template"] == "chatml"
    assert payload["model_sha256"] == model_sha256
