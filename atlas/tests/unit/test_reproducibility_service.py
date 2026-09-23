import json
from pathlib import Path

from app.services.reproducibility import ReproducibilityService


class DummyExperimentService:
    def __init__(self, artifacts=None):
        self._exp = {
            "experiment_id": "exp1",
            "name": "Test Experiment",
            "description": "",
            "parameters": {"alpha": 0.1},
            "metrics": {"acc": 0.9},
            "tags": {},
            "status": "completed",
            "created_at": "2025-09-03T10:00:00Z",
            "completed_at": "2025-09-03T10:10:00Z",
            "run_id": "run-123",
            "artifacts": artifacts or [],
        }

    def get_experiment(self, req):
        if req.get("experiment_id") != "exp1":
            return {"success": False, "error": "not found"}
        return {"success": True, "experiment": self._exp}


class DummyDataVersioningService:
    def __init__(self):
        self.data_versions = {}


def test_manifest_and_zip_creation(tmp_path, monkeypatch):
    # Arrange: create small artifact file
    art_dir = tmp_path / "arts"
    art_dir.mkdir()
    art_file = art_dir / "a.txt"
    art_file.write_text("hello")

    exp_service = DummyExperimentService(artifacts=[str(art_file)])
    dv_service = DummyDataVersioningService()

    svc = ReproducibilityService()
    # Redirect exports dir to temp
    svc.exports_dir = tmp_path / "exports"
    svc.exports_dir.mkdir(parents=True, exist_ok=True)

    # Act
    res = svc.create_reproducible_package(
        experiment_service=exp_service,
        data_versioning_service=dv_service,
        experiment_id="exp1",
        include_artifacts=True,
        max_artifact_bytes=1024,
    )

    # Assert
    assert res.get("success") is True
    summary = res["summary"]
    manifest_path = Path(summary["manifest_path"])
    zip_path = Path(summary["zip_path"]) if isinstance(summary["zip_path"], str) else Path(summary["zip_path"])  # type: ignore[arg-type]
    assert manifest_path.exists()
    assert zip_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert manifest["experiment"]["experiment_id"] == "exp1"
    assert manifest["export_options"]["include_artifacts"] is True


def test_cleanup_retention(tmp_path):
    svc = ReproducibilityService()
    svc.exports_dir = tmp_path / "exports"
    svc.exports_dir.mkdir(parents=True, exist_ok=True)

    # Create 3 dummy bundles and zips
    for i in range(3):
        bd = svc.exports_dir / f"bundle_x_{i}"
        bd.mkdir()
        (bd / "manifest.json").write_text("{}")
        (bd.with_suffix(".zip")).write_text("zip")
    # Keep only 2 most recent
    deleted = svc.cleanup_old_exports(max_bundles=2)
    assert deleted == 1
    remaining = [p for p in svc.exports_dir.iterdir() if p.is_dir() and p.name.startswith("bundle_")]
    assert len(remaining) == 2
