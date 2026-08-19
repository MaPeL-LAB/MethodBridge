import subprocess, sys

def test_benchmark_freeze_validator(repo_root):
    proc=subprocess.run([sys.executable,str(repo_root/"scripts/validate_benchmark_freeze.py")],cwd=repo_root,capture_output=True,text=True)
    assert proc.returncode==0, proc.stdout+proc.stderr

def test_private_holdout_contents_are_not_tracked(repo_root):
    names={p.name for p in (repo_root/"evaluations/private_holdout").iterdir()}
    assert names <= {"README.md", ".gitignore"}
