"""Classical DSP baseline filters for ECG."""
from qsp.classical.bandpass import apply_butterworth_bandpass
from qsp.classical.fft_adaptive import apply_fft_adaptive_bandpass
from qsp.classical.registry import CLASSICAL_METHODS, get_classical_method, raw_passthrough
from qsp.classical.wavelet import apply_wavelet_denoising

__all__ = [
    "apply_butterworth_bandpass",
    "apply_fft_adaptive_bandpass",
    "apply_wavelet_denoising",
    "raw_passthrough",
    "CLASSICAL_METHODS",
    "get_classical_method",
]
