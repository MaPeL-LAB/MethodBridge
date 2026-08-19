# Official runtime

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Alternative production runtime
- Defer the decision or make no change
- The selected bounded option

## Decision

Use pinned `llama.cpp` and reject candidates that cannot load through it.

## Consequences

The official evaluator contract controls the judged path.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
