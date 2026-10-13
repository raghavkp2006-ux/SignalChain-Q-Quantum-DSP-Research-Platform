# SignalChain-Q Web Product Specification (Section 25)

## 1. Architecture Overview
- **Frontend:** Next.js 14 App Router, React, TypeScript, HTML5 Canvas Oscilloscope.
- **Backend:** FastAPI, Uvicorn, Pydantic v2.
- **Quantum Simulator:** Qiskit Aer (ideal Statevector engine).

## 2. Page Hierarchy & Routing

| Route | Title | Key Features |
| :--- | :--- | :--- |
| `/` | Overview | Scientific rationale, research disclaimer, 3 pillars of fair comparison |
| `/ecg` | ECG Studio | CSV upload, PhysioNet presets, real-time waveform canvas, quantum gate counts |
| `/benchmark` | Interactive Benchmark | 5-method comparison table with SNR, RMSE, PRD, F1, and latency breakdown |
| `/research` | Research & Theory | Mathematical formulation, Grover diffusion derivation, literature novelty gate |

## 3. Safety & Resource Limits
- Temporary in-memory processing: uploaded waveforms are not stored or logged permanently.
- Web interactive benchmark is limited to &le; 4.0 seconds (1500 samples) to prevent server timeouts.
- Explicit "RESEARCH USE ONLY. NOT A DIAGNOSTIC DEVICE." disclaimer visible on all views.
