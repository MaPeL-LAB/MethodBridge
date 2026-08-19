# Local retrieval

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Vector database in MVP
- Cloud retrieval
- The selected bounded option

## Decision

Defer retrieval from the submission-critical path.

## Consequences

Reduces memory, latency, injection, and evaluator-path risk.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
