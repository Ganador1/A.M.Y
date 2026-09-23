> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="ejemplo-dvc-end-to-end-sin-dvc-obligatorio"></a>
# DVC End-to-End Example (DVC not required)

This example shows how to version a small dataset with `DataVersioningService` and generate a provenance report without requiring `dvc` to be installed (if present, it will use it; if not, it continues without blocking).

<a id="qué-hace"></a>
## What it does
- Creates a small CSV in `data/`.
- Calls `version_data` to record checksum, size, metadata, and tags in `data/versions.json`.
- Generates a provenance report for that `data_path` and saves it in `data/provenance_report.json`.

<a id="ejecutar"></a>
## Run
1) Activate virtual environment and run the script:

```
source .venv/bin/activate
python examples/dvc_versioning_e2e.py
```

Expected output (summary):
- Message `OK DVC E2E`.
- JSON with versioning information and `provenance_report`.
- File `data/provenance_report.json` created.

<a id="variables-útiles"></a>
## Useful variables
- `STRICT_DATA_PATHS=1` to force the data to be under `ALLOWED_DATA_ROOT` (by default `./data`).
- `ALLOWED_DATA_ROOT=./data` to define the allowed root.
- `MAX_VERSION_FILE_BYTES=524288000` (500MB) size limit per file.

<a id="notas"></a>
## Notes
- If `dvc` is not in the PATH, you will see warnings and DVC tracking will be skipped, but internal versioning will still work.
- Histories are stored in `data/versions.json`.
