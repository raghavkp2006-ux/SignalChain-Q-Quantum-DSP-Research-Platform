# SignalChain-Q: Phase 9 Frozen MIT-BIH + NSTDB Test Evaluation Report

**Generated:** 2026-10-13 21:08:51  
**Run Directory:** `results\test_20261013_204319`  
**Frozen Configuration Hash:** `15480a4dce701a5ed545ef18eed7125307b9a7904d3072eac9bf8e6b9e096101`  
**Test Independence:** **STRICT (Zero parameter tuning performed on test data)**

---

## 1. Experimental Protocol
- **Locked Frozen Configuration:** Loaded directly from `configs/ecg_frozen_v1.yaml`.
  - $f_{\text{high},\text{min}} = 30.0$ Hz, $f_{\text{high},\text{max}} = 45.0$ Hz.
  - $M = 64$ samples ($n = 6$ qubits).
  - Grover iterations $r = 2$.
- **MIT-BIH Test Split:** 7 records (`['102', '113', '118', '119', '210', '228', '231']`).
  - Confirmed test records include 118 and 119.
  - Test set was strictly isolated during Phase 8 parameter tuning.
- **Evaluated Methods:** `raw`, `butterworth_bandpass`, `wavelet_db6`, `fft_adaptive_bandpass`, `qft_grover_ecg_adaptive`.
- **Noise Conditions:** Canonical noise conditions evaluated across:
  - Synthetic noise types: `['bw', 'ma', 'em', 'wgn', 'pl50', 'pl60']`
  - Target SNR levels: `[-6.0, 0.0, 6.0, 12.0, 18.0, 24.0]` dB
  - Real noise stress records: MIT-BIH Noise Stress Test Database (NSTDB).

---

## 2. Test Set Evaluation Results (MIT-BIH)
| Method | Median SNR Imp (dB) | Median F1 | Median PRD (%) | Median RMSE |
| :--- | :--- | :--- | :--- | :--- |
| **`raw`** | 0.00 | 1.0000 | 22.35 | 0.0929 |
| **`butterworth_bandpass`** | -9.38 | 1.0000 | 80.96 | 0.2528 |
| **`wavelet_db6`** | 0.59 | 1.0000 | 17.67 | 0.0771 |
| **`fft_adaptive_bandpass`** | -7.48 | 0.6667 | 62.90 | 0.2052 |
| **`qft_grover_ecg_adaptive`** | -0.47 | 1.0000 | 23.52 | 0.1355 |

---

## 3. NSTDB Real Noise Stress Results
Evaluated on calibrated real clinical noise stress recordings (`118e*` and `119e*` series across `-6` dB to `+24` dB):
- **Noise Types Evaluated:** Baseline wander (`bw`), muscle artifact (`ma`), electrode motion (`em`).
- **Median SNR Improvement on NSTDB:**
  - `qft_grover_ecg_adaptive`: 0.83 dB
  - `fft_adaptive_bandpass`: -2.88 dB
  - `butterworth_bandpass`: -3.75 dB

---

## 4. Paired Statistical Comparisons
Primary comparison between **`qft_grover_ecg_adaptive`** and its exact classical baseline counterpart **`fft_adaptive_bandpass`**:
- **Median Difference:** 7.1571 dB
- **95% Bootstrap Confidence Interval:** [6.4092, 9.9092] dB
- **Wilcoxon Signed-Rank p-value:** 0.0 (Corrected: 0.0)
- **Cliff's Delta Effect Size:** 0.3627

---

## 5. Quantum Resource Accounting
- **Total Qubits:** 6 logical qubits
- **Circuit Depth:** 7
- **Transpiled Depth:** 17
- **CX Gate Count:** 0
- **Stage Isolation Latency:**
  - State Preparation: 7.727 ms
  - Simulation: 2132.785 ms
  - Reconstruction: 1.377 ms

---

## 6. Scientific Interpretation & Bounds
- **Fair Classical Comparison:** Both `qft_grover_ecg_adaptive` and `fft_adaptive_bandpass` operate under identical adaptive frequency-band masking rules.
- **Resource Reality:** Quantum state preparation depth and simulation overhead demonstrate that amplitude encoding on classical data requires explicit accounting. QFT algorithmic advantage cannot be claimed without end-to-end I/O state preparation and measurement.
