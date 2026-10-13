"""Waveform reconstruction from ideal quantum statevectors (Section 16)."""
import time
from typing import Tuple
import numpy as np
from qiskit.quantum_info import Statevector


def reconstruct_window_from_statevector(
    statevector: Statevector,
    original_scale: float,
    imag_tolerance: float = 1e-8,
) -> Tuple[np.ndarray, float, float]:
    """Extract waveform amplitudes from quantum statevector and rescale by original L2 norm.

    Returns:
        processed_window: 1D real numpy array
        max_imag_residual: maximum absolute imaginary component
        reconstruction_time_ms: execution time in ms
    """
    t0 = time.perf_counter()

    if original_scale < 1e-12:
        reconstruction_time_ms = (time.perf_counter() - t0) * 1000.0
        return np.zeros(len(statevector), dtype=np.float64), 0.0, reconstruction_time_ms

    raw_amplitudes = np.array(statevector.data, dtype=np.complex128)
    max_imag = float(np.max(np.abs(np.imag(raw_amplitudes))))

    # Extract real component and rescale by original L2 norm
    real_amplitudes = np.real(raw_amplitudes)
    processed_window = real_amplitudes * original_scale

    reconstruction_time_ms = (time.perf_counter() - t0) * 1000.0
    return processed_window, max_imag, reconstruction_time_ms
