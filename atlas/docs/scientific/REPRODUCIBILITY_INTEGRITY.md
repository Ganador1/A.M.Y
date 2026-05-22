# Artifact Reproducibility and Integrity

This document describes the complete workflow to ensure reproducibility and cryptographic integrity of models and publications in AXIOM META 4.

## Objectives

- Trace every artifact to its code (commit), dataset, parameters, and metrics.
- Validate structure using JSON Schema (gates in CI).
- Guarantee integrity (SHA-256 hash + Ed25519 signatures).
- Facilitate automatic verification (script + CI job) and manual verification (CLI).

## Key Components

| Component | File / Path | Function |
|------------|----------------|---------|
| Manifest Schema | `models/manifest.schema.json` | Defines mandatory fields and constraints (metrics, artifacts, lineage, signatures) |
| Validator | `scripts/validate_manifests.py` | Checks structure and generates JSON report (with hashes) |
| Signer | `scripts/sign_manifest.py` | Deterministically signs manifest (excluding `signatures`) |
| Verification | `scripts/verify_manifest_signatures.py` | Verifies all signatures and generates an error-aggregated report |
| CI Workflow | `.github/workflows/ci.yml` | Executes validation and signature verification |
| Public Keys | `keys/` | Versioned store of PEM public keys |

## Creation and Publication Flow of a Manifest

1. Model training / generation produces an artifact (`.pkl`, etc.).
2. Script/pipeline generates the initial manifest (`*.manifest.json`).
3. Local validation:

   ```bash
   python scripts/validate_manifests.py --models-dir models --schema models/manifest.schema.json --output reports/manifest_validation_report.json
   ```

4. Signing (a timestamp can be added with `--with-timestamp`):

   ```bash
   python scripts/sign_manifest.py --manifest models/<name>.manifest.json \
     --private-key keys/private/ed25519_private.key \
     --public-key-out keys/ed25519_public_default.pem
   ```

5. Verification:

   ```bash
   python scripts/verify_manifest_signatures.py --models-dir models --public-keys-dir keys --output reports/manifest_signature_report.json
   ```

6. Commit the manifest + new public key (if applicable) + optional reports.

## `signatures[]` Structure

```jsonc
"signatures": [
  {
    "alg": "ed25519",          // Allowed algorithm
    "sig": "<Base64>",         // Ed25519 signature of the payload
    "public_key_fingerprint": "<sha256 hex of the DER public key>",
    "ts": "2025-09-17T00:00:00Z" // (Optional) ISO8601 timestamp
  }
]
```

## Signed Payload

The manifest is serialized excluding the `signatures` key, with deterministic key ordering (sort_keys=True) and compact JSON (separators=(",",":")).

## Validation Gate (CI)

- `--fail-on-error`: Fails if there are structural errors or invalid manifests.
- `--fail-on-warn`: Additionally fails if schema or jsonschema is missing.

Enabled in CI when maturity conditions were met (≥3 consecutive valid manifests).

## Signature Gate

Current status: BLOCKING verification in CI using `--fail-on-error`. The pipeline fails if:

- Any manifest lacks signatures.
- there are invalid signatures.
- Public keys are missing for any signature.

The timestamp (`ts`) is now added via `--with-timestamp` for temporal traceability.

## Key Rotation

1. Generate a new pair.
2. Sign all manifests with the new key (the previous one can be kept temporarily: multiple entries in `signatures`).
3. Remove the old signature after 2 consecutive successful pipelines.
4. Document in `CHANGELOG` if it impacts external verifications.

## Security

- Private keys never in the repo (`.gitignore` protects `keys/private/`).
- Review contributions that alter `sign_manifest.py` or `verify_manifest_signatures.py`.
- Consider additional timestamp-type signatures (OpenTimestamps) in Phase 2.

## Isolated Manual Verification

```bash
python scripts/validate_manifests.py --models-dir models --schema models/manifest.schema.json --fail-on-error
python scripts/verify_manifest_signatures.py --models-dir models --public-keys-dir keys --fail-on-error
```

