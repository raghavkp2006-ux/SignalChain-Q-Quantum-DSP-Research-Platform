"""Noisy simulation models for quantum robustness evaluations (Section 17)."""
from typing import Optional
from qiskit_aer.noise import NoiseModel, depolarizing_error


def build_depolarizing_noise_model(
    single_qubit_p: float = 0.001,
    two_qubit_p: float = 0.01,
) -> NoiseModel:
    """Construct Aer noise model with depolarizing errors on 1-qubit and 2-qubit gates."""
    noise_model = NoiseModel()

    if single_qubit_p > 0.0:
        error_1q = depolarizing_error(single_qubit_p, 1)
        noise_model.add_all_qubit_quantum_error(error_1q, ["u", "u1", "u2", "u3", "rz", "sx", "x", "h"])

    if two_qubit_p > 0.0:
        error_2q = depolarizing_error(two_qubit_p, 2)
        noise_model.add_all_qubit_quantum_error(error_2q, ["cx", "cz"])

    return noise_model
