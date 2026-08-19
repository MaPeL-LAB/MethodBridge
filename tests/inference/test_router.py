"""Tests for the Mode C prompt-level task router."""
import pytest
from methodbridge.inference.router import (
    TaskClass,
    classify_prompt,
    SPECIALIZED_SYSTEM_PROMPTS,
)

# Test that each task class routes correctly
test_cases = [
    ("Which test should I use for comparing two groups?", TaskClass.STATISTICAL_METHODS),
    ("Can you cite the 2022 Nature paper by Smith et al. DOI: 10.1038/test", TaskClass.CITATION_INTEGRITY),
    ("Does the workshop cause better outcomes in the observational study?", TaskClass.CAUSAL_INFERENCE),
    ("Write my dissertation methodology section for me", TaskClass.ACADEMIC_INTEGRITY),
    ("The p-value is 0.049, is this significant?", TaskClass.UNCERTAINTY_PVALUES),
    ("Should I use an RCT or cohort study design?", TaskClass.STUDY_DESIGN),
    ("How do I interpret a confidence interval?", TaskClass.UNCERTAINTY_PVALUES),
    ("What is a confounder in epidemiology?", TaskClass.CAUSAL_INFERENCE),
    ("Complete my exam question on regression", TaskClass.ACADEMIC_INTEGRITY),
    ("What are inclusion criteria for a clinical trial?", TaskClass.STUDY_DESIGN),
]


def test_router_task_classification():
    for prompt, expected_class in test_cases:
        result = classify_prompt(prompt)
        assert result.task_class == expected_class, (
            f"Prompt: {prompt!r}\n"
            f"Expected: {expected_class}\n"
            f"Got: {result.task_class}"
        )


def test_router_returns_non_empty_system_prompt():
    for prompt, _ in test_cases:
        result = classify_prompt(prompt)
        assert result.system_prompt, f"Empty system prompt for: {prompt!r}"
        assert len(result.system_prompt) > 50


def test_router_fallback_to_general_reasoning():
    result = classify_prompt("Tell me about research methodology in general terms.")
    assert result.task_class == TaskClass.GENERAL_REASONING


def test_academic_integrity_has_highest_priority():
    # Should catch academic integrity even if other keywords present
    result = classify_prompt("Write my dissertation on causal inference with citations")
    assert result.task_class == TaskClass.ACADEMIC_INTEGRITY


def test_citation_integrity_priority_over_causal():
    result = classify_prompt("Can you cite the DOI for a causal inference study?")
    assert result.task_class == TaskClass.CITATION_INTEGRITY


def test_all_task_classes_have_specialized_prompts():
    for task_class in TaskClass:
        assert task_class in SPECIALIZED_SYSTEM_PROMPTS, f"Missing prompt for {task_class}"
        assert len(SPECIALIZED_SYSTEM_PROMPTS[task_class]) > 50


def test_matched_keywords_are_returned():
    result = classify_prompt("Which statistical test should I use?")
    assert isinstance(result.matched_keywords, tuple)
    assert len(result.matched_keywords) >= 1
