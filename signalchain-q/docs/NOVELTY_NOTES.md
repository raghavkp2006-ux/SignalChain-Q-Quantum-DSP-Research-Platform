# SignalChain-Q: Publication Novelty Analysis & Prior Art Gate

## 1. Mandatory Literature Gate (Section 31)

Before claiming novelty in any publication, preprint, or benchmark report, the following prior works must be explicitly cited and differentiated:

### A. Dutta et al. (IEEE Signal Processing Letters, 2024)
- **Title:** *Quantum Algorithm for Signal Denoising*
- **DOI:** `10.1109/LSP.2023.3344071`
- **Key Concepts:** QFT, adaptive thresholding in frequency domain, amplitude amplification, IQFT.
- **Differences from SignalChain-Q:**
  - Evaluated generic 1D synthetic signals (e.g., polynomial/step functions) rather than clinical physiological waveforms.
  - Used an unbounded energy threshold rather than a physiological ECG bandpass.
  - Did not measure morphological preservation (R-peak F1, QRS timing, PRD).
  - Omitted end-to-end state preparation circuit depth accounting in comparative runtime tables.

### B. Laskar et al. (Scientific Reports, 2024)
- **Title:** *A complexity efficient penta-diagonal quantum smoothing filter for bio-medical signal denoising: a study on ECG*
- **DOI:** `10.1038/s41598-024-59851-5`
- **Key Concepts:** Penta-diagonal Hamiltonian smoothing filter applied to ECG.
- **Differences from SignalChain-Q:**
  - Operates purely as a time-domain linear smoothing operator.
  - Lacks frequency-domain spectral selectivity (cannot simultaneously reject sub-0.5 Hz baseline wander and >40 Hz muscle tremor).

### C. 2026 Conference Work
- **Title:** *Quantum Fourier Transform Based Electro Cardio Gram Signal Denoising*
- **Key Concepts:** Basic QFT on ECG.

---

## 2. Definitive Rule on Claims

Codex and researchers MUST follow this rule:
> **NEVER claim "first QFT ECG denoiser" or "quantum advantage" without measured empirical data and exhaustive literature verification.**

---

## 3. Validated Scientific Contributions of SignalChain-Q

1. **ECG-Aware Adaptive Bandpass Oracle:** Physiological marking of 0.5 Hz &le; |f| &le; adaptive high cutoff (25–45 Hz) derived from local ECG activity ($A_j = \text{mean}(|x_j - \text{median}(x_j)|)$).
2. **Fair Classical vs. Quantum Equivalence:** Direct benchmarking against an exact classical equivalent (`fft_adaptive_bandpass`) utilizing the identical segmentation, windowing, and marked frequency set.
3. **Rigorous Resource Accounting:** Independent reporting of StatePreparation depth/time, transpiled CNOT (CX) counts, algorithmic depth, and simulator execution.
