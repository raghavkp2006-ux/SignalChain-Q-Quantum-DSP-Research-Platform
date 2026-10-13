# SignalChain-Q — ECG-First Classical + Quantum DSP Research Platform

Welcome to the **SignalChain-Q** research workspace.

## Repository Organization

- **`SIGNALCHAIN_Q_ECG_PROJECT_EXECUTION_PLAN.md`**: Complete system execution blueprint, research methodology, and reproducibility contract.
- **`signalchain-q/`**: The complete platform implementation containing:
  - **`backend/`**: FastAPI REST API providing `/api/health`, `/api/ecg/process`, `/api/datasets/ecg/examples`, and `/api/benchmark/ecg`.
  - **`frontend/`**: Next.js 14 Web Application with interactive Oscilloscope waveform visualizer, comparative benchmark tables, and quantum resource analyzers.
  - **`qsp/`**: Quantum and Classical Digital Signal Processing library:
    - `qsp/classical/`: Butterworth SOS (C1), Wavelet db6 (C2), and fair Adaptive FFT (C3).
    - `qsp/quantum/`: QFT, adaptive bandpass phase oracle, Grover amplitude amplification, Aer statevector reconstruction, and resource profiling.
    - `qsp/modalities/ecg/`: ECG I/O, Pan-Tompkins QRS morphology metrics, and calibrated SNR noise mixing.
    - `qsp/benchmarks/`: Deterministic ablation runner, Wilcoxon & Cliff's delta statistics, and publication plotting.
  - **`configs/`**: Frozen deterministic dataset splits (`mitdb_v1.json`) and MVP/publication configs (`ecg_mvp.yaml`).
  - **`scripts/`**: CLI dataset downloaders, manifest generators, noise injectors, and benchmark runners.
  - **`docs/`**: Algorithm specifications, dataset cards, experimental protocols, and literature novelty gate.
  - **`tests/`**: Pytest test suite covering quantum identity fidelity, oracle equivalence, SNR mixing tolerances, classical filters, and API endpoints.

For full setup and usage instructions, please refer to:
[**`signalchain-q/README.md`**](signalchain-q/README.md)
