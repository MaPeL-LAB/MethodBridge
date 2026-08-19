from methodbridge.data.validator import validate_source_registry

def test_source_registry(repo_root):
    assert validate_source_registry(repo_root) == []
