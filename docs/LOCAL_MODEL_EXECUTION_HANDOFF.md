# Local model-execution handoff

**Repository phase:** credential-free and weight-free preparation complete.  
**Empirical status:** no real candidate comparison is currently established.

## First local gate

Run:

```bash
python scripts/verify_local_model_handoff.py
```

The expected result may be:

```text
local_setup_ready: true
empirical_execution_authorized: false
```

That is correct while eligibility or attributable execution authorization remains
unresolved. Do not edit the validator or campaign file merely to make the second
field pass.

## Authorization sequence

1. Resolve the entrant and eligibility gate.
2. Record an attributable execution decision in
   `config/local_model_campaign.yml`.
3. Re-run the handoff validator.
4. Acquire one exact candidate revision at a time.
5. Preserve the revision's licence, model card, file inventory, and hashes.
6. Convert or acquire a GGUF and compute its exact SHA-256.
7. Run native, MethodBridge contract, and Mode C through the real
   digest-bound `llama.cpp` executor.
8. Retain raw prompts and responses only in ignored local storage.
9. Create a shareable run-evidence record without raw text or local paths.
10. Complete qualified semantic adjudication.
11. Compare candidates only under one unchanged campaign configuration.

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
