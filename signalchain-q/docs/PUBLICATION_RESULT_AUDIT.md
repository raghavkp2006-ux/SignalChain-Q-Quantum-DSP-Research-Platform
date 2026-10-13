# SignalChain-Q: Publication Result Audit

**Audit Date:** 2026-10-13  
**Audit Scope:** Verification of reported quantitative values in Phase 8–10 documentation against authoritative source CSV artifacts.  
**Authoritative Result Directories:**
- Validation: `results/validation_20261013_202654/`
- Test (MIT-BIH + NSTDB): `results/test_20261013_204319/`
- QTDB External: `results/qtdb_20261013_211001/`
- Ablations A–D: `results/ablations_20261013_211229/`

---

## 1. Metric Audit Table

| Phase | Metric | Reported Document Value | Source CSV File | Source Column | Aggregation Method | Verification Status | Notes / Discrepancies |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 8** | Total Evaluated Grid Configurations | 108 | `validation_parameter_grid.csv` | `config_id` | Count (`len`) | **VERIFIED** | $3 \times 3 \times 3 \times 4 = 108$, $f_{\text{min}} < f_{\text{max}}$ |
| **Phase 8** | Morphology Feasible Configurations | 46 / 108 | `selected_configuration.yaml` | `metrics_summary` | Filter ($F_1 \ge 0.99$) | **VERIFIED** | 46 configurations passed condition |
| **Phase 8** | Selected $f_{\text{high,min}}$ | 30.0 Hz | `selected_configuration.yaml` | `adaptive_filter.f_high_min` | Config selection | **VERIFIED** | Selected config `cfg_086` |
| **Phase 8** | Selected $f_{\text{high,max}}$ | 45.0 Hz | `selected_configuration.yaml` | `adaptive_filter.f_high_max` | Config selection | **VERIFIED** | Selected config `cfg_086` |
| **Phase 8** | Selected Segment Size ($M$) | 64 ($n=6$ qubits) | `selected_configuration.yaml` | `quantum.segment_size` | Config selection | **VERIFIED** | Selected config `cfg_086` |
| **Phase 8** | Selected Grover Iterations ($r$) | 2 | `selected_configuration.yaml` | `quantum.grover_iterations` | Config selection | **VERIFIED** | Selected config `cfg_086` |
| **Phase 8** | Selected Median SNR Improvement | +0.2372 dB | `selected_configuration.yaml` | `median_snr_improvement_db` | Median over 8 records | **VERIFIED** | Matches raw validation runs |
| **Phase 8** | Selected Median R-peak $F_1$ | 1.0000 | `selected_configuration.yaml` | `median_r_peak_f1` | Median over 8 records | **VERIFIED** | Morphology preserved |
| **Phase 8** | Selected Median PRD | 38.2257% | `selected_configuration.yaml` | `median_prd_percent` | Median over 8 records | **VERIFIED** | Matches raw validation runs |
| **Phase 8** | Selected Median RMSE | 0.1463 | `selected_configuration.yaml` | `median_rmse` | Median over 8 records | **VERIFIED** | Matches raw validation runs |
| **Phase 8** | Configuration SHA-256 Hash | `aa9704fa...` / `15480a4d...` | `config_hash.txt` / `configs/ecg_frozen_v1.yaml` | SHA-256 checksum | Exact hash | **NOTED / EXPLAINED** | Hash `aa9704fa...` was captured at generation; `15480a4d...` is current canonical hash after YAML formatting finalized. |
| **Phase 9** | MIT-BIH Raw Test Sample Count | 1,260 instances | `mitdb_test_results.csv` | rows | Count (`len`) | **VERIFIED** | 7 records $\times$ 6 noise $\times$ 6 SNR $\times$ 5 methods = 1,260 |
| **Phase 9** | NSTDB Test Sample Count | 60 instances | `nstdb_test_results.csv` | rows | Count (`len`) | **VERIFIED** | 12 noise records $\times$ 5 methods = 60 |
| **Phase 9** | Raw Median SNR Imp (MIT-BIH) | 0.00 dB | `test_method_summary.csv` | `snr_improvement_db_median` | Median | **VERIFIED** | Reference raw baseline |
| **Phase 9** | Butterworth Median SNR Imp (MIT-BIH) | -9.3829 dB | `test_method_summary.csv` | `snr_improvement_db_median` | Median | **VERIFIED** | Butterworth bandpass filter |
| **Phase 9** | Wavelet DB6 Median SNR Imp (MIT-BIH) | +0.5931 dB | `test_method_summary.csv` | `snr_improvement_db_median` | Median | **VERIFIED** | Classical wavelet baseline |
| **Phase 9** | FFT Adaptive Median SNR Imp (MIT-BIH) | -7.4798 dB | `test_method_summary.csv` | `snr_improvement_db_median` | Median | **VERIFIED** | Matched classical baseline |
| **Phase 9** | QFT Grover Median SNR Imp (MIT-BIH) | -0.4680 dB | `test_method_summary.csv` | `snr_improvement_db_median` | Median | **VERIFIED** | Quantum adaptive baseline |
| **Phase 9** | Wavelet DB6 Median PRD (MIT-BIH) | 17.67% | `test_method_summary.csv` | `prd_percent_median` | Median | **VERIFIED** | Lowest PRD on synthetic test |
| **Phase 9** | QFT Grover Median PRD (MIT-BIH) | 23.52% | `test_method_summary.csv` | `prd_percent_median` | Median | **VERIFIED** | Close to Wavelet; far below Butterworth (80.96%) |
| **Phase 9** | QFT Grover vs FFT Adaptive Median Diff | +7.1571 dB | `test_statistics.csv` | `median_difference` | Paired median difference | **VERIFIED** | Corrected Wilcoxon $p < 10^{-6}$ |
| **Phase 9** | QFT Grover vs FFT Adaptive 95% CI | [6.4092, 9.9092] dB | `test_statistics.csv` | `ci_95_low`, `ci_95_high` | 1000 bootstrap replicates | **VERIFIED** | Positive interval bound |
| **Phase 9** | QFT Grover vs FFT Adaptive Cliff's $\delta$ | +0.3627 | `test_statistics.csv` | `cliffs_delta` | Non-parametric effect size | **VERIFIED** | Moderate positive effect size |
| **Phase 9** | QFT Grover vs Wavelet DB6 Median Diff | -4.0603 dB | `test_statistics.csv` | `median_difference` | Paired median difference | **VERIFIED** | Corrected Wilcoxon $p < 10^{-6}$ |
| **Phase 9** | QFT Grover vs Wavelet DB6 Cliff's $\delta$ | -0.5528 | `test_statistics.csv` | `cliffs_delta` | Non-parametric effect size | **VERIFIED** | Large negative effect size |
| **Phase 9** | NSTDB Median SNR Imp (QFT Grover) | +0.8272 dB | `test_method_summary.csv` | `snr_improvement_db_median` (nstdb) | Median | **VERIFIED** | Real noise cocktail improvement |
| **Phase 9** | NSTDB Median SNR Imp (FFT Adaptive) | -2.8798 dB | `test_method_summary.csv` | `snr_improvement_db_median` (nstdb) | Median | **VERIFIED** | Real noise cocktail comparison |
| **Phase 10** | QTDB Record Count | 10 records | `qtdb_raw_results.csv` | `record_id.nunique()` | Count | **VERIFIED** | 10 records evaluated at 250 Hz |
| **Phase 10** | QTDB Median R-peak $F_1$ (QFT Grover) | 1.0000 | `qtdb_method_summary.csv` | `r_peak_f1_median` | Median | **VERIFIED** | External morphology preserved |
| **Phase 10** | QTDB Median PRD (QFT Grover) | 6.0482% | `qtdb_method_summary.csv` | `prd_percent_median` | Median | **VERIFIED** | vs Butterworth 46.36%, FFT 38.40% |
| **Phase 10** | QTDB R-peak Timing Error | 0.00 ms | `qtdb_method_summary.csv` | `r_peak_timing_error_ms_median` | Median | **AUDITED / REVISED** | Genuine discrete Pan-Tompkins alignment (0-sample shift on 4 ms sampling interval grid). See `docs/QTDB_METRIC_AUDIT.md`. |
| **Phase 10** | QTDB QRS Duration & QT Error | 0.00 ms | `qtdb_method_summary.csv` | `qrs_duration_error_ms_median` | Median proxy function | **AUDITED / REVISED** | Calculated via proxy scaling of R-peak timing error in prototype, not independent boundary delineation. Clarified in paper. |
| **Ablation A** | Peak Grover Iteration Regime | $r=1$ and $r=2$ | `ablation_a_grover_iterations.csv` | `grover_iterations` | Max SNR imp / F1 | **VERIFIED** | $r \ge 3$ triggers over-rotation |
| **Ablation B** | Gate Scaling with $M$ | $M=64$ (depth 28, 19 CX) to $M=256$ (depth 56, 27 CX) | `ablation_b_segment_size.csv` | `transpiled_depth`, `cx_count` | Exact count | **VERIFIED** | $O(2^n)$ state preparation verified |
| **Ablation C** | Oracle Functional Equivalence | True ($M=16, 32, 64$) | `ablation_c_oracle_comparison.csv` | `functional_equivalence` | Statevector fidelity check | **VERIFIED** | $O_1 \equiv O_2$ verified |
| **Ablation D** | Fair Classical FFT vs QFT Grover | FFT +0.82 dB, QFT -12.00 dB (on $M=128, r=1$) | `ablation_d_quantum_vs_classical.csv` | `snr_improvement_db` | Paired run | **VERIFIED** | Both use identical cutoffs (25–45 Hz) |

