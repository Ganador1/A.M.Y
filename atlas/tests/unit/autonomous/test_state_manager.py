import json
from pathlib import Path

from app.autonomous.core.state_manager import IterationRecord, StateManager


def _make_record(iteration=1, domain="biology"):
    return IterationRecord(
        iteration=iteration,
        domain=domain,
        selected_ids=["a", "b"],
        actions=["analyze"],
        outcomes={"a": {"score": 0.8}},
    )


def test_add_iteration_and_latest():
    manager = StateManager()
    record = _make_record()

    manager.add_iteration(record)

    latest = manager.latest()
    assert latest is record
    stats = manager.stats()
    assert stats["iterations"] == 1
    assert set(stats["domains"]) == {"biology"}


def test_snapshot_writes_file(tmp_path: Path):
    manager = StateManager()
    manager.add_iteration(_make_record())

    target = tmp_path / "state.json"
    manager.snapshot(target)

    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["iterations"][0]["domain"] == "biology"


def test_load_snapshot_rehydrates_state(tmp_path: Path):
    payload = {
        "iterations": [
            {
                "iteration": 2,
                "domain": "chemistry",
                "selected_ids": ["x"],
                "actions": ["simulate"],
                "outcomes": {"x": {"result": 1}},
                "timestamp": 123.0,
            }
        ],
        "meta": {"version": 2},
    }
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps(payload), encoding="utf-8")

    manager = StateManager()
    loaded = manager.load_snapshot(snapshot)

    assert loaded == 1
    latest = manager.latest()
    assert latest is not None
    assert latest.domain == "chemistry"
    assert latest.outcomes["x"]["result"] == 1


def test_load_snapshot_handles_missing_file(tmp_path: Path):
    manager = StateManager()
    missing = tmp_path / "missing.json"

    loaded = manager.load_snapshot(missing)

    assert loaded == 0
    assert manager.latest() is None


def test_save_snapshot_alias(tmp_path: Path):
    manager = StateManager()
    manager.add_iteration(_make_record(iteration=3, domain="quantum"))

    path = tmp_path / "alias.json"
    manager.save_snapshot(path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["iterations"][0]["domain"] == "quantum"
