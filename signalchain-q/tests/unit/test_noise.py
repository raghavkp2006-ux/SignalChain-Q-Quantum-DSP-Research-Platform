"""Unit tests for synthetic noise generation and SNR mixing (Section 7 & 29)."""
import numpy as np
import pytest
from qsp.modalities.ecg.io import generate_synthetic_lead
from qsp.modalities.ecg.noise import (
    compute_deterministic_seed,
    get_noise_vector,
    mix_noise_at_snr,
)


@pytest.fixture
def clean_ecg():
    rec = generate_synthetic_lead(duration_sec=5.0, fs=360.0, seed=1448)
    return rec.signal


@pytest.mark.parametrize("target_snr", [-6.0, 0.0, 6.0, 12.0, 18.0, 24.0])
@pytest.mark.parametrize("noise_type", ["bw", "ma", "em", "wgn"])
def test_snr_mixing_tolerance(clean_ecg, target_snr, noise_type):
    """Test target SNR tolerance: abs(measured_snr_db - target_snr_db) <= 0.25 dB."""
    n_samples = len(clean_ecg)
    noise = get_noise_vector(noise_type, n_samples=n_samples, fs=360.0, seed=1448)
    noisy_sig, measured_snr, alpha = mix_noise_at_snr(
        clean_ecg=clean_ecg,
        noise=noise,
        target_snr_db=target_snr,
        tolerance_db=0.25,
    )

    err = abs(measured_snr - target_snr)
    assert err <= 0.25, f"SNR error {err:.4f} dB exceeds 0.25 dB tolerance for target {target_snr}"
    assert not np.isnan(noisy_sig).any()
    assert not np.isinf(noisy_sig).any()


def test_deterministic_noise_rerun(clean_ecg):
    """Deterministic rerun with same seed must yield bit-identical arrays."""
    noise1 = get_noise_vector("bw", len(clean_ecg), fs=360.0, seed=1448)
    noise2 = get_noise_vector("bw", len(clean_ecg), fs=360.0, seed=1448)
    np.testing.assert_array_equal(noise1, noise2)

    noisy1, snr1, _ = mix_noise_at_snr(clean_ecg, noise1, target_snr_db=12.0)
    noisy2, snr2, _ = mix_noise_at_snr(clean_ecg, noise2, target_snr_db=12.0)
    np.testing.assert_array_equal(noisy1, noisy2)
    assert snr1 == snr2


def test_different_pair_ids_yield_different_noise(clean_ecg):
    """Different pair IDs must use different deterministic seeds."""
    seed_a = compute_deterministic_seed(1448, "pair_001")
    seed_b = compute_deterministic_seed(1448, "pair_002")
    assert seed_a != seed_b

    noise_a = get_noise_vector("bw", len(clean_ecg), seed=seed_a)
    noise_b = get_noise_vector("bw", len(clean_ecg), seed=seed_b)
    assert not np.array_equal(noise_a, noise_b)
