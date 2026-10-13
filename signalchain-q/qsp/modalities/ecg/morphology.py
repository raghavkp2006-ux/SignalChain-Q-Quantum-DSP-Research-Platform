"""ECG morphology and R-peak detection evaluation (Section 19)."""
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import signal


def detect_r_peaks_pantompkins(
    ecg: np.ndarray,
    fs: float = 360.0,
) -> np.ndarray:
    """Robust Python implementation of the Pan-Tompkins QRS detection algorithm."""
    if len(ecg) < int(fs):
        return np.array([], dtype=int)

    # 1. Bandpass filter (5 - 15 Hz)
    low = 5.0 / (0.5 * fs)
    high = 15.0 / (0.5 * fs)
    b, a = signal.butter(1, [low, high], btype="bandpass")
    filtered = signal.filtfilt(b, a, ecg)

    # 2. Derivative filter
    h_deriv = [-1.0, -2.0, 0.0, 2.0, 1.0]
    deriv = np.convolve(filtered, h_deriv, mode="same") * (fs / 8.0)

    # 3. Squaring function
    squared = deriv ** 2

    # 4. Moving-window integrator (~150 ms)
    win_len = int(0.150 * fs)
    integrated = np.convolve(squared, np.ones(win_len) / win_len, mode="same")

    # 5. Adaptive thresholding and peak finding
    min_distance = int(0.200 * fs)  # minimum 200 ms between R peaks (refractory period)
    threshold = 0.35 * np.mean(integrated) + 0.15 * np.std(integrated)

    peaks, _ = signal.find_peaks(integrated, height=threshold, distance=min_distance)

    # Refine peaks to actual local maximum in original filtered ECG within ±50ms
    search_radius = int(0.050 * fs)
    refined_peaks: List[int] = []
    for p in peaks:
        left = max(0, p - search_radius)
        right = min(len(ecg), p + search_radius + 1)
        actual_r = left + int(np.argmax(ecg[left:right]))
        if len(refined_peaks) == 0 or (actual_r - refined_peaks[-1]) >= min_distance:
            refined_peaks.append(actual_r)

    return np.array(refined_peaks, dtype=int)


def evaluate_r_peak_detections(
    ref_peaks: np.ndarray,
    test_peaks: np.ndarray,
    fs: float = 360.0,
    tolerance_ms: float = 50.0,
) -> Dict[str, float]:
    """Compare detected R-peaks against reference annotations within tolerance."""
    if len(ref_peaks) == 0:
        return {
            "r_peak_sensitivity": 1.0 if len(test_peaks) == 0 else 0.0,
            "r_peak_positive_predictivity": 1.0 if len(test_peaks) == 0 else 0.0,
            "r_peak_f1": 1.0 if len(test_peaks) == 0 else 0.0,
            "median_absolute_r_peak_timing_error_ms": 0.0,
        }

    tol_samples = int((tolerance_ms / 1000.0) * fs)
    matched_test = set()
    timing_errors_ms: List[float] = []

    tp = 0
    for r in ref_peaks:
        diffs = np.abs(test_peaks - r)
        within = np.where(diffs <= tol_samples)[0]
        # Find unused candidate with min distance
        unused = [idx for idx in within if idx not in matched_test]
        if unused:
            best_idx = min(unused, key=lambda idx: diffs[idx])
            matched_test.add(best_idx)
            tp += 1
            timing_errors_ms.append(float(diffs[best_idx] / fs * 1000.0))

    fn = len(ref_peaks) - tp
    fp = len(test_peaks) - tp

    se = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = (2 * se * ppv) / (se + ppv) if (se + ppv) > 0 else 0.0
    median_err = float(np.median(timing_errors_ms)) if timing_errors_ms else 0.0

    return {
        "r_peak_sensitivity": round(se, 4),
        "r_peak_positive_predictivity": round(ppv, 4),
        "r_peak_f1": round(f1, 4),
        "median_absolute_r_peak_timing_error_ms": round(median_err, 3),
    }
