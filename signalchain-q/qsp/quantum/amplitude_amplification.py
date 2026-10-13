"""Grover amplitude amplification and diffusion operator for QSP (Section 15)."""
import math
from typing import Optional
from qiskit import QuantumCircuit


def build_diffusion_operator(n_qubits: int) -> QuantumCircuit:
    """Build standard Grover diffusion operator: 2|s><s| - I."""
    qc = QuantumCircuit(n_qubits, name="Diffusion")

    # H on all qubits
    qc.h(range(n_qubits))

    # X on all qubits
    qc.x(range(n_qubits))

    # Multi-controlled Z on target (last qubit)
    if n_qubits == 1:
        qc.z(0)
    else:
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)

    # X on all qubits
    qc.x(range(n_qubits))

    # H on all qubits
    qc.h(range(n_qubits))

    return qc


def compute_grover_iterations(
    m_states: int,
    marked_count: int,
    mode: str = "estimated_capped",
    iteration_cap: int = 3,
    fixed_iterations: Optional[int] = None,
) -> int:
    """Calculate optimal or capped Grover iterations (Section 15).

    r_est = floor((pi/4) * sqrt(M / max(L, 1)))
    """
    if fixed_iterations is not None:
        return max(0, int(fixed_iterations))

    if marked_count <= 0 or marked_count >= m_states:
        return 0

    r_est = int(math.floor((math.pi / 4.0) * math.sqrt(m_states / max(marked_count, 1))))

    if mode == "estimated_capped":
        return max(0, min(r_est, iteration_cap))
    elif mode == "exact_estimated":
        return max(0, r_est)
    else:
        return max(0, min(r_est, iteration_cap))


def apply_amplitude_amplification(
    circuit: QuantumCircuit,
    oracle_circuit: QuantumCircuit,
    n_qubits: int,
    iterations: int,
) -> None:
    """Append Grover iterations (oracle + diffusion) to the target circuit in-place."""
    if iterations <= 0:
        return

    diffusion = build_diffusion_operator(n_qubits)

    for _ in range(iterations):
        circuit.append(oracle_circuit.to_instruction(), range(n_qubits))
        circuit.append(diffusion.to_instruction(), range(n_qubits))
