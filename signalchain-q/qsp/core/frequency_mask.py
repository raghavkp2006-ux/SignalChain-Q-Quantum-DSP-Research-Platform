"""Marked frequency bin calculations for QSP phase oracles and classical FFT filters."""
import numpy as np


def get_marked_frequencies_mask(
    segment_length: int,
    k_low: int,
    k_high: int,
) -> np.ndarray:
    """Return boolean mask of marked frequency states (Section 10).

    marked(k) = (k_low <= k <= k_high) OR (M - k_high <= k <= M - k_low)
    DC (k=0) is unmarked.
    """
    M = segment_length
    mask = np.zeros(M, dtype=bool)

    if k_low <= k_high and k_high < M:
        mask[k_low : k_high + 1] = True
        mask[M - k_high : M - k_low + 1] = True

    mask[0] = False  # DC unmarked
    return mask
