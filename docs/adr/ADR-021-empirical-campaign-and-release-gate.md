# ADR-021: Empirical campaign and release gate

**Status:** accepted for governed local execution preparation; development-
authorization coupling partially superseded by ADR-022.

## Context

Earlier simulation output was promoted into unsupported model and quantization
claims. The repository now needs a single machine-validatable campaign contract
and a separate release authorization gate.

## Decision

Use `config/local_model_campaign.yml` to control candidate order, benchmark
identity, runtime settings, evidence locations, stopping conditions, and execution
authorization. Use shareable run and semantic-review schemas that exclude raw
text and local paths. Use `config/release_authorization.yml` as a distinct,
human-controlled release gate.

## Consequences

- Local model download and empirical execution require an attributable execution
  authorization. ADR-022 permits a development-only authorization while contest
  eligibility remains unresolved; it does not authorize contest participation,
  public claims, release, or submission.
- A local real-model output is evidence, but not automatically selection evidence.
- Official performance claims require the native reference-laptop profiler.
- Release tooling cannot update metadata or public download defaults until a
  human-approved finalist, complete evidence references, exact GGUF digest, and
  accountable release authorization agree.
- Public submission documents remain evidence-gated drafts.
