import subprocess
import sys


def test_markdown_links_are_valid(repo_root):
    proc = subprocess.run(
        [sys.executable, "scripts/validate_markdown_links.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_transport_artifacts_are_absent(repo_root):
    forbidden = [
        repo_root / ".bootstrap",
        repo_root / ".bootstrap-init",
        repo_root / ".github/workflows/publish-bootstrap.yml",
        repo_root / ".github/workflows/bootstrap-repository.yml",
    ]
    assert not [path for path in forbidden if path.exists()]
