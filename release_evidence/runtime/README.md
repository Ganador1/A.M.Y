# Reproducible numerical calibration dataset

This package contains **51 successful measurements (23 AR1, 28 H₂)** and one retained rejected H₂ request from the four September calibration batches. It includes requests, results, H₂ certificates, supplied integrals, audits, negative controls and a checker.

```bash
python -m pip install -r release_evidence/runtime/requirements.txt
python release_evidence/runtime/verify.py
```

NumPy and the Python standard library are sufficient for offline replay. AR1 recomputes the retained trajectories with extracted producer functions and compares values within 1e-12 absolute tolerance. H₂ uses a separate algebraic verifier on supplied integrals and rejects a deliberately altered energy; generating new integrals requires PySCF and is a distinct check.

The public records are privacy-reviewed derivatives, not rewrites of the native hash chains. MEASUREMENT_SOURCES.json links each derivative to the original byte hash. The originals remain unchanged. The manifest checks this public package; it is not an externally signed attestation.

aggregate.json summarizes the original 20 sessions, including six that failed to close. This numerical replay does not independently verify their complete conversations, model decisions or native-chain chronology. Full historical raw-chain replication is outside this compact privacy-preserving package. No novelty, model superiority or full autonomy claim follows from the data.

For a new native calibration, the full source release includes experiments/multimodel_recovery_20260919, experiments/recovery_campaign_20260919, the runtime and scientific modules, and a frozen public model catalog. See docs/REPRODUCIBILITY.md. A new cloud response is not expected to reproduce old model text or outcomes bit-for-bit.
