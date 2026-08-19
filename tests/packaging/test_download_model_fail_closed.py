import subprocess

def test_download_script_fails_closed(repo_root):
    proc=subprocess.run([str(repo_root/"download_model.sh")], cwd=repo_root, capture_output=True, text=True)
    assert proc.returncode == 2
    assert "NOT SUBMISSION READY" in proc.stderr
