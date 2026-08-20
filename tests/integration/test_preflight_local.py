from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


def _run_preflight(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    bash = shutil.which("bash")
    assert bash is not None
    return subprocess.run(
        [bash, str(root / "scripts/preflight_local.sh"), *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        timeout=30,
    )


def _workspace_snapshot(root: Path) -> dict[str, str]:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    paths = sorted({item.decode("utf-8") for item in tracked + untracked if item})
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in paths
        if (root / relative).is_file()
    }


def _python_cache_snapshot(root: Path) -> dict[str, str]:
    caches = []
    for relative in ("src", "scripts", "tests"):
        caches.extend((root / relative).glob("**/__pycache__/*"))
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(caches)
        if path.is_file()
    }


def _minimal_checkout(root: Path, source_script: Path) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "src/methodbridge").mkdir(parents=True)
    shutil.copy2(source_script, root / "scripts/preflight_local.sh")
    (root / "src/methodbridge/__init__.py").write_text("", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "\n".join(
            (
                "[project]",
                'name = "methodbridge-local"',
                'version = "0.1.0"',
                'requires-python = ">=3.12"',
                'dependencies = ["PyYAML>=6.0.2", "jsonschema>=4.23"]',
                "",
                "[project.optional-dependencies]",
                'dev = ["pytest>=8.3"]',
                "",
            )
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)


def test_preflight_accepts_ready_but_unauthorized_state_without_writes(repo_root: Path):
    before = _workspace_snapshot(repo_root)
    cache_before = _python_cache_snapshot(repo_root)
    result = _run_preflight(repo_root)
    after = _workspace_snapshot(repo_root)
    cache_after = _python_cache_snapshot(repo_root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "local_setup_ready: true" in result.stdout
    assert "empirical_execution_authorized: false" in result.stdout
    assert "No model was downloaded or executed." in result.stdout
    assert "Changes made: none." in result.stdout
    assert str(repo_root) not in result.stdout
    assert str(repo_root) not in result.stderr
    assert before == after
    assert cache_before == cache_after


def test_preflight_fails_closed_when_repository_venv_is_missing(
    repo_root: Path, tmp_path: Path
):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert ".venv/bin/python is missing or not executable" in result.stderr
    assert "python3 -m venv .venv" in result.stderr
    assert "Changes made: none." in result.stderr


def test_preflight_rejects_path_or_option_injection(repo_root: Path):
    result = _run_preflight(repo_root, "--root", "/tmp/untrusted")

    assert result.returncode == 64
    assert "unexpected arguments were supplied" in result.stderr
    assert "No arguments are accepted." in result.stderr


def test_preflight_fails_closed_when_handoff_validator_fails(
    repo_root: Path, tmp_path: Path
):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")
    (tmp_path / ".venv/bin").mkdir(parents=True)
    shutil.copy2(repo_root / ".venv/pyvenv.cfg", tmp_path / ".venv/pyvenv.cfg")
    (tmp_path / ".venv/lib").symlink_to(repo_root / ".venv/lib", target_is_directory=True)
    (tmp_path / ".venv/bin/python").symlink_to(Path(sys.executable))
    (tmp_path / "scripts/verify_local_model_handoff.py").write_text(
        "import json\n"
        'print(json.dumps({"valid": False, "local_setup_ready": False, '
        '"empirical_execution_authorized": False}))\n'
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert "governed handoff validator reported an invalid" in result.stderr
    assert "local_setup_ready: true" not in result.stdout
