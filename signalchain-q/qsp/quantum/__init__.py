"""Quantum DSP modules for ECG denoising."""
from qsp.quantum.amplitude_amplification import (
    apply_amplitude_amplification,
    build_diffusion_operator,
    compute_grover_iterations,
)
from qsp.quantum.encoding import prepare_amplitude_state
from qsp.quantum.oracle import (
    build_diagonal_oracle,
    build_range_oracle,
    verify_oracle_equivalence,
)
from qsp.quantum.pipeline import run_quantum_ecg_pipeline
from qsp.quantum.qft import build_iqft_circuit, build_qft_circuit
from qsp.quantum.reconstruction import reconstruct_window_from_statevector
from qsp.quantum.resource_metrics import analyze_circuit_resources

__all__ = [
    "prepare_amplitude_state",
    "build_qft_circuit",
    "build_iqft_circuit",
    "build_diagonal_oracle",
    "build_range_oracle",
    "verify_oracle_equivalence",
    "build_diffusion_operator",
    "compute_grover_iterations",
    "apply_amplitude_amplification",
    "reconstruct_window_from_statevector",
    "analyze_circuit_resources",
    "run_quantum_ecg_pipeline",
]
