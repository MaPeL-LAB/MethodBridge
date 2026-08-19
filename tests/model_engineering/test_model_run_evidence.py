import argparse
import importlib.util
from pathlib import Path


def _load(repo_root: Path, name: str, relative: str):
    path = repo_root / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_shareable_run_record_is_real_but_non_promotable(repo_root):
    module = _load(repo_root, "create_model_run_evidence", "scripts/create_model_run_evidence.py")
    h40 = "a" * 40
    h64 = "b" * 64
    args = argparse.Namespace(
        run_id="run-001", campaign_id="methodbridge-model-001-v1",
        source_commit=h40, candidate_id="qwen3_1_7b",
        repository="Qwen/Qwen3-1.7B", revision=h40,
        license_identifier="Apache-2.0", gguf_sha256=h64,
        byte_size=1024, quantization="Q5_K_M", llama_cpp_commit=h40,
        configuration_sha256=h64, freeze_id="methodbridge-public-benchmark-v1.0.0",
        benchmark_sha256=h64, host_attestation_sha256=h64,
        raw_bundle_sha256=h64, response_manifest_sha256=h64,
        mode="contract", measurement_class="simulation_only",
        started_at="2026-08-19T10:00:00+00:00",
        finished_at="2026-08-19T10:01:00+00:00",
    )
    record = module.build_record(args)
    assert not module.validate_record(record, repo_root)
    assert record["model_executed"] is True
    assert record["eligible_for_model_selection"] is False
    assert record["eligible_for_submission_score"] is False
    assert record["outputs"]["raw_text_exported"] is False
    assert record["outputs"]["prompt_text_exported"] is False
    assert record["outputs"]["response_text_exported"] is False


def test_semantic_packet_contains_hashes_not_raw_text(repo_root):
    module = _load(repo_root, "build_semantic_review_packet", "scripts/build_semantic_review_packet.py")
    run = {"run_id": "run-001", "benchmark": {"freeze_id": "methodbridge-public-benchmark-v1.0.0", "aggregate_sha256": "c" * 64}}
    responses = {"responses": [{"case_id": "MB-001", "response_sha256": "d" * 64}, {"case_id": "MB-002", "response_sha256": "e" * 64}]}
    packet = module.build_packet(run, responses, "Reviewer", "Methodologist")
    assert not module.validate_packet(packet, repo_root)
    assert packet["raw_prompt_exported"] is False
    assert packet["raw_response_exported"] is False
    assert packet["aggregate"]["human_review_required"] == 2
    assert all("prompt" not in case for case in packet["cases"])
    assert "response_text" not in str(packet).lower()
