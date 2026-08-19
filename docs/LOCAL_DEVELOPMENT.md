# Local development

**Status:** remote contract complete; empirical model work remains local.

The GitHub repository is the authoritative source for code, documentation,
governance, schemas, synthetic fixtures, tests, and CI. Secrets, model weights,
private held-out cases, machine-specific configuration, and runtime outputs stay
outside Git.

## First checkout

```bash
git clone https://github.com/MaPeL-LAB/MethodBridge.git
cd MethodBridge

git switch main
git pull --ff-only origin main

python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e '.[dev]'

cp -n \
  CODEX_IMPLEMENTATION_PROMPT.local.md.example \
  CODEX_IMPLEMENTATION_PROMPT.local.md
```

Use `./.venv/bin/python` explicitly in automation so Conda, Homebrew, or a
system Python cannot silently select the wrong interpreter.

## Credential-free gate

```bash
./.venv/bin/python scripts/validate_repository.py
./.venv/bin/python scripts/validate_sources.py
./.venv/bin/python scripts/validate_dataset.py
./.venv/bin/python scripts/detect_train_eval_leakage.py
./.venv/bin/python scripts/validate_markdown_links.py
./.venv/bin/python scripts/run_evaluation.py --dry-run
./.venv/bin/python -m pytest -q
./.venv/bin/python scripts/verify_submission_readiness.py
```

The final command is expected to exit with code `2` while the repository is
truthfully blocked by eligibility, model, download, or profiler gates.

## Files that must remain local

- `.env` and credentials;
- `.venv/`, caches, IDE state, and local overrides;
- GGUF weights, base-model caches, adapters, checkpoints, and training outputs;
- runtime logs, profiler output, thermal traces, and unreviewed screenshots;
- private evaluation cases and confidential or participant-level materials.

## Branch policy

After the initial bootstrap, do not develop on `main`. Use one bounded feature
branch per `BUILD_CHECKLIST.md` phase, update evidence and status records, run
the full credential-free gate, and merge only after review and CI.

See `docs/REMOTE_TO_LOCAL_HANDOFF.md` for the ordered implementation sequence.
