#!/usr/bin/env python3
from pathlib import Path
import json
from methodbridge.data.validator import validate_source_registry
ROOT = Path(__file__).resolve().parents[1]
errors = validate_source_registry(ROOT)
print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
raise SystemExit(0 if not errors else 1)
