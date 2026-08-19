# MethodBridge benchmark review and freeze report

## Decision

**Approved with conditions** for public, pre-tuning model comparison as MethodBridge Benchmark v1.0.0.

- Accountable reviewer: Marothi Peter Letsoalo
- AI-assisted methodological review: GPT-5.6 Pro
- Review timestamp: 2026-08-19T08:16:09+02:00
- Cases reviewed: 60
- Bootstrap-executable structural cases: 40
- Freeze record: `evaluations/BENCHMARK_FREEZE.json`

Every case was checked for a meaningful target, a usable prompt, defensible expected points, material prohibited errors, appropriate family and difficulty, a family-specific review rubric, training exclusion, privacy, and consistency with MethodBridge's approved contribution and human-authority boundaries.

Twelve underspecified cases were rewritten to supply a missing study scenario, numerical values, or a concrete user request. Counts and family coverage did not change.

## Freeze conditions

1. All tracked cases are public and must not be described as secret or private holdouts.
2. No prompt, rubric, expected point, prohibited error, or paraphrase may enter training, preference optimization, prompt tuning, or synthetic curriculum generation.
3. Semantic scoring requires an attributable qualified human reviewer. Automated model judging may assist but may not be the sole authority.
4. A separate local-only challenger set is mandatory before tuning or finalist selection.
5. Any case change invalidates the aggregate hash and requires a new version and review.

The benchmark is an engineering decision instrument, not evidence that MethodBridge improves learning, research quality, or scientific outcomes. Scores must be reported with model revision, prompt contract, runtime configuration, quantization, reviewer, and uncertainty.
