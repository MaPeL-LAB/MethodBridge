from __future__ import annotations

from pathlib import Path


def test_profiler_container_installs_python_native_build_tool(repo_root: Path):
    dockerfile = (repo_root / "infra/container/Dockerfile").read_text(encoding="utf-8")

    apt_install = dockerfile.index("apt-get install")
    profiler_install = dockerfile.index("pip3 install --no-cache-dir .")
    converter_install = dockerfile.index("requirements-convert_hf_to_gguf.txt")

    assert apt_install < dockerfile.index("ninja-build") < profiler_install
    assert profiler_install < converter_install


def test_candidate_source_storage_is_git_ignored(repo_root: Path):
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "model/candidates/" in gitignore
