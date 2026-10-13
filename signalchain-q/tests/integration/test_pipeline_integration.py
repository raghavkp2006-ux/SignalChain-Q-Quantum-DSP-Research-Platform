"""Integration test: one deterministic ECG pair across all 5 required methods (Section 29)."""
import numpy as np
import pytest
from qsp.benchmarks.runner import REQUIRED_METHODS
from qsp.modalities.ecg.io import generate_synthetic_lead
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr
from qsp.modalities.ecg.pipeline import run_ecg_pipeline


def test_five_methods_integration():
    """Verify all 5 required methods execute on identical noisy input and clean reference."""
    clean_rec = generate_synthetic_lead(duration_sec=2.0, fs=360.0, seed=1448)
    clean_sig = clean_rec.signal
    fs = clean_rec.sampling_rate_hz

    # Mix 6 dB baseline wander noise
    noise_vec = get_noise_vector("bw", len(clean_sig), fs=fs, seed=1448)
    noisy_sig, _, _ = mix_noise_at_snr(clean_sig, noise_vec, target_snr_db=6.0)

    for method in REQUIRED_METHODS:
        res = run_ecg_pipeline(
            signal=noisy_sig,
            method=method,
            fs=fs,
            clean_reference=clean_sig,
        )

        assert res.method_name == method
        assert len(res.processed_signal) == len(clean_sig)
        assert np.all(np.isfinite(res.processed_signal))
        assert res.metrics.output_snr_db is not None
        assert res.stage_timings_ms is not None

        if method == "qft_grover_ecg_adaptive":
            assert res.quantum_resources is not None
            assert res.quantum_resources.total_qubits == 8  # log2(256) = 8 qubits
            assert res.quantum_resources.stateprep_time_ms >= 0.0
