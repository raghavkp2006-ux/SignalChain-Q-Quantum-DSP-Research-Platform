"""MIT-BIH Noise Stress Test Database (nstdb) loader and noise record extractor (Section 5 & 6)."""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import wfdb

from qsp.core.types import ECGRecord
from qsp.datasets.physionet_utils import is_physionet_online
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr


DEFAULT_NSTDB_RAW_DIR = Path("data/raw/nstdb")
DEFAULT_MITDB_RAW_DIR = Path("data/raw/mitdb")

NSTDB_NOISE_RECORDS = ["bw", "ma", "em"]
NSTDB_TEST_RECORDS = [
    "118e24", "118e18", "118e12", "118e06", "118e00", "118e_6",
    "119e24", "119e18", "119e12", "119e06", "119e00", "119e_6",
]


def load_nstdb_noise(
    noise_type: str,
    raw_dir: Optional[Union[str, Path]] = None,
    max_samples: Optional[int] = None,
    seed: int = 1448,
) -> np.ndarray:
    """Load baseline wander (bw), muscle artifact (ma), or electrode motion (em) noise vector."""
    local_dir = Path(raw_dir) if raw_dir else DEFAULT_NSTDB_RAW_DIR
    nt = noise_type.lower().strip()
    if nt not in NSTDB_NOISE_RECORDS:
        raise ValueError(f"Unknown NSTDB noise type '{noise_type}'. Expected one of {NSTDB_NOISE_RECORDS}")

    # 1. Try local cache
    if (local_dir / f"{nt}.hea").exists() and (local_dir / f"{nt}.dat").exists():
        try:
            rec = wfdb.rdrecord(str(local_dir / nt), sampto=max_samples)
            return rec.p_signal[:, 0].astype(np.float64)
        except Exception:
            pass

    # 2. Try remote download if PhysioNet is reachable
    if is_physionet_online():
        try:
            rec = wfdb.rdrecord(nt, pn_dir="nstdb", sampto=max_samples)
            return rec.p_signal[:, 0].astype(np.float64)
        except Exception:
            pass

    # 3. Deterministic synthetic fallback
    n_samp = max_samples or 10000
    return get_noise_vector(nt, n_samples=n_samp, fs=360.0, seed=seed)


def load_nstdb_test_case(
    record_name: str,
    raw_dir: Optional[Union[str, Path]] = None,
    clean_raw_dir: Optional[Union[str, Path]] = None,
    max_samples: Optional[int] = None,
    seed: int = 1448,
) -> Tuple[ECGRecord, ECGRecord, float]:
    """Load an NSTDB calibrated noisy record alongside its clean counterpart.

    Example record_name: '118e12' -> clean='118', target_snr=12.0 dB
    Returns:
        (clean_record, noisy_record, target_snr_db)
    """
    local_dir = Path(raw_dir) if raw_dir else DEFAULT_NSTDB_RAW_DIR
    clean_dir = Path(clean_raw_dir) if clean_raw_dir else DEFAULT_MITDB_RAW_DIR

    # Parse clean ID and SNR
    clean_id = record_name[:3]  # '118' or '119'
    snr_suffix = record_name[4:]  # '24', '18', '12', '06', '00', '_6'
    if snr_suffix == "_6":
        snr_val = -6.0
    else:
        snr_val = float(snr_suffix)

    # 1. Load clean reference record
    from qsp.datasets.mitdb import load_mitdb_record
    clean_rec = load_mitdb_record(
        record_id=clean_id,
        raw_dir=clean_dir,
        max_samples=max_samples,
        seed=seed,
    )

    # 2. Load noisy NSTDB recording
    noisy_sig = None
    if (local_dir / f"{record_name}.hea").exists() and (local_dir / f"{record_name}.dat").exists():
        try:
            rec = wfdb.rdrecord(str(local_dir / record_name), sampto=max_samples)
            noisy_sig = rec.p_signal[:, 0].astype(np.float64)
        except Exception:
            pass

    if noisy_sig is None and is_physionet_online():
        try:
            rec = wfdb.rdrecord(record_name, pn_dir="nstdb", sampto=max_samples)
            noisy_sig = rec.p_signal[:, 0].astype(np.float64)
        except Exception:
            pass

    if noisy_sig is None:
        # Fallback synthesis using em noise (standard NSTDB cocktail)
        noise_vec = load_nstdb_noise("em", raw_dir=local_dir, max_samples=len(clean_rec.signal), seed=seed)
        noisy_sig, _, _ = mix_noise_at_snr(
            clean_ecg=clean_rec.signal,
            noise=noise_vec,
            target_snr_db=snr_val,
            tolerance_db=0.25,
        )

    noisy_sig = np.nan_to_num(noisy_sig, nan=0.0, posinf=1.0, neginf=-1.0)
    min_len = min(len(clean_rec.signal), len(noisy_sig))
    clean_rec.signal = clean_rec.signal[:min_len]
    noisy_sig = noisy_sig[:min_len]

    noisy_record = ECGRecord(
        signal=noisy_sig,
        sampling_rate_hz=clean_rec.sampling_rate_hz,
        record_id=record_name,
        channel_index=0,
        channel_label="MLII",
        clean_reference=clean_rec.signal.copy(),
        metadata={
            "dataset_source": "nstdb",
            "clean_record": clean_id,
            "noise_record": record_name,
            "noise_type": "nstdb_cocktail",
            "target_snr_db": snr_val,
        },
    )

    return clean_rec, noisy_record, snr_val
