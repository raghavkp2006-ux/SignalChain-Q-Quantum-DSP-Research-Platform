"""Classical adaptive FFT bandpass denoiser: primary fair quantum baseline (Section 9, C3)."""
from typing import List
import numpy as np
from qsp.core.framing import overlap_add_reconstruct, segment_signal
from qsp.modalities.ecg.preprocessing import (
    compute_adaptive_cutoffs_for_segments,
    get_marked_frequencies_mask,
)


def apply_fft_adaptive_bandpass(
    ecg: np.ndarray,
    fs: float = 360.0,
    segment_length: int = 256,
    hop_length: int = 128,
    f_low_hz: float = 0.5,
    f_high_min_hz: float = 25.0,
    f_high_max_hz: float = 45.0,
) -> np.ndarray:
    """Fair classical equivalent of QFT adaptive filtering.

    Applies FFT -> hard binary mask -> IFFT on identical windowed segments,
    followed by weighted overlap-add reconstruction.
    """
    orig_len = len(ecg)
    segments, pad_len = segment_signal(ecg, segment_length=segment_length, hop_length=hop_length)

    compute_adaptive_cutoffs_for_segments(
        segments=segments,
        fs=fs,
        segment_length=segment_length,
        f_low_hz=f_low_hz,
        f_high_min_hz=f_high_min_hz,
        f_high_max_hz=f_high_max_hz,
    )

    processed_windows: List[np.ndarray] = []
    for seg in segments:
        # Windowed input
        xw = seg.windowed_data

        # FFT
        X = np.fft.fft(xw)

        # Marked frequency binary mask (1 if marked, 0 otherwise)
        mask = get_marked_frequencies_mask(segment_length, seg.k_low, seg.k_high)

        # Apply hard binary mask
        X_filtered = X * mask.astype(np.float64)

        # IFFT
        x_rec = np.real(np.fft.ifft(X_filtered))
        processed_windows.append(x_rec)

    # Weighted overlap-add reconstruction
    reconstructed = overlap_add_reconstruct(
        processed_windows=processed_windows,
        original_length=orig_len,
        pad_len=pad_len,
        segment_length=segment_length,
        hop_length=hop_length,
    )
    return reconstructed
