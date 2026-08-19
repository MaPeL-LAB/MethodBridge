# Submission readiness

**Status:** blocked development draft; reverify all official requirements before final submission.

The candidate remains blocked until:

- entrant eligibility and Participation Agreement review are resolved;
- an exact final model and quantization are selected by an accountable human;
- the final GGUF is bound to its source revision and SHA-256;
- qualified semantic review is complete;
- official participant-mode profiler evidence exists on a qualifying reference laptop;
- the public model URL and idempotent verified download work from a clean clone;
- `metadata.json`, the report, model card, prompts, architecture, and video describe the exact artifact;
- all public claims are supported by source or measured evidence;
- release and submission authorization are recorded.

## Evidence checks

```text
[ ] simulation proxies are excluded from empirical claims
[ ] automated keyword-proxy rates are not labelled accuracy
[ ] real model outputs have exact GGUF and llama.cpp provenance
[ ] private challenger prompts and responses remain local
[ ] quantization comparison uses the same exact source model
[ ] official score fields come only from the official profiler
[ ] no unresolved field has been silently converted into a pass
```

The controlling evidence, implementation artifact, acceptance test, and review trigger must be recorded in `research/RESEARCH_TO_DECISION_MATRIX.md`. No unmeasured result, documentary estimate, canned output, or automated proxy may be promoted to fact.
