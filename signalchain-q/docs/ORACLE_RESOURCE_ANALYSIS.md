# SignalChain-Q: Quantum Phase Oracle Architecture & Resource Analysis

**Document:** Structural Comparison of Phase Marking Oracles in Quantum DSP  
**Focus:** $O_1$ (Dense Diagonal Reference Oracle) vs. $O_2$ (Explicit Range/Comparator Oracle)  

---

## 1. Problem Formulation

In the SignalChain-Q adaptive filtering pipeline, the quantum phase oracle $U_{\mathcal{K}}$ marks discrete frequency bins corresponding to the physiological QRS complex:
$$U_{\mathcal{K}} |k\rangle = (-1)^{f(k)} |k\rangle$$
where $f(k) = 1$ if $k \in \mathcal{K}_{\text{pass}}$, and $f(k) = 0$ otherwise.

Due to the symmetry of discrete Fourier transforms for real-valued signals, the passband set $\mathcal{K}_{\text{pass}}$ contains both positive and negative frequency bins:
$$\mathcal{K}_{\text{pass}} = [k_{\text{low}}, k_{\text{high}}] \cup [M - k_{\text{high}}, M - k_{\text{low}}]$$
DC ($k=0$) and Nyquist ($k = M/2$) are strictly excluded to suppress baseline wander and high-frequency noise.

---

## 2. Oracle Architectures

### Architecture $O_1$: Dense Diagonal Reference Oracle
- **Construction:** Implemented via a unitary diagonal operator $U = \text{diag}(d_0, d_1, \dots, d_{M-1})$, where $d_k = -1$ if $k \in \mathcal{K}_{\text{pass}}$ and $d_k = +1$ otherwise.
- **Qiskit Implementation:** `qiskit.circuit.library.DiagonalGate(diagonal_phases)`
- **Logical Representation:** Encapsulated as a **single high-level instruction** (abstract logical depth = 1).

### Architecture $O_2$: Explicit Range / Bitstring Comparator Oracle
- **Construction:** Evaluates each target integer $k \in \mathcal{K}_{\text{pass}}$ independently by constructing multi-controlled phase-flip gates ($MCZ$):
  $$U_k = I - 2|k\rangle\langle k|$$
  For an $n$-bit binary representation $k = (b_{n-1} \dots b_0)_2$, $X$ gates are applied to qubits where $b_j = 0$, followed by an $(n-1)$-controlled $Z$ gate, followed by uncomputing the $X$ gates.
- **Logical Representation:** Concatenation of $|\mathcal{K}_{\text{pass}}|$ distinct multi-controlled phase gates.

---

## 3. Empirical Resource Comparison (Ablation C)

Results extracted directly from authoritative benchmark run ([ablation_c_oracle_comparison.csv](file:///c:/antigravity_projects/SignalChain-Q%20%E2%80%94%20ECG-First%20Classical%20+%20Quantum%20DSP%20Research%20Platform/signalchain-q/results/ablations_20261013_211229/ablation_c_oracle_comparison.csv)):

| Segment Size ($M$) | Qubits ($n$) | Functional Equivalence ($O_1 \equiv O_2$) | $O_1$ Logical Depth | $O_2$ Logical Depth | $O_1$ Transpile Time (ms) | $O_2$ Transpile Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **16** | 4 | **Verified (True)** | 1 | 32 | 4.88 ms | 4.43 ms |
| **32** | 5 | **Verified (True)** | 1 | 64 | 4.96 ms | 116.02 ms |
| **64** | 6 | **Verified (True)** | 1 | 128 | 4.91 ms | 4.43 ms |

---

## 4. Crucial Distinctions for Publication

### A. Abstract Logical Depth vs. Physical Gate Synthesis
A common pitfall in quantum software profiling is claiming that $O_1$ has $O(1)$ constant physical cost because its abstract circuit depth is 1.
- In reality, physical quantum hardware only natively supports 1-qubit and 2-qubit gates (e.g., $\{U_3, CX\}$ or $\{\sqrt{X}, X, R_z, CZ\}$).
- Decomposing an arbitrary $n$-qubit diagonal operator into native 2-qubit gates requires Walsh-operator / Gray-code synthesis (Shende et al., 2006; Bullock & Markov, 2004), requiring:
  $$\text{CX Count}(O_1) = 2^n - 1$$
  For $n=6$ ($M=64$), this represents 63 CNOT gates. For $n=8$ ($M=256$), this represents 255 CNOT gates.

### B. Hardware Scalability & Quantum Arithmetic
- **Trapped-Ion Architecture:** Trapped-ion systems support all-to-all connectivity and native multi-qubit Mølmer-Sørensen gates, making $O_1$ dense diagonal synthesis viable.
- **Superconducting Architecture:** Superconducting planar lattices (e.g. heavy-hex) lack all-to-all connectivity. Gray-code diagonal synthesis incurs massive SWAP routing overhead ($O(2^n)$ SWAPs), severely increasing decoherence.
- **Scalable Arithmetic Oracles ($O_3$ Future Work):** For large $M$ ($n > 10$), neither $O_1$ nor $O_2$ is optimal. The optimal fault-tolerant approach is a **quantum arithmetic comparator**:
  $$\text{Comparator}(k_{\text{low}}, k_{\text{high}}): |k\rangle |0\rangle \to |k\rangle |k_{\text{low}} \le k \le k_{\text{high}}\rangle$$
  Using ripple-carry or carry-lookahead adders with $O(n)$ ancilla qubits, this requires only $O(n) = O(\log M)$ circuit depth and zero exponential scaling!

---

## 5. Summary
1. Both $O_1$ and $O_2$ are functionally identical in spectral transformation fidelity.
2. $O_1$ is optimal for simulation and compact circuit representation in the current software stack.
3. In physical fault-tolerant implementations, arithmetic comparator oracles must replace table-lookup or dense diagonal synthesis to avoid $O(2^n)$ gate bottlenecks.
