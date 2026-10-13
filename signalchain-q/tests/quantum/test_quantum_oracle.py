"""Quantum oracle correctness and equivalence tests (Section 14 & 29)."""
import pytest
from qsp.modalities.ecg.preprocessing import get_marked_frequencies_mask
from qsp.quantum.oracle import verify_oracle_equivalence


def test_marked_frequency_symmetry_and_dc_unmarked():
    """Verify frequency bins are symmetric and DC (k=0) is unmarked."""
    mask = get_marked_frequencies_mask(segment_length=256, k_low=2, k_high=20)
    assert not mask[0], "DC bin (k=0) must be unmarked!"

    # Symmetric check: mask[k] == mask[M - k] for 1 <= k < M // 2
    for k in range(1, 128):
        assert mask[k] == mask[256 - k], f"Asymmetry found at k={k}"


@pytest.mark.parametrize("m_size, n_qubits", [(16, 4), (32, 5)])
def test_oracle_equivalence_m16_m32(m_size, n_qubits):
    """O1 (diagonal) and O2 (range) MUST mark equivalent states for M=16 and M=32 (Section 14)."""
    k_low = 1
    k_high = 3
    is_equiv = verify_oracle_equivalence(n_qubits, k_low, k_high)
    assert is_equiv, f"Diagonal and Range oracles are not equivalent for M={m_size}"