## Integrity Metrics

| Metric | Description | Goal |
|---------|-------------|----------|
| manifests_total | Number of detected manifests | -- |
| manifests_invalid | Structural invalid count | 0 |
| manifests_unsigned | Without signatures | 0 (after gate) |
| signatures_invalid | Invalid signatures | 0 |
| signatures_missing_keys | Signatures without public key | 0 |

## Future (Technical Backlog)

- Merkle Tree for publication batch and inclusion proof.
- Temporal anchoring (OpenTimestamps) of root hash.
- `/api/v1/integrity/status` endpoint with aggregates and Prometheus export.
- Integration with Provenance Graph (detailed lineage) and SPARQL export.

## Periodic Automation (Kubernetes CronJob)

An independent nightly validation runs outside the PR pipeline to detect silent training data drift or non-versioned changes.

Manifest: `kubernetes/cronjob-data-validation.yaml`

Features:
- Schedule: `15 2 * * *` (02:15 UTC)
- Concurrency Policy: `Forbid` to avoid overlaps
- Initial Hardening: `securityContext` (non-privileged, read-only root FS, non-root user)
- Executed Command: `python scripts/run_data_validations.py --fail-on-error`

Goal: Early alerting on data quality failures even if there are no active commits.

## Publication Merkle Tree (Phase 2 - Detail)

Motivation:
A unique root hash allows proving that a specific manifest was included in a signed set without redistributing all files.

