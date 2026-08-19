# Codex implementation contract

Work only on the next incomplete phase in `BUILD_CHECKLIST.md`.

Before editing, report:

1. objective;
2. files to change;
3. tests and acceptance criteria;
4. protected decisions affected;
5. rollback plan.

Preserve credential-free dry-run and smoke modes. Never describe a simulation,
canned response, fake executor, documentary estimate, or automated keyword proxy
as empirical model evidence. A simulation path must require an explicit flag and
must remain `measured: false`, ineligible for candidate selection, and ineligible
for submission scoring.

The local empirical campaign is governed by
`config/local_model_campaign.yml`. Do not download a model or begin empirical
execution while its authorization fields remain false. Do not alter those fields
without an attributable human decision and eligibility evidence.

Real model evidence requires an exact GGUF SHA-256, immutable source revision,
pinned `llama.cpp` commit, complete runtime configuration, retained raw output,
and a sanitized shareable run record. Model selection additionally requires
qualified semantic adjudication under
`schemas/semantic_review_record.schema.json`. Official performance, memory, TTFT,
and thermal claims require the official ADTC profiler on a qualifying reference
host.

Do not train or download large models unless the phase explicitly authorizes it.
Never include held-out cases in training. Never invent benchmarks, licences,
hashes, measurements, approvals, successful tool execution, model URLs, or
release evidence. Keep model weights, raw outputs, private challenger materials,
credentials, and machine-specific paths ignored.

Do not select a final model, quantization, public prompts, release, or submission
without an attributable human decision. `scripts/prepare_model_release.py` must
remain blocked until `config/model_selection_state.yml` and
`config/release_authorization.yml` satisfy every evidence and authority gate.

Run `make gate` and `make prelocal` before handing work back. Update
`BOOTSTRAP_STATUS.md`, evidence state, ADRs, decision logs, `REPORT.md`,
`MODEL_CARD.md`, public submission drafts, metadata, and `CHANGELOG.md` whenever
implementation or evidence status changes.
