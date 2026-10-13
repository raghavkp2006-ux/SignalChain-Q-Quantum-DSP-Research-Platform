# SignalChain-Q: ECG-First Classical + Quantum DSP Research Platform

> **SignalChain-Q is a web-based classical–quantum signal-processing research platform that benchmarks ECG denoising methods under identical noise conditions. It combines conventional ECG DSP baselines with QFT-based quantum denoising, an ECG-aware adaptive band-pass oracle, amplitude amplification, and detailed quantum resource accounting.**

---

## 1. Project Objective & Hypothesis

The core research objective of SignalChain-Q is to evaluate whether a frequency-domain quantum algorithm combining the Quantum Fourier Transform (QFT), an activity-guided adaptive bandpass phase oracle, and Grover amplitude amplification can effectively preserve physiological ECG morphology (P-QRS-T complex) while suppressing baseline wander and high-frequency EMG noise.

Crucially, SignalChain-Q accounts for the complete physical cost of quantum information processing—including state preparation depth, CX (CNOT) gate counts, and transpiled circuit overhead—when comparing against classical DSP baselines.

---

## 2. Why ECG-First?

ECG was chosen as the primary modality for Phase 1 because:
- **Clinical Standardization:** Established PhysioNet benchmarks (MIT-BIH, NSTDB, QTDB) provide canonical clean/noisy pairs and expert beat annotations.
- **Spectral Structure:** ECG information is concentrated within a well-defined physiological band (0.5 to ~40 Hz). This allows designing oracles that target both sub-0.5 Hz baseline drift and high-frequency muscle tremor simultaneously.
- **Rigorous Ground Truth:** Quantitative metrics (R-peak sensitivity, PRD, SNR improvement) allow testing without subjective evaluation.

*(Future modalities including EEG, EMG, PPG, audio, and imaging are planned for subsequent phases.)*

---

## 3. Implemented Denoising Pipelines

All methods receive the **identical input waveform** and clean reference:

| Identifier | Domain | Description |
| :--- | :--- | :--- |
| `raw` | Baseline (C0) | Unprocessed passthrough baseline |
| `butterworth_bandpass` | Classical (C1) | 4th-order SOS zero-phase Butterworth filter (0.5–40 Hz) |
| `wavelet_db6` | Classical (C2) | Daubechies-6 wavelet shrinkage with MAD noise estimation & universal threshold |
| `fft_adaptive_bandpass` | Classical (C3) | **Primary fair comparison:** Exact classical equivalent applying adaptive marked frequency mask on identical windowed frames |
| `qft_grover_ecg_adaptive` | Quantum (QSP) | Amplitude state preparation $\to$ QFT $\to$ adaptive bandpass oracle $\to$ Grover amplitude amplification $\to$ IQFT $\to$ statevector reconstruction |

---

## 4. Benchmark Datasets

- **MIT-BIH Arrhythmia Database (`mitdb` v1.0.0):** 48 records at 360 Hz. Partitioned into a frozen, deterministic split (`configs/splits/mitdb_v1.json`, seed `1448`) with 33 development, 8 validation, and 7 test records. Records 201 and 202 are grouped together.
- **MIT-BIH Noise Stress Test Database (`nstdb` v1.0.0):** Primary paired benchmark using records 118 and 119 across canonical SNRs (-6, 0, 6, 12, 18, 24 dB) with calibrated baseline wander (`bw`), muscle artifact (`ma`), and electrode motion (`em`).
- **QT Database (`qtdb` v1.0.0):** External validation for waveform onset/offset timing preservation.

---

## 5. Installation & Setup

### Prerequisites
- Python 3.11+ (Python 3.12 supported)
- Node.js 18+ (Node 20+ recommended)

### Python Environment Setup
```bash
# Navigate to signalchain-q directory
cd signalchain-q

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .
pip install -r requirements.txt
```

### Running Tests
Execute the comprehensive 46-test verification suite:
```bash
pytest -v
```

---

## 6. Running Dataset Downloads & Benchmark CLI

```bash
# 1. Download PhysioNet datasets (or pilot subset)
python scripts/download_datasets.py --dataset nstdb
python scripts/download_datasets.py --dataset mitdb

# 2. Build dataset manifests
python scripts/build_ecg_manifest.py

# 3. Generate SNR-controlled noisy pairs (±0.25 dB tolerance)
python scripts/generate_noisy_ecg.py --config configs/ecg_mvp.yaml --split validation --limit 10

# 4. Run pilot benchmark (900 method evaluations)
python scripts/run_ecg_benchmark.py --config configs/ecg_mvp.yaml --mode pilot

# 5. Export publication LaTeX summary tables
python scripts/export_results.py --results_dir results/pilot_* --output_dir results/publication
```

---

## 7. Web Application (FastAPI + Next.js)

### Launch Backend (Port 8000)
```bash
# From signalchain-q directory with .venv active:
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation is available at: `http://localhost:8000/docs`

### Launch Frontend (Port 3000)
```bash
# In a separate terminal:
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser:
- **`/`**: Research overview, scientific questions, and 3-pillar architectural summary.
- **`/ecg`**: Interactive ECG Studio with live oscilloscope canvas, metric calculation, and quantum resource panel.
- **`/benchmark`**: 5-method comparison table with latency and SNR improvement breakdown.
- **`/research`**: Theoretical foundations, Grover diffusion equations, and literature novelty gate.

---

## 8. Candid Scientific Limitations

1. **State Preparation Overhead:** Under current physical qubit architectures, preparing arbitrary amplitude states $|\psi\rangle = \sum_i v_i |i\rangle$ requires circuit depth exponential or polynomial in qubit count unless specialized QRAM is available.
2. **Simulation Runtime:** Simulating statevectors on classical computers is computationally slower than classical FFTs. Quantum algorithm runtime is therefore reported separately from simulation wall-clock time.
3. **Medical Disclaimer:** **RESEARCH USE ONLY.** SignalChain-Q is not a diagnostic device and must not be used for clinical patient care.

---

## 9. References

1. **Dutta, S., Basarab, A., Kouamé, D., & Georgeot, B.** (2024). *Quantum Algorithm for Signal Denoising*. IEEE Signal Processing Letters, 31, 156–160. [DOI: 10.1109/LSP.2023.3344071](https://doi.org/10.1109/LSP.2023.3344071).
2. **Laskar et al.** (2024). *A complexity efficient penta-diagonal quantum smoothing filter for bio-medical signal denoising: a study on ECG*. Scientific Reports, 14, 10580.
3. **Moody, G. B., Muldrow, W. E., & Mark, R. G.** (1984). *A noise stress test for arrhythmia detectors*. Computers in Cardiology, 11, 381–384. (PhysioNet NSTDB).
4. **Mark, R. G., & Moody, G. B.** (1997). *MIT-BIH Arrhythmia Database*. PhysioNet. [DOI: 10.13026/C2F305](https://doi.org/10.13026/C2F305).
