"""Unit and regression tests for Phase 9 & 10 dataset loaders, statistics, and oracle equivalence."""
import numpy as np
import pytest

from qsp.benchmarks.statistics import apply_holm_bonferroni, calculate_bootstrap_ci
from qsp.datasets.nstdb import load_nstdb_noise, load_nstdb_test_case
from qsp.datasets.qtdb import load_qtdb_record
from qsp.quantum.oracle import verify_oracle_equivalence


def test_nstdb_noise_loader():
    """Verify NSTDB noise loader loads calibrated noise vectors."""
    for nt in ["bw", "ma", "em"]:
        noise = load_nstdb_noise(nt, max_samples=500, seed=1448)
        assert len(noise) == 500
        assert np.all(np.isfinite(noise))
        assert np.std(noise) > 0.0


def test_nstdb_test_case_loading():
    """Verify loading NSTDB calibrated noisy records and paired clean signals."""
    clean_rec, noisy_rec, target_snr = load_nstdb_test_case("118e12", max_samples=500, seed=1448)
    assert clean_rec.record_id == "118"
    assert noisy_rec.record_id == "118e12"
    assert target_snr == 12.0
    assert len(clean_rec.signal) == len(noisy_rec.signal)
    assert noisy_rec.metadata["dataset_source"] == "nstdb"


def test_qtdb_loader_sampling_rate():
    """Verify QTDB loader sets sampling rate to 250 Hz and extracts fiducials."""
    rec = load_qtdb_record("sel100", max_samples=500, seed=1448)
    assert rec.sampling_rate_hz == 250.0
    assert rec.channel_label is not None
    assert len(rec.signal) == 500
    assert rec.metadata["dataset_source"] == "qtdb"
    assert rec.r_peaks is not None
    assert len(rec.r_peaks) > 0


def test_holm_bonferroni_correction():
    """Verify Holm-Bonferroni step-down correction properties."""
    raw_p = [0.01, 0.04, 0.03, 0.005]
    adj_p = apply_holm_bonferroni(raw_p)
    assert len(adj_p) == len(raw_p)
    # All adjusted p-values must be >= raw and <= 1.0
    for r, a in zip(raw_p, adj_p):
        assert a >= r
        assert a <= 1.0


def test_bootstrap_confidence_interval():
    """Verify bootstrap CI generates valid interval enclosing the sample median."""
    rng = np.random.default_rng(1448)
    data = rng.normal(loc=5.0, scale=1.0, size=100)
    low, high = calculate_bootstrap_ci(data, n_bootstrap=500, seed=1448)
    med = np.median(data)
    assert low <= med <= high


def test_oracle_equivalence_m16_m32():
    """Verify O1 (diagonal reference) and O2 (range) mark identical quantum states."""
    assert verify_oracle_equivalence(n_qubits=4, k_low=1, k_high=3) is True
    assert verify_oracle_equivalence(n_qubits=5, k_low=2, k_high=6) is True
