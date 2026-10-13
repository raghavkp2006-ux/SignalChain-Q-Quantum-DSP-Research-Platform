"""Datasets and built-in demo examples API endpoint (Section 25 & 27)."""
from typing import List
from fastapi import APIRouter
from backend.app.schemas.ecg import ECGExampleItem
from qsp.modalities.ecg.io import generate_synthetic_lead
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr

router = APIRouter()


@router.get("/ecg/examples")
def get_ecg_examples():
    """Return list of interactive demo ECG traces for quick browser testing."""
    clean_rec = generate_synthetic_lead(duration_sec=3.0, fs=360.0, heart_rate_bpm=72.0, seed=1448)
    clean_sig = clean_rec.signal

    # Example 1: Clean Normal Sinus Rhythm
    ex1 = {
        "example_id": "clean_nsr",
        "name": "Clean Normal Sinus Rhythm",
        "description": "Synthetic 3-second lead II ECG at 360 Hz with normal P-QRS-T morphology.",
        "sampling_rate_hz": 360.0,
        "duration_sec": 3.0,
        "signal": clean_sig.tolist(),
        "clean_reference": clean_sig.tolist(),
    }

    # Example 2: Baseline Wander Noise (0 dB SNR)
    bw_noise = get_noise_vector("bw", len(clean_sig), fs=360.0, seed=1448)
    noisy_bw, _, _ = mix_noise_at_snr(clean_sig, bw_noise, target_snr_db=0.0)
    ex2 = {
        "example_id": "noisy_bw_0db",
        "name": "ECG + Baseline Wander (0 dB SNR)",
        "description": "Normal sinus rhythm corrupted with severe respiration/patient motion drift (0.15 - 0.45 Hz).",
        "sampling_rate_hz": 360.0,
        "duration_sec": 3.0,
        "signal": noisy_bw.tolist(),
        "clean_reference": clean_sig.tolist(),
    }

    # Example 3: Muscle Artifact Noise (6 dB SNR)
    ma_noise = get_noise_vector("ma", len(clean_sig), fs=360.0, seed=1449)
    noisy_ma, _, _ = mix_noise_at_snr(clean_sig, ma_noise, target_snr_db=6.0)
    ex3 = {
        "example_id": "noisy_ma_6db",
        "name": "ECG + Muscle Artifact (6 dB SNR)",
        "description": "ECG corrupted with high-frequency electromyographic (EMG) muscle noise.",
        "sampling_rate_hz": 360.0,
        "duration_sec": 3.0,
        "signal": noisy_ma.tolist(),
        "clean_reference": clean_sig.tolist(),
    }

    return {"examples": [ex1, ex2, ex3]}
