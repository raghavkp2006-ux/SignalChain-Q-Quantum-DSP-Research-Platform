"""Registry for classical ECG baseline filtering methods (Section 9 & Section 20)."""
from typing import Any, Callable, Dict
import numpy as np
from qsp.classical.bandpass import apply_butterworth_bandpass
from qsp.classical.fft_adaptive import apply_fft_adaptive_bandpass
from qsp.classical.wavelet import apply_wavelet_denoising


def raw_passthrough(ecg: np.ndarray, **kwargs) -> np.ndarray:
    """C0: raw unfiltered baseline."""
    return ecg.copy()


CLASSICAL_METHODS: Dict[str, Callable[..., np.ndarray]] = {
    "raw": raw_passthrough,
    "butterworth_bandpass": apply_butterworth_bandpass,
    "wavelet_db6": apply_wavelet_denoising,
    "fft_adaptive_bandpass": apply_fft_adaptive_bandpass,
}


def get_classical_method(name: str) -> Callable[..., np.ndarray]:
    """Retrieve classical filter callable by identifier."""
    key = name.lower().strip()
    if key not in CLASSICAL_METHODS:
        raise ValueError(
            f"Unknown classical method '{name}'. Available: {list(CLASSICAL_METHODS.keys())}"
        )
    return CLASSICAL_METHODS[key]
