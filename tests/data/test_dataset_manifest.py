from methodbridge.data.validator import validate_dataset

def test_dataset_manifest(repo_root):
    assert validate_dataset(repo_root) == []
