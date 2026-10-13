"""Quantum state preparation for normalized ECG amplitudes (Section 12)."""
import time
from typing import Tuple
import numpy as np
from qiskit.circuit.library import StatePreparation
from qiskit import QuantumCircuit


def prepare_amplitude_state(
    windowed_vector: np.ndarray,
) -> Tuple[QuantumCircuit, float, float, int, int]:
    """Prepare |psi> = sum_i v_norm[i] |i> using amplitude encoding.

    Returns:
        circuit: QuantumCircuit containing state preparation
        scale: original L2 norm ||v||2
        encoding_time_ms: execution time for state preparation in ms
        encoding_depth: circuit depth of the state preparation subcircuit
        encoding_gate_count: total gate count in state preparation
    """
    m_samples = len(windowed_vector)
    n_qubits = int(np.log2(m_samples))
    if 2 ** n_qubits != m_samples:
        raise ValueError(f"Vector length {m_samples} must be a power of 2.")

    t0 = time.perf_counter()
    scale = float(np.linalg.norm(windowed_vector))

    qc = QuantumCircuit(n_qubits, name="StatePrep")

    if scale < 1e-12:
        # Trivial all-zero state
        encoding_time_ms = (time.perf_counter() - t0) * 1000.0
        return qc, 0.0, encoding_time_ms, 0, 0

    v_norm = (windowed_vector / scale).astype(np.float64)

    # Use Qiskit's StatePreparation gate
    sp_gate = StatePreparation(v_norm)
    qc.append(sp_gate, range(n_qubits))

    encoding_time_ms = (time.perf_counter() - t0) * 1000.0
    encoding_depth = qc.depth()
    encoding_gate_count = len(qc.data)

    return qc, scale, encoding_time_ms, encoding_depth, encoding_gate_count
