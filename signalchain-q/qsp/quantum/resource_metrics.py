"""Quantum circuit profiling and resource metrics accounting (Section 18)."""
import time
from typing import Dict, Tuple
from qiskit import QuantumCircuit, transpile
from qsp.core.types import QuantumResourceMetrics


def analyze_circuit_resources(
    circuit: QuantumCircuit,
    optimization_level: int = 3,
    backend_name: str = "aer_statevector",
) -> Tuple[QuantumCircuit, Dict[str, int], float]:
    """Transpile circuit and extract logical vs transpiled gate metrics.

    Returns:
        transpiled_circuit
        metrics_dict
        transpile_time_ms
    """
    t0 = time.perf_counter()
    transpiled = transpile(circuit, optimization_level=optimization_level)
    transpile_time_ms = (time.perf_counter() - t0) * 1000.0

    ops = transpiled.count_ops()
    total_gates = sum(ops.values())
    cx_count = ops.get("cx", 0)

    # In transpiled standard basis (e.g. u3, cx or sx, x, rz, cx)
    two_qubit_gates = 0
    single_qubit_gates = 0
    for instr in transpiled.data:
        q_count = len(instr.qubits)
        if q_count == 1:
            single_qubit_gates += 1
        elif q_count >= 2:
            two_qubit_gates += 1

    counts = {
        "transpiled_depth": transpiled.depth(),
        "total_gate_count": total_gates,
        "single_qubit_gate_count": single_qubit_gates,
        "two_qubit_gate_count": two_qubit_gates,
        "cx_count": cx_count,
    }

    return transpiled, counts, transpile_time_ms
