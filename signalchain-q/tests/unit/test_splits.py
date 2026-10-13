"""Unit tests for MIT-BIH deterministic dataset splits (Section 5 & 29)."""
import json
from pathlib import Path
import pytest


def get_split_path() -> Path:
    p1 = Path("configs/splits/mitdb_v1.json")
    if p1.exists():
        return p1
    p2 = Path("signalchain-q/configs/splits/mitdb_v1.json")
    if p2.exists():
        return p2
    return Path(__file__).resolve().parents[2] / "configs" / "splits" / "mitdb_v1.json"


def test_mitdb_split_file_exists():
    split_path = get_split_path()
    assert split_path.exists(), f"mitdb_v1.json must exist at {split_path}."


def test_mitdb_split_rules():
    split_path = get_split_path()
    with open(split_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    splits = data["splits"]
    dev = splits["development"]
    val = splits["validation"]
    test = splits["test"]

    # Total must be 48
    all_recs = dev + val + test
    assert len(all_recs) == 48, f"Expected 48 MIT-BIH records, got {len(all_recs)}"
    assert len(set(all_recs)) == 48, "Duplicate records found across splits!"

    # Rule: 201 and 202 must stay in the same split
    in_dev = ("201" in dev) and ("202" in dev)
    in_val = ("201" in val) and ("202" in val)
    in_test = ("201" in test) and ("202" in test)
    assert in_dev or in_val or in_test, "Records 201 and 202 MUST be in the same split!"

    # Rule: 118 and 119 excluded from tuning (must be in test)
    assert "118" in test, "Record 118 must be in test split."
    assert "119" in test, "Record 119 must be in test split."
    assert "118" not in dev and "118" not in val
    assert "119" not in dev and "119" not in val
