"""Core types, framing, metrics, timing, and reproducibility utilities for QSP."""
from qsp.core.types import (
    ECGRecord,
    ECGSegment,
    FilterResult,
    QuantumResourceMetrics,
    BenchmarkMetrics,
)
from qsp.core.framing import segment_signal, overlap_add_reconstruct
from qsp.core.metrics import (
    calculate_snr_db,
    calculate_rmse,
    calculate_mae,
    calculate_prd,
    calculate_pearson_r,
    evaluate_signal_metrics,
)
from qsp.core.timing import StageTimer
from qsp.core.reproducibility import (
    seed_everything,
    capture_environment_metadata,
    compute_config_hash,
)

__all__ = [
    "ECGRecord",
    "ECGSegment",
    "FilterResult",
    "QuantumResourceMetrics",
    "BenchmarkMetrics",
    "segment_signal",
    "overlap_add_reconstruct",
    "calculate_snr_db",
    "calculate_rmse",
    "calculate_mae",
    "calculate_prd",
    "calculate_pearson_r",
    "evaluate_signal_metrics",
    "StageTimer",
    "seed_everything",
    "capture_environment_metadata",
    "compute_config_hash",
]
