"""Deterministic benchmark runner executing classical vs quantum ECG evaluations (Section 20 & 21)."""
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from qsp.core.reproducibility import seed_everything
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr
from qsp.modalities.ecg.pipeline import run_ecg_pipeline


REQUIRED_METHODS = [
    "raw",
    "butterworth_bandpass",
    "wavelet_db6",
    "fft_adaptive_bandpass",
    "qft_grover_ecg_adaptive",
]


def run_benchmark_on_segments(
    records: List[Dict[str, Any]],
    noise_types: List[str] = ("bw", "ma", "em"),
    snr_levels: List[float] = (-6.0, 0.0, 6.0, 12.0, 18.0, 24.0),
    methods: Optional[List[str]] = None,
    seed: int = 1448,
    progress_callback: Optional[callable] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Execute evaluation across methods, noise types, and SNR levels."""
    seed_everything(seed)
    methods_to_run = methods or REQUIRED_METHODS

    results_records: List[Dict[str, Any]] = []
    quantum_records: List[Dict[str, Any]] = []

    total_tasks = len(records) * len(noise_types) * len(snr_levels) * len(methods_to_run)
    completed = 0

    for rec_info in records:
        clean_signal = rec_info["signal"]
        fs = rec_info.get("sampling_rate_hz", 360.0)
        rec_id = rec_info.get("record_id", "rec_0")
        split = rec_info.get("split", "dev")

        n_samples = len(clean_signal)

        for noise_type in noise_types:
            for snr_db in snr_levels:
                # Deterministic noise mixing
                noise_vec = get_noise_vector(
                    noise_type=noise_type,
                    n_samples=n_samples,
                    fs=fs,
                    seed=seed + int(rec_info.get("index", 0)) * 100,
                )
                noisy_sig, actual_snr, _ = mix_noise_at_snr(
                    clean_ecg=clean_signal,
                    noise=noise_vec,
                    target_snr_db=snr_db,
                    tolerance_db=0.25,
                )

                for method in methods_to_run:
                    filter_res = run_ecg_pipeline(
                        signal=noisy_sig,
                        method=method,
                        fs=fs,
                        clean_reference=clean_signal,
                    )

                    row = {
                        "record_id": rec_id,
                        "split": split,
                        "noise_type": noise_type,
                        "target_snr_db": snr_db,
                        "input_snr_db": actual_snr,
                        "method": method,
                        "output_snr_db": filter_res.metrics.output_snr_db,
                        "snr_improvement_db": filter_res.metrics.snr_improvement_db,
                        "rmse": filter_res.metrics.rmse,
                        "mae": filter_res.metrics.mae,
                        "prd": filter_res.metrics.prd,
                        "pearson_r": filter_res.metrics.pearson_r,
                        "r_peak_f1": filter_res.metrics.r_peak_f1,
                        "total_ms": filter_res.stage_timings_ms.get("total_ms", 0.0),
                    }
                    results_records.append(row)

                    if filter_res.quantum_resources:
                        q_dict = filter_res.quantum_resources.to_dict()
                        q_dict.update({
                            "record_id": rec_id,
                            "noise_type": noise_type,
                            "target_snr_db": snr_db,
                            "method": method,
                        })
                        quantum_records.append(q_dict)

                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_tasks)

    return results_records, quantum_records
