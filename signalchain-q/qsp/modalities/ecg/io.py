"""I/O routines for ECG datasets and web upload CSV processing (Section 26)."""
import io
from pathlib import Path
from typing import Optional, Tuple, Union
import numpy as np
import pandas as pd
from qsp.core.types import ECGRecord


def load_ecg_csv(
    file_or_path: Union[str, Path, io.StringIO, io.BytesIO],
    sampling_rate_hz: Optional[float] = None,
    default_fs: float = 360.0,
) -> Tuple[np.ndarray, float, Optional[np.ndarray]]:
    """Parse an ECG CSV file.

    Supported formats:
      1. Single column: amplitude
      2. Two columns: time, amplitude

    Returns:
        signal: 1D np.ndarray
        fs: sampling rate in Hz
        time_vector: optional 1D np.ndarray
    """
    if isinstance(file_or_path, io.BytesIO):
        df = pd.read_csv(file_or_path)
    elif isinstance(file_or_path, io.StringIO):
        df = pd.read_csv(file_or_path)
    else:
        df = pd.read_csv(str(file_or_path))

    # Clean column headers
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "amplitude" in df.columns:
        signal = df["amplitude"].values.astype(np.float64)
    elif "val" in df.columns:
        signal = df["val"].values.astype(np.float64)
    elif "signal" in df.columns:
        signal = df["signal"].values.astype(np.float64)
    elif len(df.columns) == 1:
        signal = df.iloc[:, 0].values.astype(np.float64)
    elif len(df.columns) >= 2:
        # Default: first is time, second is amplitude
        signal = df.iloc[:, 1].values.astype(np.float64)
    else:
        raise ValueError("Unsupported CSV format: could not find ECG amplitude column.")

    # Validation: Check finite and non-empty
    if len(signal) == 0:
        raise ValueError("Signal too short: CSV contains 0 samples.")
    if not np.all(np.isfinite(signal)):
        raise ValueError("Invalid numeric values: signal contains NaN or Inf.")

    time_vector = None
    if "time" in df.columns:
        time_vals = df["time"].values.astype(np.float64)
        if len(time_vals) > 1:
            diffs = np.diff(time_vals)
            positive_diffs = diffs[diffs > 0]
            if len(positive_diffs) > 0:
                inferred_dt = float(np.median(positive_diffs))
                if inferred_dt > 0:
                    fs = 1.0 / inferred_dt
                    time_vector = time_vals
                    return signal, round(fs, 2), time_vector

    if sampling_rate_hz is not None and sampling_rate_hz > 0:
        fs = float(sampling_rate_hz)
    else:
        fs = float(default_fs)

    return signal, fs, time_vector


def generate_synthetic_lead(
    duration_sec: float = 10.0,
    fs: float = 360.0,
    heart_rate_bpm: float = 72.0,
    seed: int = 1448,
) -> ECGRecord:
    """Generate a clean synthetic normal sinus rhythm ECG lead for testing."""
    rng = np.random.default_rng(seed)
    n_samples = int(duration_sec * fs)
    t = np.arange(n_samples) / fs
    rr_interval = 60.0 / heart_rate_bpm

    # Synthesize P-Q-R-S-T waves as weighted Gaussians centered at beat intervals
    signal = np.zeros(n_samples, dtype=np.float64)
    beat_times = np.arange(0.2, duration_sec - 0.2, rr_interval)

    for bt in beat_times:
        # P wave
        signal += 0.15 * np.exp(-((t - (bt - 0.16)) ** 2) / (2 * (0.025 ** 2)))
        # Q wave
        signal -= 0.15 * np.exp(-((t - (bt - 0.04)) ** 2) / (2 * (0.01 ** 2)))
        # R wave
        signal += 1.20 * np.exp(-((t - bt) ** 2) / (2 * (0.015 ** 2)))
        # S wave
        signal -= 0.25 * np.exp(-((t - (bt + 0.035)) ** 2) / (2 * (0.012 ** 2)))
        # T wave
        signal += 0.30 * np.exp(-((t - (bt + 0.22)) ** 2) / (2 * (0.045 ** 2)))

    # Subtle baseline respiration drift
    signal += 0.05 * np.sin(2 * np.pi * 0.25 * t)

    return ECGRecord(
        signal=signal,
        sampling_rate_hz=fs,
        record_id="synthetic_demo",
        channel_index=0,
        channel_label="Lead_II",
        clean_reference=signal.copy(),
    )
