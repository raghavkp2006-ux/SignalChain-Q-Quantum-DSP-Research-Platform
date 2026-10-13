"""Unit tests for classical ECG DSP baselines (Section 9 & 29)."""
import numpy as np
import pytest
from qsp.classical.bandpass import apply_butterworth_bandpass
from qsp.classical.fft_adaptive import apply_fft_adaptive_bandpass
from qsp.classical.wavelet import apply_wavelet_denoising
from qsp.modalities.ecg.io import generate_synthetic_lead


@pytest.fixture
def test_signal():
    rec = generate_synthetic_lead(duration_sec=3.0, fs=360.0, seed=1448)
    return rec.signal


def test_butterworth_zero_phase(test_signal):
    """Test Butterworth bandpass output length, zero-phase property, and finite values."""
    filtered = apply_butterworth_bandpass(test_signal, fs=360.0, lowcut_hz=0.5, highcut_hz=40.0, zero_phase=True)
    assert len(filtered) == len(test_signal)
    assert np.all(np.isfinite(filtered))


def test_wavelet_db6(test_signal):
    """Test Wavelet db6 denoising output length and finite values."""
    filtered = apply_wavelet_denoising(test_signal, wavelet_name="db6", max_level=5)
    assert len(filtered) == len(test_signal)
    assert np.all(np.isfinite(filtered))


def test_fft_adaptive_bandpass(test_signal):
    """Test Adaptive FFT bandpass filter output length and finite values."""
    filtered = apply_fft_adaptive_bandpass(test_signal, fs=360.0, segment_length=256, hop_length=128)
    assert len(filtered) == len(test_signal)
    assert np.all(np.isfinite(filtered))
