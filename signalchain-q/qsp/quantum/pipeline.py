"""QFT + Adaptive Bandpass Phase Oracle + Grover Amplification + IQFT Pipeline (Section 11)."""
import time
from typing import List, Optional
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import StatePreparation, QFTGate
from qiskit.quantum_info import Statevector

from qsp.core.framing import overlap_add_reconstruct, segment_signal
from qsp.core.types import FilterResult, QuantumResourceMetrics
from qsp.modalities.ecg.preprocessing import compute_adaptive_cutoffs_for_segments
from qsp.quantum.amplitude_amplification import (
    apply_amplitude_amplification,
    compute_grover_iterations,
)
from qsp.quantum.encoding import prepare_amplitude_state
from qsp.quantum.oracle import build_diagonal_oracle, build_range_oracle
from qsp.quantum.qft import build_iqft_circuit, build_qft_circuit
from qsp.quantum.reconstruction import reconstruct_window_from_statevector
from qsp.quantum.resource_metrics import analyze_circuit_resources


def run_quantum_ecg_pipeline(
    ecg: np.ndarray,
    fs: float = 360.0,
    segment_length: int = 256,
    hop_length: int = 128,
    f_low_hz: float = 0.5,
    f_high_min_hz: float = 25.0,
    f_high_max_hz: float = 45.0,
    oracle_type: str = "diagonal_reference",
    grover_iterations_cap: int = 3,
    fixed_grover_iterations: Optional[int] = None,
    transpile_optimization_level: int = 3,
    profile_resources: bool = True,
) -> FilterResult:
    """Execute Section 11 Quantum DSP pipeline:

    ECG segment -> Hann window -> StatePreparation -> QFT -> Oracle -> Grover -> IQFT
    -> Statevector reconstruction -> Rescale -> Weighted overlap-add.
    """
    total_start = time.perf_counter()
    orig_len = len(ecg)

    # 1. Segmentation
    segments, pad_len = segment_signal(ecg, segment_length=segment_length, hop_length=hop_length)

    # 2. Adaptive activity & frequency marking
    compute_adaptive_cutoffs_for_segments(
        segments=segments,
        fs=fs,
        segment_length=segment_length,
        f_low_hz=f_low_hz,
        f_high_min_hz=f_high_min_hz,
        f_high_max_hz=f_high_max_hz,
    )

    n_qubits = int(np.log2(segment_length))
    processed_windows: List[np.ndarray] = []

    # Aggregated quantum resource timers and metrics
    total_sp_time_ms = 0.0
    total_build_time_ms = 0.0
    total_sim_time_ms = 0.0
    total_rec_time_ms = 0.0
    total_transpile_time_ms = 0.0

    last_resource_metrics = QuantumResourceMetrics(
        segment_length=segment_length,
        signal_qubits=n_qubits,
        ancilla_qubits=0,
        total_qubits=n_qubits,
        transpile_optimization_level=transpile_optimization_level,
        simulator_backend="aer_statevector",
    )

    sample_circuit_analyzed = False

    for seg in segments:
        xw = seg.windowed_data
        norm_val = float(np.linalg.norm(xw))

        if norm_val < 1e-12:
            processed_windows.append(np.zeros(segment_length, dtype=np.float64))
            continue

        # Stage A: State preparation
        sp_qc, scale, sp_ms, sp_depth, sp_gates = prepare_amplitude_state(xw)
        total_sp_time_ms += sp_ms

        # Stage B: Circuit assembly (QFT -> Oracle -> Grover -> IQFT)
        t_b0 = time.perf_counter()
        qc = QuantumCircuit(n_qubits, name=f"QSP_Seg{seg.index}")
        qc.append(sp_qc.to_instruction(), range(n_qubits))

        # QFT
        qft_gate = QFTGate(n_qubits)
        qc.append(qft_gate, range(n_qubits))

        # Oracle
        if oracle_type == "range_oracle":
            oracle_qc = build_range_oracle(n_qubits, seg.k_low, seg.k_high)
        else:
            oracle_qc = build_diagonal_oracle(n_qubits, seg.k_low, seg.k_high)

        # Amplitude amplification
        num_grover = compute_grover_iterations(
            m_states=segment_length,
            marked_count=seg.marked_count,
            iteration_cap=grover_iterations_cap,
            fixed_iterations=fixed_grover_iterations,
        )
        if num_grover > 0:
            apply_amplitude_amplification(qc, oracle_qc, n_qubits, num_grover)
        else:
            # Oracle phase flip alone
            qc.append(oracle_qc.to_instruction(), range(n_qubits))

        # IQFT
        qc.append(qft_gate.inverse(), range(n_qubits))
        total_build_time_ms += (time.perf_counter() - t_b0) * 1000.0

        # Optional resource analysis on representative segment
        if profile_resources and not sample_circuit_analyzed:
            _, res_counts, tr_ms = analyze_circuit_resources(
                circuit=qc,
                optimization_level=transpile_optimization_level,
            )
            total_transpile_time_ms += tr_ms
            last_resource_metrics.stateprep_depth = sp_depth
            last_resource_metrics.qft_depth = qft_gate.definition.depth() if qft_gate.definition else n_qubits
            last_resource_metrics.oracle_depth = oracle_qc.depth()
            last_resource_metrics.grover_iterations = num_grover
            last_resource_metrics.total_logical_depth = qc.depth()
            last_resource_metrics.algorithm_depth = qc.depth() - sp_depth
            last_resource_metrics.transpiled_depth = res_counts["transpiled_depth"]
            last_resource_metrics.total_gate_count = res_counts["total_gate_count"]
            last_resource_metrics.single_qubit_gate_count = res_counts["single_qubit_gate_count"]
            last_resource_metrics.two_qubit_gate_count = res_counts["two_qubit_gate_count"]
            last_resource_metrics.cx_count = res_counts["cx_count"]
            sample_circuit_analyzed = True

        # Stage C: Ideal Statevector simulation
        t_s0 = time.perf_counter()
        sv = Statevector(qc)
        total_sim_time_ms += (time.perf_counter() - t_s0) * 1000.0

        # Stage D: Reconstruction
        win_rec, max_imag, rec_ms = reconstruct_window_from_statevector(sv, scale)
        total_rec_time_ms += rec_ms
        processed_windows.append(win_rec)

    # 3. Overlap-add reconstruction
    reconstructed = overlap_add_reconstruct(
        processed_windows=processed_windows,
        original_length=orig_len,
        pad_len=pad_len,
        segment_length=segment_length,
        hop_length=hop_length,
    )

    total_pipeline_time_ms = (time.perf_counter() - total_start) * 1000.0

    last_resource_metrics.stateprep_time_ms = round(total_sp_time_ms, 3)
    last_resource_metrics.circuit_build_time_ms = round(total_build_time_ms, 3)
    last_resource_metrics.transpile_time_ms = round(total_transpile_time_ms, 3)
    last_resource_metrics.simulation_time_ms = round(total_sim_time_ms, 3)
    last_resource_metrics.reconstruction_time_ms = round(total_rec_time_ms, 3)
    last_resource_metrics.total_pipeline_time_ms = round(total_pipeline_time_ms, 3)

    return FilterResult(
        method_name="qft_grover_ecg_adaptive",
        processed_signal=reconstructed,
        original_signal=ecg,
        sampling_rate_hz=fs,
        stage_timings_ms={
            "stateprep_ms": total_sp_time_ms,
            "circuit_build_ms": total_build_time_ms,
            "simulation_ms": total_sim_time_ms,
            "reconstruction_ms": total_rec_time_ms,
            "total_ms": total_pipeline_time_ms,
        },
        quantum_resources=last_resource_metrics,
    )
