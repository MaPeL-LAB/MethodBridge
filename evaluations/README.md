# Evaluation suite

Sixty held-out specifications cover scientific reasoning, research methods, statistics, pedagogy, safety, African context, and general retention. The first forty contain bootstrap-executable structural assertions. None may enter training.

## Benchmark v1.0.0 freeze

The 60 tracked cases are a **public governed benchmark**, frozen in `BENCHMARK_FREEZE.json` and excluded from every training or prompt-optimization path. They are not a secret holdout. Before tuning or finalist selection, use a separate local-only challenger set following `private_holdout/README.md`.

```bash
python scripts/validate_benchmark_freeze.py
```
