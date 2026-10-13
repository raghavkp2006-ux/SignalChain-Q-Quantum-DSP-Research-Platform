# SignalChain-Q Experiment Protocol

## 1. Experimental Conditions

### Noise Types
- **Baseline Wander (`bw`):** Respiration and drift frequencies (0.05–0.5 Hz).
- **Muscle Artifact (`ma`):** High-frequency electromyographic interference (20–100 Hz).
- **Electrode Motion (`em`):** Large transient steps accompanied by low-frequency recovery.

### Signal-to-Noise Ratio Grid
- Range: `[-6, 0, 6, 12, 18, 24]` dB
- Mixing Rule:
  $$\alpha = \sqrt{\frac{P_x}{P_n \cdot 10^{\text{SNR}_{\text{target}} / 10}}}$$
- Strict Tolerance: $|\text{SNR}_{\text{measured}} - \text{SNR}_{\text{target}}| \le 0.25$ dB.

---

## 2. Benchmark Suites

### Pilot Benchmark (Section 21)
- 10 segments &times; 3 noise types &times; 6 SNRs &times; 5 methods = **900 runs**.
- Used strictly for debugging, stability, and pipeline verification.

### Full Publication Benchmark (Section 22)
- 50 deterministic test segments &times; 3 noise types &times; 6 SNRs &times; 5 methods = **4,500 runs**.
- Paired Wilcoxon signed-rank tests with Holm-Bonferroni correction and Cliff's delta effect sizes.
