# Manifest policy

`MANIFEST.json` is the immutable file-by-file inventory of the recovered
`v0.1.0-recovered` bootstrap release. It is intentionally retained as
historical release evidence rather than rewritten on every development commit.

`scripts/build_manifest.py` may be used to generate a fresh candidate manifest
for a later release. A new manifest must be reviewed and committed only when a
release or submission candidate is frozen. CI validates repository structure,
links, data governance, evaluation contracts, and tests on every change; it does
not silently rewrite historical release evidence.
