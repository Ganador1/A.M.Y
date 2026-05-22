import os
from pathlib import Path

import pytest

from app.services.data_versioning import DataVersioningService
from app.config import settings


@pytest.mark.asyncio
async def test_version_data_size_limit(tmp_path, monkeypatch):
    # Set small size limit (1 KB)
    monkeypatch.setattr(settings, "max_version_file_bytes", 1024)
    monkeypatch.setattr(settings, "strict_data_paths", False)
    svc = DataVersioningService()

    # Create a temp file of ~2KB
    test_file = tmp_path / "big.dat"
    test_file.write_bytes(b"0" * 2048)

    res = await svc.version_data({"data_path": str(test_file)})
    assert not res["success"]
    assert "exceeds limit" in res["error"]


@pytest.mark.asyncio
async def test_version_data_strict_paths(tmp_path, monkeypatch):
    # Enable strict paths and set allowed root to tmp_path/data
    allowed_root = tmp_path / "data"
    allowed_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "strict_data_paths", True)
    monkeypatch.setattr(settings, "allowed_data_root", str(allowed_root))
    svc = DataVersioningService()

    # Create a file outside allowed root
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("hello")

    res = await svc.version_data({"data_path": str(outside_file)})
    assert not res["success"]
    assert "outside allowed root" in res["error"]


@pytest.mark.asyncio
async def test_version_data_ok_within_root(tmp_path, monkeypatch):
    # Allow within a custom root
    allowed_root = tmp_path / "data"
    allowed_root.mkdir(parents=True, exist_ok=True)
    in_file = allowed_root / "ok.txt"
    in_file.write_text("hello")

    monkeypatch.setattr(settings, "strict_data_paths", True)
    monkeypatch.setattr(settings, "allowed_data_root", str(allowed_root))
    svc = DataVersioningService()

    res = await svc.version_data({"data_path": str(in_file)})
    assert res["success"] is True
    assert res["version_id"]


@pytest.mark.asyncio
async def test_versions_persist(tmp_path, monkeypatch):
    # Use a temp data directory by changing CWD
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        svc = DataVersioningService()
        f = Path("./data/sample.txt")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("v1")

        res = await svc.version_data({"data_path": str(f)})
        assert res["success"]
        v_id = res["version_id"]

        # Recreate service and ensure it loads existing versions
        svc2 = DataVersioningService()
        r = svc2.get_version({"version_id": v_id})
        assert r["success"]
        assert r["version"]["data_path"] == str(f)
    finally:
        os.chdir(cwd)
