from pathlib import Path
from methodbridge.data import load_json, load_yaml


def validate_source_registry(root: Path) -> list[str]:
    doc = load_yaml(root / "data/source_registry.yml")
    errors = []
    if len(doc.get("sources", [])) < 16:
        errors.append("source_count_below_16")
    return errors


def validate_dataset(root: Path) -> list[str]:
    manifest = load_json(root / "data/dataset_manifest.json")
    errors = []
    if len(manifest.get("records", [])) != 4:
        errors.append("fixture_count_not_4")
    return errors
