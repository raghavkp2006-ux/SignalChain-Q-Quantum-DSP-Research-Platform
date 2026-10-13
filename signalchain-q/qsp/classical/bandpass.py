"""Classical Butterworth ECG bandpass filter baseline (Section 9, C1)."""
from typing import Optional
import numpy as np
from scipy import signal


def apply_butterworth_bandpass(
    ecg: np.ndarray,
    fs: float = 360.0,
    order: int = 4,
    lowcut_hz: float = 0.5,
    highcut_hz: float = 40.0,
    zero_phase: bool = True,
    notch_hz: Optional[float] = None,
    notch_q: float = 30.0,
) -> np.ndarray:
    """Butterworth bandpass filter using Second-Order Sections (SOS).

    scipy.signal.butter(order, [low, high], btype='bandpass', output='sos')
    scipy.signal.sosfiltfilt(...)
    """
    nyq = 0.5 * fs
    low = lowcut_hz / nyq
    high = highcut_hz / nyq

    # Bound frequencies within Nyquist range
    low = max(0.001, min(low, 0.99))
    high = max(low + 0.001, min(high, 0.99))

    sos = signal.butter(order, [low, high], btype="bandpass", output="sos")

    if zero_phase:
        filtered = signal.sosfiltfilt(sos, ecg)
    else:
        filtered = signal.sosfilt(sos, ecg)

    # Optional powerline notch filter
    if notch_hz is not None and notch_hz < nyq:
        w0 = notch_hz / nyq
        b_notch, a_notch = signal.iirnotch(w0, notch_q)
        if zero_phase:
            filtered = signal.filtfilt(b_notch, a_notch, filtered)
        else:
            filtered = signal.lfilter(b_notch, a_notch, filtered)

    return filtered
