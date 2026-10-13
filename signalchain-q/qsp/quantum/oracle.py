"""Quantum phase oracle implementations for ECG bandpass filtering (Section 14)."""
from typing import List
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qsp.core.frequency_mask import get_marked_frequencies_mask


def build_diagonal_oracle(
    n_qubits: int,
    k_low: int,
    k_high: int,
) -> QuantumCircuit:
    """O1 — diagonal_reference: phase[k] = -1 if marked(k) else +1 (Section 14)."""
    m_states = 2 ** n_qubits
    mask = get_marked_frequencies_mask(m_states, k_low, k_high)

    phases = np.ones(m_states, dtype=np.float64)
    phases[mask] = -1.0

    qc = QuantumCircuit(n_qubits, name="DiagonalOracle")
    qc.append(DiagonalGate(phases.tolist()), range(n_qubits))
    return qc


def build_range_oracle(
    n_qubits: int,
    k_low: int,
    k_high: int,
) -> QuantumCircuit:
    """O2 — range_oracle: structured gate-level phase marking for marked frequency ranges."""
    m_states = 2 ** n_qubits
    mask = get_marked_frequencies_mask(m_states, k_low, k_high)
    marked_indices = np.where(mask)[0].tolist()

    qc = QuantumCircuit(n_qubits, name="RangeOracle")

    # Gate-level multi-controlled phase flip for marked basis states
    # Phase flip on state |k>: X on qubits where bit is 0, MCZ across all qubits, then X again
    for k in marked_indices:
        bin_str = format(k, f"0{n_qubits}b")[::-1]  # Qiskit qubit 0 is LSB
        for q_idx, bit in enumerate(bin_str):
            if bit == "0":
                qc.x(q_idx)

        # Multi-controlled Z on target (last qubit)
        if n_qubits == 1:
            qc.z(0)
        else:
            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)

        for q_idx, bit in enumerate(bin_str):
            if bit == "0":
                qc.x(q_idx)

    return qc


def verify_oracle_equivalence(
    n_qubits: int,
    k_low: int,
    k_high: int,
) -> bool:
    """Verify that O1 (diagonal) and O2 (range) mark identical states for M=16 or M=32."""
    from qiskit.quantum_info import Operator
    op_diag = Operator(build_diagonal_oracle(n_qubits, k_low, k_high))
    op_range = Operator(build_range_oracle(n_qubits, k_low, k_high))
    return op_diag.equiv(op_range)
