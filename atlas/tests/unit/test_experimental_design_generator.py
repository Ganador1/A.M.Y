from app.autonomous.generators.experimental_design_generator import generate_experimental_design
from app.autonomous.core.state_manager import StateManager, IterationRecord
from pathlib import Path


def test_generate_basic_plan_cap_limit():
    config = {
        "factors": {
            "lr": [1e-3, 1e-4, 1e-5],
            "batch_size": [16, 32],
            "optimizer": ["adam", "sgd"],
        },
        "max_runs": 4,
        "stop_metric": "val_loss",
        "early_stop_threshold": 0.005,
    }
    result = generate_experimental_design(config)
    assert result["total_planned"] == 4
    assert len(result["runs"]) == 4
    for r in result["runs"]:
        assert set(["lr", "batch_size", "optimizer", "run_id"]).issubset(r.keys())


def test_generate_no_factors():
    result = generate_experimental_design({})
    assert result["total_planned"] == 0
    assert result["runs"] == []
    assert "stop_metric" in result
    assert "early_stop_threshold" in result


def test_generate_threshold_and_metric_defaults():
    result = generate_experimental_design({"factors": {"x": [1, 2]}, "max_runs": 1})
    assert result["stop_metric"] == "loss"
    assert result["early_stop_threshold"] == 0.01


# --- StateManager snapshot tests (integrated aquí por limitaciones de espacio en disco) ---


def test_state_snapshot_round_trip(tmp_path: Path):
    sm = StateManager()
    sm.add_iteration(
        IterationRecord(
            iteration=1,
            domain="math",
            selected_ids=["c1", "c2"],
            actions=["mutate", "sketch"],
            outcomes={"c1": {"status": "open"}},
        )
    )
    out_file = sm.snapshot(tmp_path / "state.json")
    assert out_file.exists()
    sm2 = StateManager()
    loaded = sm2.load_snapshot(out_file)
    assert loaded == 1
    latest = sm2.latest()
    assert latest is not None
    assert latest.domain == "math"
    assert latest.selected_ids == ["c1", "c2"]


def test_state_snapshot_empty_load(tmp_path: Path):
    sm = StateManager()
    missing = tmp_path / "missing.json"
    loaded = sm.load_snapshot(missing)
    assert loaded == 0
