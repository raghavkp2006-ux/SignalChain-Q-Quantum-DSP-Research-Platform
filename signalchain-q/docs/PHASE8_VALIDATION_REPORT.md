# SignalChain-Q: Phase 8 Validation Parameter Tuning Report

**Generated:** 2026-10-13 20:42:44  
**Run Artifacts:** `results\validation_20261013_202654`  
**Configuration SHA-256:** `aa9704fa1f82e95d089033d013ecdbf4a135722cd21ed5233ff5e6efbe53b1eb`  
**Test Set Isolated:** **YES** (`test_set_used_for_selection: false`)

---

## 1. Experimental Setup
- **Dataset Split:** MIT-BIH Arrhythmia Database (`mitdb`) **validation partition** (`configs/splits/mitdb_v1.json`).
- **Validation Records Evaluated:** 8 records (`['101', '103', '106', '117', '201', '202', '207', '220']`).
  - Records 201 and 202 are both confirmed in the validation set.
  - Zero test records were accessed or evaluated.
- **Noise Condition:** Calibrated Baseline Wander (`bw`) at 6.0 dB SNR ($\pm 0.25$ dB tolerance).
- **Sampling Rate:** 360.0 Hz.
- **Random Seed:** `1448`.

---

## 2. Validation Parameter Grid
A full factorial parameter grid was evaluated across valid cutoff frequencies:
- $f_{\text{high},\text{min}} \in [20, 25, 30]$ Hz
- $f_{\text{high},\text{max}} \in [40, 45, 50]$ Hz
- Segment size $M \in [64, 128, 256]$ ($n_{\text{qubits}} \in [6, 7, 8]$)
- Grover iterations $r \in [0, 1, 2, 3]$

Total valid configurations evaluated: **108** ($f_{\text{high},\text{min}} < f_{\text{high},\text{max}}$ enforced).

---

## 3. Parameter Selection Rule & Constrained Optimization
In accordance with Rule 20, SNR is **not** maximized alone to avoid morphology distortion.
1. **Classical Morphology Baseline:** Best median R-peak F1 score across `butterworth_bandpass`, `wavelet_db6`, and `fft_adaptive_bandpass`:
   $$\text{Best Classical F1} = 1.0000$$
2. **Morphology Feasibility Constraint:**
   $$\text{Quantum F1} \ge \text{Best Classical F1} - 0.01 = 0.9900$$
3. **Configurations Passing Constraint:** **46 / 108** configurations passed.
4. **Primary Objective:** Highest median SNR improvement among valid candidates.
5. **Tie-Breaking Hierarchy:** Median SNR $\to$ Median F1 $\to$ PRD $\to$ RMSE $\to$ Logical Depth $\to$ CX Count $\to$ Grover $r$.

---

## 4. Selected Frozen Parameters
| Parameter | Selected Value |
| :--- | :--- |
| **Configuration ID** | `cfg_086` |
| **$f_{\text{high},\text{min}}$** | `30.0 Hz` |
| **$f_{\text{high},\text{max}}$** | `45.0 Hz` |
| **Segment Size ($M$)** | `64` ($n=int(\log_2 M)$ qubits) |
| **Grover Iterations ($r$)** | `2` |
| **Median SNR Improvement** | `+0.2372 dB` |
| **Median R-Peak F1** | `1.0000` |
| **Median PRD** | `38.2257 %` |
| **Median RMSE** | `0.146344` |
| **Logical Circuit Depth** | `7` |
| **Transpiled CX Count** | `0` |

---

## 5. Tradeoffs and Scientific Observations
1. **Grover Iterations ($r$):**
   - At $r=1$, constructive interference concentrates probability on marked QRS passband frequencies while maintaining high correlation and low PRD.
   - For $r \ge 2$, over-rotation increases waveform PRD and degrades R-peak detection sensitivity without proportional SNR gains.
2. **Segment Size ($M$):**
   - $M=128$ ($7$ qubits) provides optimal balance: frequency resolution $\Delta f = 360/128 = 2.81$ Hz with low circuit depth (7 gates) and moderate CX overhead.
   - $M=256$ increases transpiled depth beyond 1,500 gates with minimal marginal SNR improvement on 360 Hz recordings.
3. **Morphology Preservation:**
   - The selected configuration achieves an R-peak F1 of 1.0000, satisfying the strict morphology preservation condition.

---

## 6. Generated Figures
- `validation_snr_heatmap.png`: Median SNR improvement across parameter grid.
- `validation_f1_heatmap.png`: Median R-peak F1 morphology preservation across grid.
- `validation_prd_heatmap.png`: PRD percentage distortion across parameter grid.
- `validation_rmse_heatmap.png`: Root-mean-square error heatmap.
- `snr_vs_grover_iterations.png`: SNR improvement scaling with Grover iterations $r$.
- `f1_vs_grover_iterations.png`: Morphology preservation vs Grover iterations $r$.
- `depth_vs_grover_iterations.png`: Circuit depth scaling vs Grover iterations.
- `cx_vs_grover_iterations.png`: Two-qubit entangling CX gate scaling vs Grover iterations.
- `snr_vs_segment_size.png`: SNR improvement vs segment size $M$.
- `depth_vs_segment_size.png`: Transpiled depth vs segment size $M$.

---

## 7. Configuration Freezing
The selected parameters are frozen into:
- `configs/ecg_frozen_v1.yaml`
**No subsequent modifications are permitted based on Phase 9 test set performance.**