---

## 2. Inconsistencies & Reconciliations

1. **Configuration Hash:**
   - Initial Phase 8 run recorded `aa9704fa1f82e95d089033d013ecdbf4a135722cd21ed5233ff5e6efbe53b1eb`.
   - The finalized frozen configuration file [configs/ecg_frozen_v1.yaml](file:///c:/antigravity_projects/SignalChain-Q%20%E2%80%94%20ECG-First%20Classical%20+%20Quantum%20DSP%20Research%20Platform/signalchain-q/configs/ecg_frozen_v1.yaml) has SHA-256 checksum `15480a4dce701a5ed545ef18eed7125307b9a7904d3072eac9bf8e6b9e096101` (due to explicit comment additions and whitespace normalization).
   - Both test directories (`results/test_20261013_204319/` and `results/qtdb_20261013_211001/`) correctly read and record `15480a4dce701a5ed545ef18eed7125307b9a7904d3072eac9bf8e6b9e096101`.
2. **QTDB Morphology Interval Granularity:**
   - As documented in `docs/QTDB_METRIC_AUDIT.md`, R-peak timing error is 0.0 ms because detected R-peaks coincide exactly on the 4.0 ms (250 Hz) discrete sampling grid.
   - QRS and QT interval errors reported as 0.00 ms were linear proxies of R-peak temporal shift rather than manual/multi-lead fiducial point parsing. This is clearly qualified in all tables and manuscript text.
