from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from methodbridge.evaluation import evaluate_case_response
from methodbridge.inference.runner import (
    InferenceConfigurationError,
    run_llama_cpp_inference,
    run_simulation_proxy,
)


def test_simulation_proxy_requires_explicit_acknowledgement():
    with pytest.raises(InferenceConfigurationError):
        run_simulation_proxy(
            "Explain confounding.",
            candidate_id="candidate",
            mode="contract",
        )


def test_simulation_proxy_cannot_become_model_or_submission_evidence():
    result = run_simulation_proxy(
        "Explain confounding.",
        candidate_id="candidate",
        mode="contract",
        explicit_acknowledgement=True,
    )
    assert result.executor_kind == "simulation_proxy"
    assert result.evidence_class == "simulation_proxy"
    assert result.measured is False
    assert result.eligible_as_model_output_evidence is False
    assert result.eligible_for_model_selection is False
    assert result.eligible_for_submission_score is False
    assert result.model_sha256 is None
    assert result.time_to_first_token_ms is None
    assert result.total_time_ms is None
    assert result.throughput_tps is None
    assert result.peak_rss_mb is None


def test_real_executor_requires_existing_gguf(tmp_path: Path):
    with pytest.raises(InferenceConfigurationError):
        run_llama_cpp_inference(
            "Prompt",
            candidate_id="candidate",
            mode="native",
            model_path=tmp_path / "missing.gguf",
            expected_model_sha256="0" * 64,
            llama_cpp_commit="1" * 40,
            prompt_template="chatml",
        )


def test_real_executor_rejects_hash_mismatch(tmp_path: Path):
    model = tmp_path / "candidate.gguf"
    model.write_bytes(b"GGUF-test")
    with pytest.raises(InferenceConfigurationError, match="SHA-256 mismatch"):
        run_llama_cpp_inference(
            "Prompt",
            candidate_id="candidate",
            mode="native",
            model_path=model,
            expected_model_sha256="0" * 64,
            llama_cpp_commit="1" * 40,
            prompt_template="chatml",
        )


def test_real_executor_records_digest_bound_model_output(tmp_path: Path):
    model = tmp_path / "candidate.gguf"
    model.write_bytes(b"GGUF-test")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()

    fake_llama = tmp_path / "llama-cli"
    fake_llama.write_text("#!/bin/sh\nprintf 'real model response\\n'\n", encoding="utf-8")
    fake_llama.chmod(0o755)

    result = run_llama_cpp_inference(
        "Prompt",
        candidate_id="candidate",
        mode="native",
        model_path=model,
        expected_model_sha256=digest,
        llama_cpp_commit="1" * 40,
        llama_cli=fake_llama,
        prompt_template="chatml",
    )
    assert result.response == "real model response"
    assert result.executor_kind == "llama_cpp"
    assert result.evidence_class == "local_real_model_output"
    assert result.measured is True
    assert result.eligible_as_model_output_evidence is True
    assert result.eligible_for_model_selection is False
    assert result.eligible_for_submission_score is False
    assert result.model_sha256 == digest
    assert result.total_time_ms is not None
    assert result.throughput_tps is None
    assert result.peak_rss_mb is None


def test_keyword_scorer_is_explicitly_non_authoritative():
    case = {
        "case_id": "TEST-001",
        "family": "methods",
        "expected_key_points": ["identify confounding", "state uncertainty"],
        "prohibited_errors": ["claims causation is proven"],
    }
    result = evaluate_case_response(case, "The answer should identify confounding and uncertainty.")
    assert result["automated_proxy"] == "keyword_overlap_v1"
    assert result["semantic_review_required"] is True
    assert "proxy_pass" in result
    assert "accuracy" not in result
    assert "passed" not in result
