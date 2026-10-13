"""Quantum Fourier Transform (QFT) and Inverse QFT circuits (Section 13)."""
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate


def build_qft_circuit(n_qubits: int) -> QuantumCircuit:
    """Build QFT circuit on n_qubits."""
    qc = QuantumCircuit(n_qubits, name="QFT")
    qc.append(QFTGate(n_qubits), range(n_qubits))
    return qc


def build_iqft_circuit(n_qubits: int) -> QuantumCircuit:
    """Build Inverse QFT (IQFT) circuit on n_qubits."""
    qc = QuantumCircuit(n_qubits, name="IQFT")
    qc.append(QFTGate(n_qubits).inverse(), range(n_qubits))
    return qc
