"""Unit and regression tests for Phase 8 validation grid tuning and parameter freezing."""
import json
from pathlib import Path
import pytest
import yaml

from qsp.experiments.validate_ecg import generate_parameter_grid
from qsp.datasets.mitdb import load_mitdb_split, load_mitdb_record


_BASE = Path(__file__).resolve().parent.parent.parent
SPLITS_PATH = _BASE / "configs" / "splits" / "mitdb_v1.json" if (_BASE / "configs" / "splits" / "mitdb_v1.json").exists() else Path("configs/splits/mitdb_v1.json")
FROZEN_CONFIG_PATH = _BASE / "configs" / "ecg_frozen_v1.yaml" if (_BASE / "configs" / "ecg_frozen_v1.yaml").exists() else Path("configs/ecg_frozen_v1.yaml")


def test_validation_grid_generation_108_configs():
    """Verify that parameter grid produces exactly 108 valid configurations."""
    grid = generate_parameter_grid()
    assert len(grid) == 108, f"Expected 108 configurations, got {len(grid)}"

    # Ensure every single configuration satisfies f_high_min < f_high_max
    for cfg in grid:
        assert cfg["f_high_min"] < cfg["f_high_max"], f"Invalid cutoffs: {cfg}"
        assert cfg["segment_size"] in [64, 128, 256]
        assert cfg["grover_iterations"] in [0, 1, 2, 3]


def test_validation_split_isolation():
    """Verify validation split contains 201/202 and zero test records."""
    with open(SPLITS_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    val_records = set(str(r) for r in meta["splits"]["validation"])
    test_records = set(str(r) for r in meta["splits"]["test"])

    assert "201" in val_records
    assert "202" in val_records
    assert "118" in test_records
    assert "119" in test_records

    # Zero overlap
    intersection = val_records.intersection(test_records)
    assert len(intersection) == 0, f"Contamination: {intersection}"


def test_validation_loader_rejects_test_contamination(tmp_path):
    """Test that load_mitdb_split raises ValueError if test records are found in validation."""
    dirty_splits = {
        "metadata": {"dataset": "mitdb"},
        "splits": {
            "validation": ["101", "118"],  # Contaminated with test record 118
            "test": ["118", "119"],
        },
    }
    dirty_path = tmp_path / "dirty_splits.json"
    with open(dirty_path, "w", encoding="utf-8") as f:
        json.dump(dirty_splits, f)

    with pytest.raises(ValueError, match="TEST CONTAMINATION"):
        load_mitdb_split("validation", splits_file=dirty_path)


def test_frozen_config_immutability():
    """Regression test: Phase 9 and Phase 10 cannot automatically modify configs/ecg_frozen_v1.yaml."""
    if not FROZEN_CONFIG_PATH.exists():
        pytest.skip("ecg_frozen_v1.yaml not created yet")

    with open(FROZEN_CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Must be frozen and strictly marked that test set was not used
    assert cfg["selection"]["frozen"] is True
    assert cfg["selection"]["test_set_used_for_selection"] is False
    assert "config_hash" in cfg
    assert len(cfg["config_hash"]) == 64  # SHA-256
