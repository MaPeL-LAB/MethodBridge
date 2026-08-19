import subprocess, sys

def test_upstream_and_candidate_validator(repo_root):
    proc=subprocess.run([sys.executable, str(repo_root/'scripts/validate_upstream_and_candidates.py')], cwd=repo_root, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
