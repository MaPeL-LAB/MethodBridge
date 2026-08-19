import subprocess, sys

def test_repository_validator(repo_root):
    proc=subprocess.run([sys.executable, str(repo_root/"scripts/validate_repository.py")], cwd=repo_root)
    assert proc.returncode == 0
