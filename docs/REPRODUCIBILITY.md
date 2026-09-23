# Reproducing AMY experiments and tests

The curated full source archive is the reproducibility entry point. It contains the AMY runtime, Atlas source, the two calibration harnesses, English manuals and numerical evidence. The Python wheel is a runtime component, not the complete laboratory. The archives exclude Git history, credentials, local state and raw private conversations. A repository clone retains the existing Git history; cleaning the current tree does not rewrite earlier commits.

## 1. Exact autocorrelation witness

```bash
python3 release_evidence/autocorrelation/verify.py
```

Python 3.10+ standard library only. This recomputes the exact lower bound and rejects two altered certificates. It does not rerun the historical optimizer or establish worldwide priority.

## 2. Recorded numerical calibration

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r release_evidence/runtime/requirements.txt
python release_evidence/runtime/verify.py
```

The expected result is 23 AR1 replays, 28 H₂ certificate checks and one retained invalid request. H₂ uses retained integrals; no PySCF or cloud key is needed for this replay. The AR1 floating-point tolerance is 1e-12; NumPy is pinned to the audited environment. A mismatch must be investigated, not silently accepted as success.

## 3. Fresh native model calibration

Requires Python 3.13+ and the scientific dependencies for generating new calculations:

```bash
python -m pip install -e '.[test]'
python -m pip install -r release_evidence/runtime/requirements.txt pyscf
cp .env.example .env
# Put your own Ollama Cloud key in .env. Never distribute it.
python experiments/multimodel_recovery_20260919/campaign.py prepare --output-root /tmp/amy-fresh-calibration --workers worker-01,worker-02
python experiments/multimodel_recovery_20260919/campaign.py run --output-root /tmp/amy-fresh-calibration
```

Use a new output directory each time. Omitting `--workers` prepares ten workers. The frozen catalog records historical availability; confirm that your provider still offers the requested models. These calls consume your own quota. The native configuration bounds cycles, calls and runtime. Do not expect new provider responses to reproduce old text or closure outcomes bit-for-bit.

The installed Atlas tool worker has additional optional scientific dependencies; see ENVIRONMENT.md. These two calibration laboratories use their declared Python modules directly inside the native AMY loop. The retained H₂ numerical audit does not depend on all Atlas services being installed.

## 4. What is not reproduced by the public package

The private raw conversation archive, original native hash-chain roots, provider identity and full search chronology are not certified by the public numerical derivative. Original files were kept unchanged, and public derivatives have separate manifests. Historical aggregate closure counts describe the retained audit; the public numerical replay does not independently derive those counts from complete model transcripts.

Maintainer attribution: **Ganador1**. Other researchers' citations and third-party license credits remain attributed to their original authors.

## 5. Focused release regression tests

The curated snapshot includes the focused release and calibration tests, not the entire private research test collection. Run `python -m pytest -q tests` after installing the test and scientific dependencies above. Original raw run logs are deliberately excluded.

For the extended public regression suite, install `python -m pip install -r scripts/release/requirements-validation.txt`. This pins the direct validation dependencies used locally, including the optional HTTP stack. The real HTTP test checks headers, host filtering, request-size limits and CORS without a model call. It does not validate every optional Atlas service.

## Generated experiment code

The public profile requires Docker isolation for generated code and refuses to fall back to a host subprocess. Build the image with `docker build -t amy-sandbox:latest sandbox` and start Docker before enabling generated-code experiments. Retained numerical verifiers and the trusted AR1/H2 calibration tools do not require Docker. The local operator profile is not the public release default.
