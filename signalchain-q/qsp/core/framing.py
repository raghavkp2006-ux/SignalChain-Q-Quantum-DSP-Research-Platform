"""Segmentation and weighted overlap-add reconstruction for ECG processing (Section 8)."""
from typing import List, Tuple
import numpy as np
from qsp.core.types import ECGSegment


def get_hann_window(segment_length: int) -> np.ndarray:
    """Return periodic or symmetric Hann window."""
    return np.hanning(segment_length)


def segment_signal(
    signal: np.ndarray,
    segment_length: int = 256,
    hop_length: int = 128,
) -> Tuple[List[ECGSegment], int]:
    """Segment an input signal using reflection padding and Hann windowing.

    Returns:
        segments: List of ECGSegment objects
        pad_len: Number of reflection-padded samples on left and right
    """
    if segment_length <= 0 or (segment_length & (segment_length - 1)) != 0:
        raise ValueError(f"segment_length ({segment_length}) must be a power of two.")
    if hop_length <= 0:
        raise ValueError("hop_length must be positive.")

    orig_len = len(signal)
    pad_len = segment_length

    # Reflection padding on both boundaries
    padded = np.pad(signal, pad_len, mode="reflect")

    window = get_hann_window(segment_length)
    segments: List[ECGSegment] = []
    num_samples = len(padded)

    start = 0
    seg_idx = 0
    while start + segment_length <= num_samples:
        raw_slice = padded[start : start + segment_length]
        windowed = raw_slice * window
        segments.append(
            ECGSegment(
                index=seg_idx,
                start_sample=start,
                end_sample=start + segment_length,
                raw_data=raw_slice.copy(),
                windowed_data=windowed.copy(),
            )
        )
        start += hop_length
        seg_idx += 1

    return segments, pad_len


def overlap_add_reconstruct(
    processed_windows: List[np.ndarray],
    original_length: int,
    pad_len: int,
    segment_length: int = 256,
    hop_length: int = 128,
    eps: float = 1e-12,
) -> np.ndarray:
    """Reconstruct continuous signal from processed segments via weighted overlap-add.

    numerator += processed_window * hann
    denominator += hann^2
    output = numerator / (denominator + eps)
    """
    window = get_hann_window(segment_length)
    total_padded_len = pad_len * 2 + original_length + segment_length

    numerator = np.zeros(total_padded_len, dtype=np.float64)
    denominator = np.zeros(total_padded_len, dtype=np.float64)

    for i, seg in enumerate(processed_windows):
        start = i * hop_length
        end = start + segment_length
        if end > total_padded_len:
            break
        # Weighted overlap-add (Section 8)
        numerator[start:end] += seg * window
        denominator[start:end] += window ** 2

    reconstructed_padded = numerator / (denominator + eps)

    # Trim reflection padding to restore exact original signal length
    reconstructed = reconstructed_padded[pad_len : pad_len + original_length]
    return reconstructed
