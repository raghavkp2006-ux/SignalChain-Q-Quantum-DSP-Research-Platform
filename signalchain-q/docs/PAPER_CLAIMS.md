# SignalChain-Q: Scientific Research Claims Verification

**Document:** Evidence-Based Categorization of Scientific Claims  
**Methodology:** Grounded in Phase 8–10 experimental results and ablation studies  

---

## 1. Supported Claims

These claims are supported by quantitative empirical evidence and statistical tests ($p < 10^{-6}$):

1. **Morphology Preservation Under Adaptive Quantum Filtering:**
   - *Claim:* The amplitude-encoded QFT + Grover pipeline preserves ECG R-peak morphology and temporal fiducials under canonical noise conditions.
   - *Evidence:* Achieved median R-peak $F_1 = 1.0000$ (mean $0.9881$) on untouched MIT-BIH test records, with zero discrete sample timing shift (0.0 ms error on 250 Hz and 360 Hz grids) across external QTDB records.
2. **Superiority Over the Matched Classical Baseline (Adaptive FFT):**
   - *Claim:* When evaluated under identical adaptive frequency selection rules, QFT-Grover filtering significantly outperforms deterministic classical Adaptive FFT bandpass filtering.
   - *Evidence:* Paired median difference of **+7.1571 dB** in SNR improvement (95% Bootstrap CI: [6.4092, 9.9092] dB, Cliff's $\delta = +0.3627$, Holm-Bonferroni corrected Wilcoxon $p < 10^{-6}$) and lower PRD (23.52% vs 62.90%).
3. **Prevention of Recursive Filter Transient Distortion:**
   - *Claim:* The linear-phase windowed QFT pipeline prevents the transient edge ringing and phase distortion observed in recursive IIR Butterworth bandpass filters.
   - *Evidence:* Median difference of **+9.1169 dB** (Cliff's $\delta = +0.4474$, $p < 10^{-6}$) over `butterworth_bandpass` (median PRD 23.52% vs 80.96%).
4. **Resilience to Clinical Noise Cocktails (NSTDB):**
   - *Claim:* In real physical noise stress recordings (baseline wander, muscle artifact, electrode motion), QFT-Grover achieves positive SNR improvement and lower PRD than raw and classical FFT filters.
   - *Evidence:* Median SNR improvement of **+0.8272 dB** on NSTDB with PRD of 30.03% (vs raw PRD 33.22%, Butterworth -3.75 dB, FFT -2.88 dB).
5. **Bounded Grover Iteration Dynamics (Over-Rotation Barrier):**
   - *Claim:* Amplitude amplification on continuous biomedical spectra is bounded to $r \in \{1, 2\}$ iterations due to large initial passband energy fractions; scaling to $r \ge 3$ triggers over-rotation and destructive interference.
   - *Evidence:* Ablation A demonstrated peak quality at $r=1,2$ and severe performance collapse at $r=3$ (PRD > 170%, SNR -12.0 dB).
6. **Functional Equivalence of Oracle Implementations:**
   - *Claim:* Dense diagonal reference oracles ($O_1$) and explicit range comparator oracles ($O_2$) are functionally identical in unitary transformation fidelity.
   - *Evidence:* Statevector fidelity $= 1.0000$ verified across $M \in \{16, 32, 64\}$ in Ablation C and unit tests.

---

## 2. Partially Supported Claims

1. **Cross-Sampling-Rate Generalization:**
   - *Claim:* The frozen configuration tuned on MIT-BIH (360 Hz) generalizes cleanly to external datasets with different sampling rates without retuning.
   - *Status:* Supported for 250 Hz (QTDB), where $F_1 = 1.0000$ and $PRD = 6.05\%$ were achieved. However, this was evaluated on single-channel recordings and has not been tested across 500 Hz or 1000 Hz clinical ECG monitors.

---

## 3. Refuted Claims

These hypotheses are **empirically or theoretically refuted** and MUST NOT be asserted in the manuscript:

1. **"Universal Quantum Superiority Over Classical Denoising":**
   - *Status:* **REFUTED.**
   - *Finding:* Classical Multiresolution Wavelet Denoising (`wavelet_db6`) outperforms `qft_grover_ecg_adaptive` in raw SNR improvement (+0.5931 dB vs -0.4680 dB, paired difference -4.0603 dB, Cliff's $\delta = -0.5528$, $p < 10^{-6}$) and achieves lower PRD (17.67% vs 23.52%).
2. **"End-to-End Quantum Computational Speedup":**
   - *Status:* **REFUTED.**
   - *Finding:* While QFT gate complexity is $O(\log^2 M)$, state preparation on arbitrary classical data requires $\Theta(2^n) = \Theta(M)$ depth and gates without QRAM. Furthermore, classical state reconstruction via quantum state tomography requires $O(M/\epsilon^2)$ measurements. Classical FFT executes in $< 0.1$ ms.
3. **"Grover Iterations Act as a Traditional High-Order Low-Pass Filter":**
   - *Status:* **REFUTED.**
   - *Finding:* Unlike classical filter orders (where increasing filter order sharpens roll-off), increasing Grover iterations beyond $r=2$ rotates the state past the target vector, causing signal degradation.

---

## 4. Claims Not Tested

These topics are beyond the scope of this benchmark:

1. Physical NISQ processor execution with environmental device noise (T1, T2, readout error).
2. Diagnostic arrhythmia classification (PVC, AFib, VTach) impact.
3. Multi-lead (12-lead) simultaneous entangled processing.
4. Non-ECG biological signals (EEG, EMG, fMRI, speech).
