#!/usr/bin/env python3
"""Release hygiene tests for the public repository surface."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_URL = "https://github.com/Ganador1/A.M.Y"


def _load_secret_hygiene_module():
    module_path = ROOT / "scripts" / "diagnostics" / "verify_secret_hygiene.py"
    spec = importlib.util.spec_from_file_location("verify_secret_hygiene", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _tracked_files() -> list[str]:
    public_manifest = ROOT / "PUBLIC_SOURCE_MANIFEST.json"
    if public_manifest.exists():
        return [row["path"] for row in json.loads(public_manifest.read_text())["files"]]
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [
        line
        for line in proc.stdout.splitlines()
        if line and (ROOT / line).exists()
    ]


def test_public_metadata_points_to_current_repository_and_license():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["urls"] == {
        "Homepage": REPOSITORY_URL,
        "Documentation": f"{REPOSITORY_URL}/blob/main/README.md",
        "Repository": REPOSITORY_URL,
    }

    public_readme = (ROOT / "README_PUBLIC.md").read_text(encoding="utf-8")
    assert f"git clone --branch main {REPOSITORY_URL}.git" in public_readme
    assert "Apache-2.0" in public_readme
    assert "MIT" not in public_readme
    assert "tuusuario" not in public_readme
    assert "Pre-release" not in public_readme
    assert "v0.9.0" not in public_readme
    assert "84+" not in public_readme
    assert "release candidate" in public_readme.lower()
    assert "94 herramientas" not in public_readme


def test_public_readme_does_not_link_missing_repository_docs():
    public_readme = (ROOT / "README_PUBLIC.md").read_text(encoding="utf-8")
    missing = []
    for target in re.findall(r"\]\(([^)]+\.md)\)", public_readme):
        if target.startswith(("http://", "https://")):
            continue
        if not (ROOT / target).exists():
            missing.append(target)
    assert missing == []


def test_public_entrypoints_identify_project_and_getting_started():
    assert (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[0] == "# A.M.Y — Autonomous Mind Yield"
    assert (ROOT / "README_PUBLIC.md").read_text(encoding="utf-8").splitlines()[0] == "# Getting started with A.M.Y"


def test_secret_hygiene_scans_repository_root_and_no_live_kubernetes_secret_is_tracked():
    verifier = _load_secret_hygiene_module()
    assert verifier.ROOT == ROOT

    tracked_manifests = [
        Path(path)
        for path in _tracked_files()
        if path.startswith("atlas/kubernetes/") and path.endswith((".yml", ".yaml"))
    ]
    live_secret_manifests = []
    for rel_path in tracked_manifests:
        if ".example." in rel_path.name:
            continue
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        if re.search(r"(?m)^kind:\s*Secret\s*$", text):
            live_secret_manifests.append(rel_path.as_posix())

    assert live_secret_manifests == []
    assert (ROOT / "atlas" / "kubernetes" / "secret.example.yml").exists()


def test_public_experiment_papers_do_not_publish_known_invalid_outputs():
    bad_patterns = (
        "Unknown operation",
        "zero tool failures",
        "output SHA-256: unavailable",
        "0.000 g/mol",
    )
    offenders = []
    for paper in sorted((ROOT / "experiments" / "ab_test").glob("**/papers/*.md")):
        text = paper.read_text(encoding="utf-8")
        for pattern in bad_patterns:
            if pattern in text:
                offenders.append(f"{paper.relative_to(ROOT)}: {pattern}")

    assert offenders == []


def test_release_hygiene_workflow_runs_public_checks():
    workflow = ROOT / ".github" / "workflows" / "release-hygiene.yml"
    assert workflow.exists()
    text = workflow.read_text(encoding="utf-8")
    assert "tests/test_public_release_hygiene.py" in text
    assert "scripts/diagnostics/verify_secret_hygiene.py" in text


def test_release_candidate_metadata_and_curated_evidence_are_consistent():
    spec = importlib.util.spec_from_file_location(
        "check_release", ROOT / "scripts/release/check_release.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.check(ROOT)
    assert result["passed"], result["errors"]


def test_release_member_filter_rejects_private_state_and_traversal():
    spec = importlib.util.spec_from_file_location(
        "check_release", ROOT / "scripts/release/check_release.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("../secret", "/tmp/secret", "amy/.env", "amy/atlas/.api_keys.enc",
                 "amy/output/transcript.json", "amy/.venv/bin/python",
                 "amy/atlas/app/security/secrets_backup.json", "amy/service.secret.json",
                 "amy/secret.yaml"):
        assert module.unsafe_member(name), name
    for name in ("amy/.env.example", "amy/core/runtime_receipts.py",
                 "amy/release_evidence/autocorrelation/candidate.json"):
        assert not module.unsafe_member(name), name
