def test_no_gguf(repo_root):
    assert list(repo_root.rglob("*.gguf")) == []
