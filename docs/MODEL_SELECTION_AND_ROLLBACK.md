# Selection and rollback

**Status:** populated bootstrap decision; reverify before final submission.

Reject candidates that fail exact GGUF conversion/load, critical safety, memory, crash, or licensing gates. Preserve untouched and pre-quantization checkpoints.

## Verification

The controlling evidence, implementation artifact, acceptance test, and review trigger must be recorded in `research/RESEARCH_TO_DECISION_MATRIX.md`. No unmeasured result may be promoted to fact.
