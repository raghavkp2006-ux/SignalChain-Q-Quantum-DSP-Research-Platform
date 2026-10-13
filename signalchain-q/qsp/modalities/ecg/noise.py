"""Synthetic and recorded noise generation and SNR-controlled mixing (Section 7)."""
import hashlib
from typing import Optional, Tuple
import numpy as np


def compute_deterministic_seed(base_seed: int, identifier: str) -> int:
    """Derive a deterministic integer seed from base_seed and an arbitrary identifier."""
    h = hashlib.sha256(f"{base_seed}:{identifier}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def generate_baseline_wander(
    n_samples: int,
    fs: float = 360.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize baseline wander (0.05 - 0.5 Hz respiration/drift component)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_samples) / fs
    # Sum of slow sinusoids with random phases
    f1, f2, f3 = 0.15, 0.3, 0.45
    phi1, phi2, phi3 = rng.uniform(0, 2 * np.pi, size=3)
    bw = (
        0.5 * np.sin(2 * np.pi * f1 * t + phi1)
        + 0.3 * np.sin(2 * np.pi * f2 * t + phi2)
        + 0.2 * np.sin(2 * np.pi * f3 * t + phi3)
    )
    return bw - np.mean(bw)


def generate_muscle_artifact(
    n_samples: int,
    fs: float = 360.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize high-frequency EMG/muscle artifact noise (20 - 150 Hz)."""
    rng = np.random.default_rng(seed)
    # High-pass or bandpass filtered Gaussian noise
    white = rng.standard_normal(n_samples)
    # 3-point moving average difference for simple high-pass emphasis
    ma = np.convolve(white, [1.0, -1.0], mode="same")
    return ma - np.mean(ma)


def generate_electrode_motion(
    n_samples: int,
    fs: float = 360.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize electrode motion artifact: sharp baseline step/drift with transient noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_samples) / fs
    step_time = rng.uniform(0.3, 0.7) * (n_samples / fs)
    transient = 0.5 * np.exp(-((t - step_time) ** 2) / (2 * (0.1 ** 2))) * np.sin(2 * np.pi * 2.0 * t)
    drift = generate_baseline_wander(n_samples, fs, seed=seed)
    em = transient + drift
    return em - np.mean(em)


def generate_powerline(
    n_samples: int,
    fs: float = 360.0,
    freq_hz: float = 50.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize 50Hz or 60Hz powerline sinusoidal interference."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_samples) / fs
    phi = rng.uniform(0, 2 * np.pi) if seed is not None else 0.0
    pl = np.sin(2 * np.pi * freq_hz * t + phi) + 0.15 * np.sin(2 * np.pi * 2 * freq_hz * t + phi)
    return pl - np.mean(pl)


def generate_white_gaussian(
    n_samples: int,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Synthesize zero-mean white Gaussian noise."""
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n_samples)
    return noise - np.mean(noise)


def get_noise_vector(
    noise_type: str,
    n_samples: int,
    fs: float = 360.0,
    seed: Optional[int] = None,
    noise_reference: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Retrieve or generate noise vector of desired type and length."""
    nt = noise_type.lower().strip()
    if noise_reference is not None and len(noise_reference) >= n_samples:
        # Extract deterministic slice from recorded noise
        rng = np.random.default_rng(seed)
        max_start = len(noise_reference) - n_samples
        start = rng.integers(0, max_start + 1) if max_start > 0 else 0
        noise = noise_reference[start : start + n_samples].copy()
        return noise - np.mean(noise)

    if nt in ("bw", "baseline_wander"):
        return generate_baseline_wander(n_samples, fs, seed=seed)
    elif nt in ("ma", "muscle_artifact"):
        return generate_muscle_artifact(n_samples, fs, seed=seed)
    elif nt in ("em", "electrode_motion"):
        return generate_electrode_motion(n_samples, fs, seed=seed)
    elif nt in ("pl50", "powerline_50hz"):
        return generate_powerline(n_samples, fs, freq_hz=50.0, seed=seed)
    elif nt in ("pl60", "powerline_60hz"):
        return generate_powerline(n_samples, fs, freq_hz=60.0, seed=seed)
    elif nt in ("wgn", "white_gaussian"):
        return generate_white_gaussian(n_samples, seed=seed)
    else:
        raise ValueError(f"Unknown noise_type: {noise_type}")


def mix_noise_at_snr(
    clean_ecg: np.ndarray,
    noise: np.ndarray,
    target_snr_db: float,
    tolerance_db: float = 0.25,
) -> Tuple[np.ndarray, float, float]:
    """Mix zero-mean noise with clean ECG to achieve exact target SNR (Section 7).

    Px = mean((x - mean(x))^2)
    Pn = mean((n - mean(n))^2)
    alpha = sqrt(Px / (Pn * 10^(SNR_target/10)))
    y = x + alpha * n

    Returns:
        noisy_ecg: x + alpha * n
        measured_snr_db: 10 * log10(Px / mean((noisy - clean)^2))
        alpha: scaling factor applied to noise
    """
    x = clean_ecg.astype(np.float64)
    n = noise.astype(np.float64)

    if len(x) != len(n):
        min_len = min(len(x), len(n))
        x = x[:min_len]
        n = n[:min_len]

    # Ensure zero-mean noise
    n = n - np.mean(n)

    p_x = np.mean((x - np.mean(x)) ** 2)
    p_n = np.mean(n ** 2)

    if p_x <= 1e-15:
        raise ValueError("Clean ECG has zero or near-zero variance.")
    if p_n <= 1e-15:
        raise ValueError("Noise vector has zero or near-zero variance.")

    alpha = np.sqrt(p_x / (p_n * (10.0 ** (target_snr_db / 10.0))))
    scaled_noise = alpha * n
    noisy_ecg = x + scaled_noise

    # Verify actual measured SNR
    noise_power_actual = np.mean((noisy_ecg - x) ** 2)
    measured_snr_db = float(10.0 * np.log10(p_x / noise_power_actual))

    if abs(measured_snr_db - target_snr_db) > tolerance_db:
        raise AssertionError(
            f"Measured SNR ({measured_snr_db:.3f} dB) exceeds tolerance of ±{tolerance_db} dB "
            f"from target ({target_snr_db:.3f} dB)"
        )

    return noisy_ecg, measured_snr_db, float(alpha)
