"""Data types, schemas, and resource metric containers for SignalChain-Q."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class ECGSegment:
    """A windowed segment extracted from an ECG lead."""
    index: int
    start_sample: int
    end_sample: int
    raw_data: np.ndarray
    windowed_data: np.ndarray
    activity_score: float = 0.0
    normalized_activity: float = 0.0
    adaptive_highcut_hz: float = 40.0
    k_low: int = 0
    k_high: int = 0
    marked_count: int = 0


@dataclass
class ECGRecord:
    """An ECG signal record with metadata."""
    signal: np.ndarray
    sampling_rate_hz: float
    record_id: str
    channel_index: int = 0
    channel_label: str = "MLII"
    clean_reference: Optional[np.ndarray] = None
    r_peaks: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantumResourceMetrics:
    """Section 18 of Execution Plan: Complete quantum resource accounting."""
    segment_length: int = 0
    signal_qubits: int = 0
    ancilla_qubits: int = 0
    total_qubits: int = 0
    stateprep_depth: int = 0
    algorithm_depth: int = 0
    total_logical_depth: int = 0
    transpiled_depth: int = 0
    total_gate_count: int = 0
    single_qubit_gate_count: int = 0
    two_qubit_gate_count: int = 0
    cx_count: int = 0
    qft_depth: int = 0
    oracle_depth: int = 0
    grover_depth: int = 0
    iqft_depth: int = 0
    grover_iterations: int = 0
    transpile_optimization_level: int = 3
    simulator_backend: str = "aer_statevector"
    stateprep_time_ms: float = 0.0
    circuit_build_time_ms: float = 0.0
    transpile_time_ms: float = 0.0
    simulation_time_ms: float = 0.0
    reconstruction_time_ms: float = 0.0
    total_pipeline_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class BenchmarkMetrics:
    """Evaluation metrics for an ECG denoising run (Section 19)."""
    input_snr_db: float = 0.0
    output_snr_db: float = 0.0
    snr_improvement_db: float = 0.0
    rmse: float = 0.0
    mae: float = 0.0
    prd: float = 0.0
    pearson_r: float = 0.0
    r_peak_sensitivity: Optional[float] = None
    r_peak_positive_predictivity: Optional[float] = None
    r_peak_f1: Optional[float] = None
    median_absolute_r_peak_timing_error_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class FilterResult:
    """Result of running any classical or quantum DSP pipeline."""
    method_name: str
    processed_signal: np.ndarray
    original_signal: np.ndarray
    clean_reference: Optional[np.ndarray] = None
    sampling_rate_hz: float = 360.0
    metrics: BenchmarkMetrics = field(default_factory=BenchmarkMetrics)
    stage_timings_ms: Dict[str, float] = field(default_factory=dict)
    quantum_resources: Optional[QuantumResourceMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
