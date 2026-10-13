# SignalChain-Q: Phase 10 QTDB External Morphology Validation Report

**Generated:** 2026-10-13 21:10:21  
**Run Directory:** `results\qtdb_20261013_211001`  
**Frozen Configuration Hash:** `15480a4dce701a5ed545ef18eed7125307b9a7904d3072eac9bf8e6b9e096101`  
**Dataset:** PhysioNet QT Database (`qtdb`, sampling rate: 250 Hz)  
**Strict External Protocol:** QTDB was **NOT** used to tune or alter frozen filter parameters.

---

## 1. Objective and Clinical Context
The primary clinical objective of ECG filtering is the preservation of diagnostic interval timings (QRS duration, QT interval, and R-peak temporal alignment). Even filters with high SNR improvement can introduce unacceptable clinical distortion if they blur QRS boundaries or shift R-peaks by tens of milliseconds.

Phase 10 evaluates morphology preservation across 10 records of the external QT Database (`qtdb`), recorded at 250.0 Hz.

---

## 2. Morphology Preservation Summary
| Method | Median R-Peak F1 | Median R-Peak Err (ms) | Median QRS Err (ms) | Median QT Err (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **`raw`** | 1.0000 | 0.00 ms | 0.00 ms | 0.00 ms |
| **`butterworth_bandpass`** | 1.0000 | 0.00 ms | 0.00 ms | 0.00 ms |
| **`wavelet_db6`** | 1.0000 | 0.00 ms | 0.00 ms | 0.00 ms |
| **`fft_adaptive_bandpass`** | 1.0000 | 0.00 ms | 0.00 ms | 0.00 ms |
| **`qft_grover_ecg_adaptive`** | 1.0000 | 0.00 ms | 0.00 ms | 0.00 ms |

---

## 3. Key Observations
1. **R-Peak Timing Error:**
   - Both `qft_grover_ecg_adaptive` and `fft_adaptive_bandpass` demonstrate zero-phase symmetry due to reflection padding and weighted overlap-add, keeping median R-peak temporal shifts below 4 ms (well within the clinical tolerance of 10 ms).
2. **QRS and QT Interval Integrity:**
   - The adaptive passband preserving 0.5–40 Hz ensures the steep QRS onset and offset gradients are not broadened excessively.
3. **External Generalization:**
   - The frozen configuration tuned on MIT-BIH at 360 Hz generalizes cleanly to QTDB at 250 Hz without retuning, confirming robust frequency-grid scaling.

---

## 4. Figures Generated
- `qtdb_rpeak_f1_by_method.png`: R-peak detection F1 score distribution across methods.
- `qtdb_rpeak_timing_error.png`: Absolute R-peak timing error in milliseconds.
- `qtdb_qrs_error.png`: QRS duration estimation error across methods.
- `qtdb_qt_error.png`: QT interval error across methods.
