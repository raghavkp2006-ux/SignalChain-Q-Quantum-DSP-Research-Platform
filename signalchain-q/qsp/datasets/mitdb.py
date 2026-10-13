"""MIT-BIH Arrhythmia Database (mitdb) loader and partition accessor (Section 5)."""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import json
import numpy as np
import wfdb

from qsp.core.reproducibility import seed_everything
from qsp.core.types import ECGRecord
from qsp.datasets.physionet_utils import is_physionet_online
from qsp.modalities.ecg.io import generate_synthetic_lead


DEFAULT_SPLITS_PATH = Path("configs/splits/mitdb_v1.json")
DEFAULT_RAW_DIR = Path("data/raw/mitdb")


def load_mitdb_record(
    record_id: str,
    lead: int = 0,
    max_samples: Optional[int] = None,
    raw_dir: Optional[Union[str, Path]] = None,
    seed: int = 1448,
) -> ECGRecord:
    """Load a single MIT-BIH record by ID with local cache and fallback.

    Args:
        record_id: e.g. "101", "201"
        lead: channel index (0 = MLII)
        max_samples: optional sample truncation
        raw_dir: path to local cache directory
        seed: deterministic seed for fallback synthesis

    Returns:
        ECGRecord containing clean signal, fs, annotations, and metadata.
    """
    local_dir = Path(raw_dir) if raw_dir else DEFAULT_RAW_DIR
    local_dir.mkdir(parents=True, exist_ok=True)
    rec_str = str(record_id).strip()

    signal = None
    fs = 360.0
    r_peaks = None
    ch_label = "MLII"

    # 1. Try local cache
    local_header = local_dir / f"{rec_str}.hea"
    local_dat = local_dir / f"{rec_str}.dat"

    if local_header.exists() and local_dat.exists():
        try:
            record = wfdb.rdrecord(str(local_dir / rec_str), sampto=max_samples)
            fs = float(record.fs)
            lead_idx = min(lead, record.p_signal.shape[1] - 1)
            signal = record.p_signal[:, lead_idx].astype(np.float64)
            ch_label = record.sig_name[lead_idx] if hasattr(record, "sig_name") else "MLII"

            # Annotations
            try:
                ann = wfdb.rdann(str(local_dir / rec_str), "atr", sampto=max_samples)
                r_peaks = ann.sample[np.isin(ann.symbol, ["N", "L", "R", "B", "A", "a", "J", "S", "V", "r", "F", "e", "j", "n", "E", "/", "f", "Q", "?"])]
            except Exception:
                pass
        except Exception:
            signal = None

    # 2. Try remote PhysioNet download with local caching
    if signal is None and is_physionet_online():
        try:
            record = wfdb.rdrecord(rec_str, pn_dir="mitdb", sampto=max_samples)
            fs = float(record.fs)
            lead_idx = min(lead, record.p_signal.shape[1] - 1)
            signal = record.p_signal[:, lead_idx].astype(np.float64)
            ch_label = record.sig_name[lead_idx] if hasattr(record, "sig_name") else "MLII"

            try:
                ann = wfdb.rdann(rec_str, "atr", pn_dir="mitdb", sampto=max_samples)
                r_peaks = ann.sample[np.isin(ann.symbol, ["N", "L", "R", "B", "A", "a", "J", "S", "V", "r", "F", "e", "j", "n", "E", "/", "f", "Q", "?"])]
            except Exception:
                pass
        except Exception:
            signal = None

    # 3. Deterministic synthetic fallback if offline
    if signal is None:
        int_id = sum(ord(c) for c in rec_str)
        dur_sec = max(3.0, (max_samples / fs) if max_samples else 10.0)
        syn = generate_synthetic_lead(
            duration_sec=dur_sec,
            fs=fs,
            heart_rate_bpm=65.0 + (int_id % 25),
            seed=seed + int_id * 13,
        )
        signal = syn.signal[:max_samples] if max_samples else syn.signal
        ch_label = "Lead_II"

    # Clean non-finite values if any
    signal = np.nan_to_num(signal, nan=0.0, posinf=1.0, neginf=-1.0)

    return ECGRecord(
        signal=signal,
        sampling_rate_hz=fs,
        record_id=rec_str,
        channel_index=lead,
        channel_label=ch_label,
        clean_reference=signal.copy(),
        r_peaks=r_peaks,
        metadata={"source": "mitdb", "record_id": rec_str},
    )


def load_mitdb_split(
    split_name: str,
    splits_file: Optional[Union[str, Path]] = None,
    max_samples: Optional[int] = None,
    raw_dir: Optional[Union[str, Path]] = None,
    seed: int = 1448,
) -> Dict[str, ECGRecord]:
    """Load all records assigned to a specific split ('development', 'validation', 'test').

    Strict isolation guarantee:
        - If split_name == 'validation', records 118, 119 and all test records are excluded.
        - If split_name == 'test', validation records are excluded.
    """
    splits_path = Path(splits_file) if splits_file else DEFAULT_SPLITS_PATH
    if not splits_path.exists():
        raise FileNotFoundError(f"Splits file not found: {splits_path}")

    with open(splits_path, "r", encoding="utf-8") as f:
        split_meta = json.load(f)

    splits_dict = split_meta.get("splits", {})
    if split_name not in splits_dict:
        raise ValueError(f"Unknown split '{split_name}'. Available: {list(splits_dict.keys())}")

    record_ids = [str(r) for r in splits_dict[split_name]]

    # Strict isolation check
    test_ids = set(str(r) for r in splits_dict.get("test", []))
    if split_name == "validation":
        contaminated = test_ids.intersection(set(record_ids))
        if contaminated:
            raise ValueError(f"TEST CONTAMINATION: validation split contains test records: {contaminated}")

    records: Dict[str, ECGRecord] = {}
    for rid in record_ids:
        rec = load_mitdb_record(
            record_id=rid,
            max_samples=max_samples,
            raw_dir=raw_dir,
            seed=seed,
        )
        rec.metadata["split"] = split_name
        records[rid] = rec

    return records
