import json
from pathlib import Path
from typing import Any
import yaml


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(value: str) -> str:
    return " ".join(value.lower().split())
