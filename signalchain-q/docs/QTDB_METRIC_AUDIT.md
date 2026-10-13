# SignalChain-Q: QTDB Morphology Metric Audit

**Audit Date:** 2026-10-13  
**Target Module:** `qsp/experiments/validate_qtdb.py` (`evaluate_qtdb_waveform_intervals`)  
**Target Results:** `results/qtdb_20261013_211001/qtdb_method_summary.csv` and `docs/PHASE10_QTDB_REPORT.md`

---

## 1. Audit Context and Question

Phase 10 results reported:
- Median R-peak timing error: `0.00 ms`
- Median QRS duration error: `0.00 ms`
- Median QT interval error: `0.00 ms`

**Audit Objective:** Verify whether these metrics are genuinely produced by independent post-filter feature detection, or whether they represent an artifact of annotation copying, rounding, or proxy estimation.

---

## 2. Source Code Inspection

In `qsp/experiments/validate_qtdb.py`, lines 43–80:

```python
def evaluate_qtdb_waveform_intervals(
    clean_sig: np.ndarray,
    processed_sig: np.ndarray,
    fs: float = 250.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    ref_peaks = metadata.get("r_peaks")
    if ref_peaks is None or len(ref_peaks) == 0:
        ref_peaks = detect_r_peaks_pantompkins(clean_sig, fs=fs)

    test_peaks = detect_r_peaks_pantompkins(processed_sig, fs=fs)
    r_eval = evaluate_r_peak_detections(ref_peaks, test_peaks, fs=fs)

    dt_ms = 1000.0 / fs  # 4.0 ms per sample at 250 Hz

    timing_errors = []
    for r_ref in ref_peaks:
        diffs = np.abs(test_peaks - r_ref)
        if len(diffs) > 0 and np.min(diffs) <= int(0.15 * fs):
            closest = np.min(diffs)
            timing_errors.append(closest * dt_ms)

    med_r_err = float(np.median(timing_errors)) if timing_errors else 0.0

    # Line 70-71:
    qrs_err = round(med_r_err * 0.85, 2)
    qt_err = round(med_r_err * 1.25, 2)
```

---

## 3. Findings

### A. R-Peak Timing Error (Genuinely Evaluated, Discrete Grid Bound)
1. **Detection Mechanism:**
   - `test_peaks` is produced by executing the Pan-Tompkins QRS detector **independently** on the filtered signal `processed_sig`.
   - `ref_peaks` is produced by running Pan-Tompkins on `clean_sig`.
2. **Why the Error is 0.00 ms:**
   - Both `qft_grover_ecg_adaptive` and classical `fft_adaptive_bandpass` use **symmetric reflection padding** and **weighted Hann overlap-add synthesis**.
   - These techniques guarantee linear-phase / zero-phase reconstruction.
   - On clean ECG records at $f_s = 250$ Hz ($\Delta t = 4.0$ ms), the energy peak of the squared derivative coincides at the **identical discrete sample index** before and after filtering ($|r_{\text{test}} - r_{\text{ref}}| = 0$ samples).
   - $0 \times 4.0\text{ ms} = 0.00\text{ ms}$.
3. **Validity:**
   - The R-peak detection timing measurement is **genuine**, but it reflects discrete sample resolution ($\pm 2.0$ ms sub-sample jitter is quantized to 0 on the discrete grid).

### B. QRS Duration and QT Interval Errors (Identified as Proxy Functions)
1. **Derivation Mechanism:**
   - Lines 70–71 compute:
     $$\text{qrs\_err} = \text{round}(\text{med\_r\_err} \times 0.85, 2)$$
     $$\text{qt\_err} = \text{round}(\text{med\_r\_err} \times 1.25, 2)$$
   - When $\text{med\_r\_err} = 0.00$, both evaluate to $0.00$ ms.
2. **Scientific Finding:**
   - **These were NOT independently delineated morphology boundaries.**
   - The script did not independently detect QRS onset, QRS offset (J-point), or T-wave offset using a dedicated multi-lead ECG delineator model or PhysioNet `.pu` annotation boundary parser.
   - Reporting QRS and QT interval errors as measured values without qualification would be scientifically inaccurate.

---

## 4. Remediation & Publication Guidance

1. **In Manuscript Tables:**
   - Clearly report **R-peak timing error** as measured via independent Pan-Tompkins peak detection.
   - Do **NOT** claim independent experimental measurement of QRS duration and QT interval boundaries in milliseconds.
   - Clearly footnote or label that sub-sample QRS onset/offset and T-wave offset boundary delineation requires dedicated fiducial delineation algorithms.
2. **In Discussion:**
   - Highlight that while zero-phase overlap-add ensures zero-sample discrete peak drift on a 4.0 ms grid, subtle morphologic changes (such as PRD = 6.05% for QFT Grover vs PRD = 0.001% for Wavelet) can affect low-amplitude wave segments (P-wave, T-wave).
