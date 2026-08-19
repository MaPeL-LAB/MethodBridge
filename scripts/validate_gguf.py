#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from methodbridge.conversion.gguf import validate_gguf_header
parser=argparse.ArgumentParser()
parser.add_argument("path")
args=parser.parse_args()
ok=validate_gguf_header(Path(args.path))
print(json.dumps({"valid_gguf_header":ok,"path":args.path}, indent=2))
raise SystemExit(0 if ok else 1)
