import subprocess, sys

def test_evaluation_dry_run(repo_root):
    proc=subprocess.run([sys.executable, str(repo_root/"scripts/run_evaluation.py"), "--dry-run"], cwd=repo_root)
    assert proc.returncode == 0
