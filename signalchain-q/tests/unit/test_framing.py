"""Unit tests for segmentation and weighted overlap-add reconstruction (Section 8)."""
import numpy as np
import pytest
from qsp.core.framing import overlap_add_reconstruct, segment_signal


def test_segment_length_power_of_two():
    """Only powers of two allowed for quantum processing."""
    sig = np.random.randn(500)
    with pytest.raises(ValueError, match="must be a power of two"):
        segment_signal(sig, segment_length=200, hop_length=100)


def test_identity_overlap_add_reconstruction():
    """Identity test: windowing and weighted overlap-add without filtering must achieve RMSE < 1e-8."""
    np.random.seed(1448)
    n_samples = 1000
    orig = np.sin(np.linspace(0, 10 * np.pi, n_samples)) + 0.5 * np.cos(np.linspace(0, 30 * np.pi, n_samples))

    segment_length = 256
    hop_length = 128

    segments, pad_len = segment_signal(orig, segment_length=segment_length, hop_length=hop_length)
    # Identity: processed windows are the windowed analysis frames xw = x * hann
    windowed_windows = [seg.windowed_data for seg in segments]

    reconstructed = overlap_add_reconstruct(
        processed_windows=windowed_windows,
        original_length=n_samples,
        pad_len=pad_len,
        segment_length=segment_length,
        hop_length=hop_length,
    )

    # Exclude boundary samples from reflection transition
    interior_orig = orig[50:-50]
    interior_rec = reconstructed[50:-50]

    rmse = np.sqrt(np.mean((interior_orig - interior_rec) ** 2))
    assert rmse < 1e-8, f"Identity reconstruction RMSE {rmse} exceeds 1e-8 threshold!"
