from pathlib import Path

GGUF_MAGIC = b"GGUF"

def validate_gguf_header(path: Path) -> bool:
    if not path.is_file():
        return False
    with path.open("rb") as handle:
        return handle.read(4) == GGUF_MAGIC
