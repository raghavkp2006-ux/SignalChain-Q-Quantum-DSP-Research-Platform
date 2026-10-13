"""ECG-aware adaptive activity threshold and marked frequency bands (Section 10)."""
import math
from typing import List, Tuple
import numpy as np
from qsp.core.types import ECGSegment


def compute_segment_activity(segment_data: np.ndarray) -> float:
    """A_j = mean(abs(x_j - median(x_j)))."""
    return float(np.mean(np.abs(segment_data - np.median(segment_data))))


def compute_adaptive_cutoffs_for_segments(
    segments: List[ECGSegment],
    fs: float = 360.0,
    segment_length: int = 256,
    f_low_hz: float = 0.5,
    f_high_min_hz: float = 25.0,
    f_high_max_hz: float = 45.0,
    lower_percentile: float = 10.0,
    upper_percentile: float = 90.0,
) -> None:
    """Compute and attach adaptive bandwidth and marked frequency bins to all segments in-place."""
    if not segments:
        return

    # 1. Compute activity scores across all segments
    activities = np.array([compute_segment_activity(seg.raw_data) for seg in segments], dtype=np.float64)

    # 2. Global recording activity distribution percentiles
    q_low = float(np.percentile(activities, lower_percentile))
    q_high = float(np.percentile(activities, upper_percentile))
    denom = max(q_high - q_low, 1e-12)

    M = segment_length
    k_low = int(math.ceil(f_low_hz * M / fs))

    for i, seg in enumerate(segments):
        a_j = activities[i]
        u_j = float(np.clip((a_j - q_low) / denom, 0.0, 1.0))
        f_high_j = f_high_min_hz + u_j * (f_high_max_hz - f_high_min_hz)

        k_high = int(math.floor(f_high_j * M / fs))
        # Ensure k_low <= k_high and k_high < M // 2
        k_high = max(k_low, min(k_high, (M // 2) - 1))

        # Count symmetric marked states
        # k_low <= k <= k_high and (M - k_high) <= k <= (M - k_low)
        marked_count = 2 * (k_high - k_low + 1)

        seg.activity_score = a_j
        seg.normalized_activity = u_j
        seg.adaptive_highcut_hz = f_high_j
        seg.k_low = k_low
        seg.k_high = k_high
        seg.marked_count = marked_count

from qsp.core.frequency_mask import get_marked_frequencies_mask
