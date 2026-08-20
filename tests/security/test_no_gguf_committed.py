import subprocess


def test_no_gguf(repo_root):
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.gguf"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    ).stdout

    assert tracked == b""