Mitigated Threats:
- Selective suppression of manifests after publication (detected when recalculating root).
- Subsequent malicious insertion (already anchored root won't match recomputation).
- Silent alteration of an individual manifest (leaf hash changes and through propagation the root differs).

Algorithm:
1. Deterministically sort `*.manifest.json` files by path.
2. Calculate SHA-256 of raw bytes of each file (leaves).
3. If an odd number of leaves, duplicate the last one (deterministic balance).
4. For each level: concatenate (hex_left + hex_right) as ASCII bytes and SHA-256 → new node.
5. Repeat until a single root.

Generared `merkle_root.json` by `scripts/compute_merkle_root.py` includes:
- `leaf_hashes`: Ordered list of leaf hashes.
- `tree_levels`: Levels for debugging (optional).
- `manifests`: (file, hash) pairs for human inspection.
- `root`: Final root hash.

Manual Verification:
```bash
python scripts/compute_merkle_root.py --models-dir models --output /tmp/new_merkle.json
python scripts/verify_merkle_root.py --models-dir models --file models/merkle_root.json
```
If verification produces `VERIFICATION OK`, the snapshot matches. Differences indicate change or suppression.

Inclusion Proof (simplified manual):
1. Obtain target leaf hash H.
2. Extract from `tree_levels` the necessary siblings at each level.
3. Recalculate upwards following the order (left/right) and compare with `root`.

Root Signing (future):
Planning to sign `merkle_root.json` with `sign_manifest.py` (extension or dedicated script) and anchor the root SHA-256 in an external timestamp service.

Current Limitations:
- No separate minimum proof (path) is generated; it recalculates with full levels.
- No external anchoring yet.

## Sandbox Hardening (Placeholder)

Upcoming controls:
- Execution in isolated containers (gVisor / Firecracker) for inference tests.
- Seccomp/AppArmor policy verification.
- Disable outbound networking in scientific validation tasks.

Initial script: `scripts/check_runtime_sandbox.py` (checks basic env vars and capabilities in the container).

## Scientific Gates (Placeholder)

Goal: Before publishing a new model, require quantitative minimum thresholds and coherence checks.

First checks (`scripts/run_scientific_gates.py` script):
- Presence of required base dataset.
- Minimum size > N rows.
- Existing aggregated metrics file with key fields (e.g., `accuracy`, `f1`).

CI Job will fail if any of these checks fail (exit != 0).

Future metrics:
- Drift between current distribution and baseline (KS-test / PSI)
- Minimum calibration (ECE < threshold)
- Repeatability (variance in replicas within range)

## Reproducible Bundle and Scientific Publication

To facilitate independent distribution and verification of results, AXIOM META 4 generates reproducible bundles containing all necessary artifacts to replicate an experiment.

### Bundle Construction

Script: `scripts/build_repro_bundle.py`

The bundle includes:
- All manifests (`*.manifest.json`) with signatures
- `merkle_root.json` file (if it exists)
- Optionally, model artifacts referenced in manifests (`--include-artifacts` flag)

Determinism Strategies:
- Alphabetically sorted file list
- Fixed tar metadata: `mtime=0`, `uid/gid=0`, owner `root`
- Gzip level 9 compression, GNU format

Output: `dist/atlas-repro_<timestamp>.tar.gz` + `dist/bundle_metadata.json`

### Bundle Verification

Script: `scripts/verify_repro_bundle.py`

Verifies:
1. SHA-256 hash of each listed file vs metadata
2. SHA-256 hash of the complete bundle
3. Reports `BUNDLE OK` or `BUNDLE FAIL` with details of discrepancies

### Publication Pipeline

Automated flow:
1. **Merkle**: `compute_merkle_root.py` → `models/merkle_root.json`
2. **Bundle**: `build_repro_bundle.py` → `dist/`
3. **Publication**: `generate_publication_tex.py` → `publications/output.tex`
4. **Compilation** (optional): `pdflatex output.tex` → `output.pdf`

### LaTeX Template

File: `publications/template.tex`

Automatically replaced placeholders:
- `MERKLE_ROOT_PLACEHOLDER` → Truncated Merkle root hash
- `BUNDLE_HASH_PLACEHOLDER` → SHA-256 hash of the bundle
- `TIMESTAMP_PLACEHOLDER` → Generation date/time
- `GIT_COMMIT_PLACEHOLDER` → Current commit hash

The resulting publication includes:
- Reproducibility statement with verifiable hashes
- Step-by-step verification instructions
- "Data Availability" section with bundle content

### Third-Party Verification

Readers can verify independently:

```bash
# 1. Verify bundle integrity
python scripts/verify_repro_bundle.py --metadata bundle_metadata.json

# 2. Verify manifest signatures
python scripts/verify_manifest_signatures.py --models-dir extracted/models --public-keys-dir keys

# 3. Verify Merkle root
python scripts/verify_merkle_root.py --models-dir extracted/models --file extracted/models/merkle_root.json
```

Expected outputs: `BUNDLE OK`, `All signatures valid`, `VERIFICATION OK`

### CI Integration

`reproducible-bundle` job in workflow:
- Runs after `merkle-verification`
- Builds deterministic bundle
- Automatically verifies integrity
- Uploads artifacts (`*.tar.gz` + metadata) as GitHub Artifacts

Goal: Each commit/PR generates a verifiable bundle for review and archiving.

## Sandbox Hardening (Roadmap)

Planned controls for secure execution:

### Container Isolation
- **gVisor**: Userspace kernel for inference/training syscalls
- **Firecracker**: microVMs for critical or multi-tenant loads
- **seccomp**: Custom syscall filters (deny networking, filesystem writes outside `/tmp`)
- **AppArmor/SELinux**: Restrictive MAC policies

### Runtime Constraints
- Read-only filesystem (except specific directories)
- No outbound network access for validation tasks
- Strict CPU/memory limits with cgroups v2
- Minimum capabilities (drop ALL, add specific according to need)

### Continuous Verification
- Fuzz testing of endpoints that execute code/expressions
- Negative "escape" tests (verify that sandbox contains processes)
- Monitoring of anomalous syscalls during execution

Current script: `scripts/check_runtime_sandbox.py` (placeholder - checks basic environment variables)

Future implementation: active verification of policies, capabilities, namespaces, and effective isolation measures.

---

Keep this document synced with changes in schema, scripts, and CI pipeline.
