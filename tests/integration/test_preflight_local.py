from __future__ import annotations

import hashlib
import json
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


def _link_current_interpreter(root: Path) -> None:
    (root / ".venv/bin").mkdir(parents=True)
    (root / ".venv/bin/python").symlink_to(Path(sys.executable))
    interpreter_lib = Path(sys.prefix) / "lib"
    assert interpreter_lib.is_dir()
    (root / ".venv/lib").symlink_to(interpreter_lib, target_is_directory=True)
    base_executable = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
    (root / ".venv/pyvenv.cfg").write_text(
        "\n".join(
            (
                f"home = {base_executable.parent}",
                "include-system-site-packages = false",
                f"version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "",
            )
        ),
        encoding="utf-8",
    )


def _write_handoff_validator(root: Path, payload: dict, exit_code: int) -> None:
    (root / "scripts/verify_local_model_handoff.py").write_text(
        f"print({json.dumps(json.dumps(payload))})\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )


def test_preflight_accepts_ready_but_unauthorized_state_without_writes(
    repo_root: Path, tmp_path: Path
):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")
    _link_current_interpreter(tmp_path)
    _write_handoff_validator(
        tmp_path,
        {
            "valid": True,
            "local_setup_ready": True,
            "empirical_execution_authorized": False,
        },
        0,
    )
    checkout_before = _workspace_snapshot(tmp_path)
    checkout_cache_before = _python_cache_snapshot(tmp_path)
    source_before = _workspace_snapshot(repo_root)
    source_cache_before = _python_cache_snapshot(repo_root)

    result = _run_preflight(tmp_path)

    checkout_after = _workspace_snapshot(tmp_path)
    checkout_cache_after = _python_cache_snapshot(tmp_path)
    source_after = _workspace_snapshot(repo_root)
    source_cache_after = _python_cache_snapshot(repo_root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "local_setup_ready: true" in result.stdout
    assert "empirical_execution_authorized: false" in result.stdout
    assert "No model was downloaded or executed." in result.stdout
    assert "Changes made: none." in result.stdout
    assert str(tmp_path) not in result.stdout
    assert str(tmp_path) not in result.stderr
    assert str(repo_root) not in result.stdout
    assert str(repo_root) not in result.stderr
    assert checkout_before == checkout_after
    assert checkout_cache_before == checkout_cache_after
    assert source_before == source_after
    assert source_cache_before == source_cache_after


def test_preflight_fails_closed_when_repository_venv_is_missing(
    repo_root: Path, tmp_path: Path
):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert ".venv/bin/python is missing or not executable" in result.stderr
    assert "python3 -m venv .venv" in result.stderr
    assert "Changes made: none." in result.stderr


def test_preflight_rejects_path_or_option_injection(repo_root: Path, tmp_path: Path):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")

    result = _run_preflight(tmp_path, "--root", "/tmp/untrusted")

    assert result.returncode == 64
    assert "unexpected arguments were supplied" in result.stderr
    assert "No arguments are accepted." in result.stderr


def test_preflight_fails_closed_when_handoff_validator_fails(
    repo_root: Path, tmp_path: Path
):
    _minimal_checkout(tmp_path, repo_root / "scripts/preflight_local.sh")
    _link_current_interpreter(tmp_path)
    _write_handoff_validator(
        tmp_path,
        {
            "valid": False,
            "local_setup_ready": False,
            "empirical_execution_authorized": False,
        },
        1,
    )

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert "governed handoff validator reported an invalid" in result.stderr
    assert "local_setup_ready: true" not in result.stdout
