# Public weight hosting

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Credentialed model hub
- Commit weights to Git
- The selected bounded option

## Decision

Use stable credential-free HTTPS hosting with hash verification.

## Consequences

Meets evaluator access and reproducibility needs.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
