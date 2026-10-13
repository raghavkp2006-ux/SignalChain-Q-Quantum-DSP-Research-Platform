"""Wavelet ECG denoising baseline (Section 9, C2)."""
import numpy as np
import pywt


def apply_wavelet_denoising(
    ecg: np.ndarray,
    wavelet_name: str = "db6",
    max_level: int = 5,
    threshold_mode: str = "soft",
    mad_scale: float = 0.6745,
) -> np.ndarray:
    """Wavelet denoising using Daubechies 6, VisuShrink universal threshold, and MAD noise scale."""
    n = len(ecg)
    wavelet = pywt.Wavelet(wavelet_name)
    level = min(max_level, pywt.dwt_max_level(n, wavelet.dec_len))
    if level < 1:
        return ecg.copy()

    coeffs = pywt.wavedec(ecg, wavelet, level=level)

    # Estimate noise standard deviation sigma using Median Absolute Deviation (MAD) of first detail level
    detail_coeffs = coeffs[-1]
    sigma = float(np.median(np.abs(detail_coeffs)) / mad_scale)

    # Universal threshold T = sigma * sqrt(2 * ln(N))
    threshold = float(sigma * np.sqrt(2.0 * np.log(n)))

    # Apply soft thresholding to all detail coefficients (coeffs[1:])
    new_coeffs = [coeffs[0]]
    for d in coeffs[1:]:
        new_coeffs.append(pywt.threshold(d, value=threshold, mode=threshold_mode))

    reconstructed = pywt.waverec(new_coeffs, wavelet)
    # Trim to exact original length
    return reconstructed[:n]
