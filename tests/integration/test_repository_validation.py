from pathlib import Path
import subprocess
import sys


def _run_validator(repo_root: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(repo_root / "scripts/validate_repository.py")],
        cwd=repo_root,
    )


def test_repository_validator(repo_root):
    proc = _run_validator(repo_root)
    assert proc.returncode == 0


def test_repository_validator_allows_ignored_local_gguf(repo_root):
    candidate_dir = repo_root / "model/candidates/validator-test-only"
    candidate_dir.mkdir(parents=True, exist_ok=False)
    gguf = candidate_dir / "ignored-local.gguf"
    try:
        gguf.write_bytes(b"GGUF\x03\x00\x00\x00")
        proc = _run_validator(repo_root)
        assert proc.returncode == 0
    finally:
        gguf.unlink(missing_ok=True)
        candidate_dir.rmdir()
