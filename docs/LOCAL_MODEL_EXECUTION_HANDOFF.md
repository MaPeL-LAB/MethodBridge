# Local model-execution handoff

**Repository phase:** development-only local R&D authorized by `EXEC-001`.
**Empirical status:** no real candidate comparison is currently established.
**Contest status:** eligibility unresolved; release and submission unauthorized.

## First local gate

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/verify_local_model_handoff.py
```

The expected result may be:

```text
local_setup_ready: true
authorization_scope: private_product_r_and_d
development_r_and_d_authorized: true
eligibility_gate: unresolved
contest_path_authorized: false
empirical_execution_authorized: true
```

This means development-only acquisition and execution may proceed under
`EXEC-001`; it does not mean the entrant is eligible, registered, released, or
authorized to submit. Do not alter these independent fields merely to make a
contest or release check pass.

## Development-only sequence

1. Re-run the handoff validator and confirm `EXEC-001` development scope.
2. Acquire one exact candidate revision at a time, only when its reviewed
   licence, admission, and public no-credential access still match policy.
3. Preserve the revision's licence, model card, file inventory, and hashes.
4. Convert or acquire a GGUF and compute its exact SHA-256.
5. Run native, MethodBridge contract, and Mode C through the real
   digest-bound `llama.cpp` executor.
6. Retain raw prompts and responses only in ignored local storage.
7. Create a shareable run-evidence record without raw text or local paths.
8. Complete qualified semantic adjudication.
9. Compare candidates only under one unchanged campaign configuration.

## Independent contest and release sequence

Before any contest, public, hosting, release, or submission action: resolve
entrant eligibility separately; complete real evidence and qualified review;
record later accountable finalist, quantization, public-claims, release, rules,
and submission decisions as applicable. `EXEC-001` satisfies none of those gates.

## First empirical wave

```text
qwen25_1_5b_instruct
qwen3_1_7b
smollm3_3b
```

The larger candidates remain conditional. Qwen3-1.7B with Q5_K_M is only a
documentary first-test hypothesis, not a finalist.

## Local outputs

```text
artifacts/model-campaign/raw/
artifacts/model-campaign/shareable/
artifacts/model-campaign/experiment-ledger.jsonl
private_evaluations/reviews/
model/
```

All are local or ignored except deliberately reviewed, sanitized evidence records.

## Stopping conditions

Stop on licence uncertainty, revision or digest mismatch, ambiguous chat template,
load failure, crash, timeout, OOM, unsafe memory or thermal state, evaluation
leakage, unacceptable fabricated-citation behavior, protected-authority failure,
or accidental export of secrets, raw private cases, or machine-specific paths.
