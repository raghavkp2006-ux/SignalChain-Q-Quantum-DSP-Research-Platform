"""Unified ECG pipeline orchestration function run_ecg_pipeline(...) (Section 2 & 20)."""
import time
from typing import Any, Dict, Optional
import numpy as np

from qsp.classical.registry import get_classical_method
from qsp.core.metrics import evaluate_signal_metrics
from qsp.core.timing import StageTimer
from qsp.core.types import FilterResult
from qsp.modalities.ecg.morphology import (
    detect_r_peaks_pantompkins,
    evaluate_r_peak_detections,
)
from qsp.quantum.pipeline import run_quantum_ecg_pipeline


def run_ecg_pipeline(
    signal: np.ndarray,
    method: str = "fft_adaptive_bandpass",
    fs: float = 360.0,
    clean_reference: Optional[np.ndarray] = None,
    params: Optional[Dict[str, Any]] = None,
) -> FilterResult:
    """Orchestrate end-to-end ECG filtering pipeline.

    Supported methods:
      - 'raw'
      - 'butterworth_bandpass'
      - 'wavelet_db6'
      - 'fft_adaptive_bandpass'
      - 'qft_grover_ecg_adaptive'
    """
    params = params or {}
    timer = StageTimer()
    method_key = method.lower().strip()

    t_start = time.perf_counter()

    if method_key == "qft_grover_ecg_adaptive":
        # Quantum pipeline execution
        res = run_quantum_ecg_pipeline(
            ecg=signal,
            fs=fs,
            segment_length=params.get("segment_length", 256),
            hop_length=params.get("hop_length", 128),
            f_low_hz=params.get("f_low_hz", 0.5),
            f_high_min_hz=params.get("f_high_min_hz", 25.0),
            f_high_max_hz=params.get("f_high_max_hz", 45.0),
            oracle_type=params.get("oracle", "diagonal_reference"),
            grover_iterations_cap=params.get("grover_iteration_cap", 3),
            fixed_grover_iterations=params.get("fixed_grover_iterations", None),
            transpile_optimization_level=params.get("transpile_optimization_level", 3),
        )
        processed = res.processed_signal
        q_resources = res.quantum_resources
        timings = res.stage_timings_ms
    else:
        # Classical DSP method execution
        fn = get_classical_method(method_key)
        # Filter method arguments that match signature
        if method_key == "butterworth_bandpass":
            filtered = fn(
                ecg=signal,
                fs=fs,
                order=params.get("order", 4),
                lowcut_hz=params.get("lowcut_hz", 0.5),
                highcut_hz=params.get("highcut_hz", 40.0),
                zero_phase=params.get("zero_phase", True),
            )
        elif method_key == "wavelet_db6":
            filtered = fn(
                ecg=signal,
                wavelet_name=params.get("wavelet_name", "db6"),
                max_level=params.get("max_level", 5),
                threshold_mode=params.get("threshold_mode", "soft"),
                mad_scale=params.get("mad_scale", 0.6745),
            )
        elif method_key == "fft_adaptive_bandpass":
            filtered = fn(
                ecg=signal,
                fs=fs,
                segment_length=params.get("segment_length", 256),
                hop_length=params.get("hop_length", 128),
                f_low_hz=params.get("f_low_hz", 0.5),
                f_high_min_hz=params.get("f_high_min_hz", 25.0),
                f_high_max_hz=params.get("f_high_max_hz", 45.0),
            )
        else:
            filtered = fn(ecg=signal)

        processed = filtered
        q_resources = None
        timings = {"total_ms": (time.perf_counter() - t_start) * 1000.0}

    # Evaluate waveform quality metrics
    metrics = evaluate_signal_metrics(
        processed=processed,
        clean_reference=clean_reference,
        noisy_input=signal,
    )

    # Evaluate morphology / R-peak preservation if clean reference is available
    if clean_reference is not None:
        ref_peaks = detect_r_peaks_pantompkins(clean_reference, fs=fs)
        test_peaks = detect_r_peaks_pantompkins(processed, fs=fs)
        morph_results = evaluate_r_peak_detections(ref_peaks, test_peaks, fs=fs)
        metrics.r_peak_sensitivity = morph_results["r_peak_sensitivity"]
        metrics.r_peak_positive_predictivity = morph_results["r_peak_positive_predictivity"]
        metrics.r_peak_f1 = morph_results["r_peak_f1"]
        metrics.median_absolute_r_peak_timing_error_ms = morph_results["median_absolute_r_peak_timing_error_ms"]

    return FilterResult(
        method_name=method_key,
        processed_signal=processed,
        original_signal=signal,
        clean_reference=clean_reference,
        sampling_rate_hz=fs,
        metrics=metrics,
        stage_timings_ms=timings,
        quantum_resources=q_resources,
    )
