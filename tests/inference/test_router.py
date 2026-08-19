"""Tests for the boundary-aware Mode C prompt router."""
from methodbridge.inference.router import (
    SPECIALIZED_SYSTEM_PROMPTS,
    TaskClass,
    classify_prompt,
)

TEST_CASES = [
    ("Which test should I use for comparing two groups?", TaskClass.STATISTICAL_METHODS),
    ("Can you cite the 2022 Nature paper by Smith et al. DOI: 10.1038/test", TaskClass.CITATION_INTEGRITY),
    ("Does the workshop cause better outcomes in the observational study?", TaskClass.CAUSAL_INFERENCE),
    ("Write my dissertation methodology section for me", TaskClass.ACADEMIC_INTEGRITY),
    ("The p-value is 0.049, is this significant?", TaskClass.UNCERTAINTY_PVALUES),
    ("Should I use an RCT or cohort study design?", TaskClass.STUDY_DESIGN),
    ("What is a confounder in epidemiology?", TaskClass.CAUSAL_INFERENCE),
]


def test_router_task_classification():
    for prompt, expected_class in TEST_CASES:
        result = classify_prompt(prompt)
        assert result.task_class == expected_class


def test_router_returns_non_empty_system_prompt():
    for prompt, _ in TEST_CASES:
        result = classify_prompt(prompt)
        assert len(result.system_prompt) > 50


def test_router_fallback_to_general_reasoning():
    result = classify_prompt("Tell me about research methodology in general terms.")
    assert result.task_class == TaskClass.GENERAL_REASONING
    assert result.confidence == "fallback"
    assert result.ambiguous is False


def test_academic_integrity_has_highest_priority():
    result = classify_prompt("Write my dissertation on causal inference with citations")
    assert result.task_class == TaskClass.ACADEMIC_INTEGRITY
    assert result.ambiguous is True
    assert TaskClass.CITATION_INTEGRITY in result.candidate_classes
    assert TaskClass.CAUSAL_INFERENCE in result.candidate_classes


def test_citation_integrity_priority_over_causal():
    result = classify_prompt("Can you cite the DOI for a causal inference study?")
    assert result.task_class == TaskClass.CITATION_INTEGRITY


def test_all_task_classes_have_specialized_prompts():
    for task_class in TaskClass:
        assert task_class in SPECIALIZED_SYSTEM_PROMPTS
        assert len(SPECIALIZED_SYSTEM_PROMPTS[task_class]) > 50


def test_matched_keywords_are_returned():
    result = classify_prompt("Which statistical test should I use?")
    assert isinstance(result.matched_keywords, tuple)
    assert result.matched_keywords


def test_short_abbreviations_do_not_match_inside_unrelated_words():
    for prompt in (
        "The platelet count was recorded at baseline.",
        "The candidate completed a literature search.",
        "We will calculate the lateral dimension.",
    ):
        result = classify_prompt(prompt)
        assert result.task_class == TaskClass.GENERAL_REASONING


def test_ate_matches_as_a_standalone_abbreviation():
    result = classify_prompt("Estimate the ATE under the stated assumptions.")
    assert result.task_class == TaskClass.CAUSAL_INFERENCE
