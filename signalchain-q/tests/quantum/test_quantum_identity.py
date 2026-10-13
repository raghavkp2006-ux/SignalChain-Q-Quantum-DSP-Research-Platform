"""Quantum identity reconstruction tests (Section 13 & 29)."""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate, StatePreparation
from qiskit.quantum_info import Statevector, state_fidelity


@pytest.mark.parametrize("m_size", [16, 32, 64, 128, 256])
def test_qft_iqft_identity_fidelity(m_size):
    """Test StatePreparation -> QFT -> IQFT fidelity >= 0.999999999 (Section 13)."""
    np.random.seed(1448 + m_size)
    n_qubits = int(np.log2(m_size))

    v = np.random.randn(m_size)
    v /= np.linalg.norm(v)

    qc = QuantumCircuit(n_qubits)
    qc.append(StatePreparation(v), range(n_qubits))
    qc.append(QFTGate(n_qubits), range(n_qubits))
    qc.append(QFTGate(n_qubits).inverse(), range(n_qubits))

    sv_out = Statevector(qc)
    sv_in = Statevector(v)

    fid = state_fidelity(sv_in, sv_out)
    assert fid >= 0.999999999, f"Fidelity {fid} for M={m_size} is below 0.999999999 threshold."


def test_statevector_amplitude_reconstruction():
    """Verify that ideal Statevector reconstruction reproduces original normalized signal."""
    np.random.seed(1448)
    v = np.random.randn(16)
    scale = float(np.linalg.norm(v))
    v_norm = v / scale

    qc = QuantumCircuit(4)
    qc.append(StatePreparation(v_norm), range(4))

    sv = Statevector(qc)
    amps = np.real(np.array(sv.data))
    reconstructed = amps * scale

    np.testing.assert_allclose(v, reconstructed, atol=1e-12)
