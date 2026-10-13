"""Evaluation metrics for ECG denoising pipelines (Section 19)."""
from typing import Optional
import numpy as np
from qsp.core.types import BenchmarkMetrics


def calculate_snr_db(clean: np.ndarray, test: np.ndarray) -> float:
    """Calculate Signal-to-Noise Ratio (SNR) in dB."""
    if len(clean) != len(test):
        min_len = min(len(clean), len(test))
        clean = clean[:min_len]
        test = test[:min_len]

    noise_residual = clean - test
    p_signal = np.sum(clean ** 2)
    p_noise = np.sum(noise_residual ** 2)

    if p_noise <= 1e-15:
        return 100.0  # clean is essentially identical
    if p_signal <= 1e-15:
        return -100.0

    return float(10.0 * np.log10(p_signal / p_noise))


def calculate_rmse(clean: np.ndarray, test: np.ndarray) -> float:
    """Calculate Root Mean Squared Error (RMSE)."""
    min_len = min(len(clean), len(test))
    return float(np.sqrt(np.mean((clean[:min_len] - test[:min_len]) ** 2)))


def calculate_mae(clean: np.ndarray, test: np.ndarray) -> float:
    """Calculate Mean Absolute Error (MAE)."""
    min_len = min(len(clean), len(test))
    return float(np.mean(np.abs(clean[:min_len] - test[:min_len])))


def calculate_prd(clean: np.ndarray, test: np.ndarray) -> float:
    """Calculate Percentage Root-Mean-Square Difference (PRD).

    PRD = 100 * ||clean - test||2 / ||clean||2
    """
    min_len = min(len(clean), len(test))
    norm_clean = np.linalg.norm(clean[:min_len])
    if norm_clean < 1e-12:
        return 0.0
    norm_diff = np.linalg.norm(clean[:min_len] - test[:min_len])
    return float(100.0 * (norm_diff / norm_clean))


def calculate_pearson_r(clean: np.ndarray, test: np.ndarray) -> float:
    """Calculate Pearson correlation coefficient r(clean, processed)."""
    min_len = min(len(clean), len(test))
    c = clean[:min_len]
    t = test[:min_len]

    std_c = np.std(c)
    std_t = np.std(t)

    if std_c < 1e-12 or std_t < 1e-12:
        return 0.0

    r = np.corrcoef(c, t)[0, 1]
    return float(np.clip(r, -1.0, 1.0))


def evaluate_signal_metrics(
    processed: np.ndarray,
    clean_reference: Optional[np.ndarray],
    noisy_input: Optional[np.ndarray] = None,
) -> BenchmarkMetrics:
    """Compute all standard waveform evaluation metrics against a clean reference."""
    if clean_reference is None:
        return BenchmarkMetrics()

    out_snr = calculate_snr_db(clean_reference, processed)
    in_snr = calculate_snr_db(clean_reference, noisy_input) if noisy_input is not None else 0.0
    snr_imp = out_snr - in_snr

    rmse = calculate_rmse(clean_reference, processed)
    mae = calculate_mae(clean_reference, processed)
    prd = calculate_prd(clean_reference, processed)
    corr = calculate_pearson_r(clean_reference, processed)

    return BenchmarkMetrics(
        input_snr_db=round(in_snr, 4),
        output_snr_db=round(out_snr, 4),
        snr_improvement_db=round(snr_imp, 4),
        rmse=round(rmse, 6),
        mae=round(mae, 6),
        prd=round(prd, 4),
        pearson_r=round(corr, 6),
    )
