# Migrating from 1.0 to 1.1

1. Back up local memory and evidence before switching code. Retain the source version used for older runs; current code hashes are not expected to match historical snapshots.
2. Start new missions from `config.release.yaml`. The working operator `config.yaml` retains its previous model, continuous-run policy and hardware settings. Its mission text is now English; an explicit namespace preserves the existing mission-memory location. Change that namespace for a different mission.
3. Decision responses must contain an allowed action and nonempty content. Incomplete, malformed or ambiguous responses are rejected rather than silently converted into successful empty actions.
4. Native session closure requires known receipt IDs. Laboratory quantitative assessments are an additional contract, not a universal verifier for arbitrary prose.
5. Fresh per-run provenance and inherited receipt checking do not repair damaged legacy journals. Preserve and report historical failures.
6. The AMY wheel excludes Atlas. With a wheel installation, point `AMY_ATLAS_ROOT` at a separate Atlas source directory and `AMY_ATLAS_PYTHON` at its Python interpreter. Source checkouts use `atlas/.venv_new` by default.
7. Provider aliases may change. Record the actual request/response identity and check availability before running; ten configured slots do not guarantee provider throughput or sufficient local CPU/RAM.

Do not translate raw historical evidence in place. Publish a translated note with its own hash and a link to the original.

When there is no config.yaml in the working directory, an installed runtime prefers its packaged config.release.yaml, falling back to the legacy packaged config.yaml only if the portable profile is absent. An explicit --config path still takes precedence.
