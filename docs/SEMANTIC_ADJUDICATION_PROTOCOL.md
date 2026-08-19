# Qualified semantic adjudication protocol

The automated keyword-overlap score is a smoke-test proxy. It is not accuracy,
expert judgment, reasoning quality, or retention.

A candidate becomes eligible for comparison only after a qualified reviewer has
assessed the actual digest-bound model responses against the frozen case rubrics.

## Review record

Use `schemas/semantic_review_record.schema.json`. The shareable record contains:

- case ID;
- response SHA-256;
- judgment;
- error categories;
- concise rationale;
- reviewer identity, role, timestamp, and conflict declaration;
- aggregate counts and limitations.

It must not contain private prompts, raw responses, expected-answer text, rubric
text, participant information, credentials, or local paths.

## Allowed judgments

```text
pass
fail
inconclusive
human_review_required
test_error
```

`inconclusive`, `human_review_required`, and `test_error` are never converted to
passes.

## Selection boundary

A completed semantic review may make a local real-model run eligible for
comparison, but it does not select a finalist. Final model and quantization
decisions remain attributable human decisions and require official reference
profiling, licence review, and the full comparison record.
