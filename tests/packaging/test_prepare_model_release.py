import json
from pathlib import Path
import pytest
import subprocess
import sys


def test_prepare_model_release_cli_dry_run(repo_root):
    proc = subprocess.run(
        [sys.executable, str(repo_root / "scripts/prepare_model_release.py"), "--dry-run"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["model_card"]["status"] == "dry_run"
    assert data["download_script_validation"]["valid"] is True


def test_prepare_model_release_generate_card(repo_root, tmp_path):
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.prepare_model_release import generate_model_card

    output_card = tmp_path / "README.md"
    content = generate_model_card(output_card)
    assert "MethodBridge" in content
    assert "Qwen/Qwen3-1.7B" in content
    assert "Q5_K_M" in content
    assert output_card.is_file()
    assert output_card.read_text(encoding="utf-8") == content


def test_download_script_validation(repo_root):
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.prepare_model_release import validate_download_script

    valid, issues = validate_download_script(repo_root / "download_model.sh")
    assert valid is True
    assert issues == []


def test_update_release_metadata_dry_run(repo_root):
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from scripts.prepare_model_release import update_release_metadata

    res = update_release_metadata(
        repo_root,
        model_url="https://huggingface.co/MaPeL-LAB/MethodBridge-Qwen3-1.7B-Q5_K_M-GGUF/resolve/main/methodbridge-local-final.gguf",
        sha256="a" * 64,
        dry_run=True,
    )
    assert res["status"] == "dry_run"
    assert res["sha256"] == "a" * 64
