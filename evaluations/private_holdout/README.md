# Local-only challenger and hidden-prompt set

The 60 tracked MethodBridge cases are a **public governed benchmark**. They are useful for reproducible comparison but cannot function as a secret holdout once published.

Before candidate selection or tuning, an accountable reviewer must create a separate local-only challenger set that:

- is stored outside Git and outside every model-training or prompt-optimization path;
- contains no copied or lightly paraphrased public benchmark prompts;
- covers general scientific reasoning beyond biomedical examples;
- includes adversarial uncertainty, citation, privacy, academic-integrity, and mission-boundary cases;
- is versioned and hashed in a restricted evidence record without exposing its contents;
- is never shown to a candidate during training, preference optimization, prompt iteration, or synthetic-data generation;
- is reviewed by a qualified human and used only after the public benchmark configuration is frozen.

Only aggregate, sanitized results may be committed. Official ADTC hidden prompts remain outside project control.
