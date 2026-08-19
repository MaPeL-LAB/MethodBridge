# Public claims policy

**Status:** active fail-closed control.

MethodBridge may publish only claims supported by the evidence class named in the
same artifact. Repository structure, scripts, or simulation output do not prove
model quality, speed, memory use, thermal behavior, or final suitability.

## Evidence classes

| Evidence class | Permitted wording |
|---|---|
| `simulation_proxy` | The plumbing, schemas, prompt contracts, or router were exercised without loading a model. |
| `local_real_model_output` | A digest-bound GGUF produced output through the pinned `llama.cpp` process; qualified semantic review is still required. |
| `official_reference_profile` | The exact GGUF was profiled on a qualifying native reference host through the pinned official profiler. |

## Prohibited wording before evidence exists

Do not publish an empirical winner, final model, selected quantization, tokens per
second, time to first token, peak RAM, thermal result, perplexity delta, reasoning
retention, accuracy, or benchmark score unless an immutable evidence record,
qualified review where required, and the applicable human decision are present.

The following files are public-claim surfaces and are validated:

- `README.md`
- `REPORT.md`
- `MODEL_CARD.md`
- `model/README.md`
- `docs/DEVPOST_SUBMISSION_DRAFT.md`
- `docs/DEMO_VIDEO_STORYBOARD.md`
- `BOOTSTRAP_STATUS.md`

Placeholders must use `REQUIRES_...` or `PENDING_...` wording. A placeholder must
not be illustrated with invented or historical unsupported numbers.
