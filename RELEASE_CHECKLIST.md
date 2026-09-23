# Release checklist — A.M.Y 1.1.0rc1

This candidate has not been published. Check results are recorded in the local release-preparation report; boxes below do not reuse approvals from the 1.0 checklist.

## Prepared

- [x] English primary documentation and publication catalog.
- [x] Runtime, package, lockfile and citation version aligned to 1.1.0rc1.
- [x] Placeholder DOI removed; no unissued identifier or release date asserted.
- [x] Historical experiment records preserved; selected mathematical evidence packaged separately.
- [x] Scientific claims distinguish exact witnesses, numerical checks, reproductions and engineering changes.
- [x] Operator configuration distinguished from a portable release example.

## Validation before promotion

- [x] Run `python scripts/release/check_release.py --dist dist/release-1.1.0rc1` and inspect the report.
- [x] Run the selected offline regression suite and review every failure or skip.
- [x] Run `python release_evidence/autocorrelation/verify.py`, including negative controls.
- [x] Build source and wheel distributions; smoke-test the installed runtime outside the checkout.
- [ ] Review the exact Git source set, including untracked additions and any tracked credential containers.
- [ ] Run CI on the final committed revision. Local results do not imply remote CI passed.

## Publication gates

- [ ] Maintainer approves final files, notes, version and license attribution.
- [ ] Tag the reviewed revision and build final artifacts from it.
- [ ] Verify CI build attestations against the actual distributed files.
- [ ] Create a real repository release/deposit; only then add its DOI and release date.
- [ ] For a scientific paper: external mathematical review, broader prior-art review and curated search-lineage archive.

The wheel contains AMY runtime code; Atlas is a separate source installation. The compact witness package proves its mathematical claim, not complete provenance for every historical run. Legacy source comments and archived documentation remain multilingual; the maintained public entry points are English.

See [the validation record](docs/releases/VALIDATION_1_1_0rc1.md) for scope and results. Re-run package checks after any further file changes.

## Publication privacy boundary

Use the curated public-source export for this candidate. The existing Git history and private working tree are not anonymized. Do not assume a GitHub tag's automatically generated source archive is equivalent to the reviewed export. Maintainer attribution in public derivatives is Ganador1; preserve third-party license credits and research citations.

After building an sdist, run `python scripts/release/normalize_archive_metadata.py <archive.tar.gz>` to remove build-account ownership from tar headers. Scan the final archives with `scripts/release/audit_public_artifacts.py` using a local, unshared identifier list and credential files. Keep original research evidence unchanged; redacted derivatives have their own manifests.
