# Reproducibility Guide: SignalChain-Q

This document provides complete, step-by-step instructions for reproducing all experimental results, validation runs, ablations, publication tables, and figures reported in the **SignalChain-Q** publication.

---

## 1. Environment & Python Setup

The codebase requires **Python 3.10+** (tested on Python 3.12.10).

```bash
# Clone repository
git clone https://github.com/raghavkp2006-ux/SignalChain-Q-Quantum-DSP-Research-Platform.git
cd SignalChain-Q-Quantum-DSP-Research-Platform/signalchain-q

# Create and activate virtual environment
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### Dependency Installation

Install all required numerical, DSP, and quantum packages:

```bash
pip install --upgrade pip setuptools wheel
pip install numpy scipy pandas matplotlib wfdb pywt qiskit qiskit-aer pyyaml pytest
```

---

## 2. Dataset Acquisition & Manifest Construction

SignalChain-Q uses publicly accessible PhysioNet benchmarks:
- **MIT-BIH Arrhythmia Database (`mitdb`)**
- **MIT-BIH Noise Stress Database (`nstdb`)**
- **QT Database (`qtdb`)**

To download the required record subsets and generate the canonical dataset splits:

```bash
# 1. Download records and construct MIT-BIH manifest
python scripts/build_ecg_manifest.py

# 2. Acquire Noise Stress Database records (bw, ma, em)
python scripts/fetch_nstdb_records.py

# 3. Generate synthetic and calibrated noise test sets
python scripts/generate_noisy_ecg.py --dataset mitdb --seed 1448
```

The pre-registered dataset split is preserved at:
```text
configs/splits/mitdb_v1.json
```
- **Validation Split (8 records):** `101`, `103`, `106`, `117`, `201`, `202`, `207`, `220`
- **Test Split (12 records):** `100`, `105`, `108`, `109`, `111`, `112`, `114`, `115`, `116`, `118`, `119`, `121`
- **QTDB External Validation:** `sel100`, `sel102`, `sel103`, `sel104`, `sel16421`

---

## 3. Frozen Configuration & Reproducibility Seed

All experiments use deterministic pseudo-random number generator seed:
```text
Seed = 1448
```

The frozen optimal parameter configuration is stored at:
```text
configs/ecg_frozen_v1.yaml
```

- **Configuration Hash:** `aa9704fa1f82e95d089033d013ecdbf4a135722cd21ed5233ff5e6efbe53b1eb`
- **File SHA-256:** `c797177d95e058ed49a567323c9506ef213e7cbcf1e853d1936ad58bc6033c01`
- **Frozen Parameters:**
  - $f_{\text{high, min}} = 30.0$\,Hz
  - $f_{\text{high, max}} = 45.0$\,Hz
  - $f_{\text{low}} = 0.5$\,Hz
  - Segment size $M = 64$ ($n=6$ qubits)
  - Hop size $H = 32$ (50\% overlap)
  - Grover iterations $r = 2$
  - Oracle: `diagonal_reference` ($\mathcal{O}_1$)

---

## 4. Execution Commands for Experimental Phases

> **Note:** Completed experimental runs are preserved under `results/`. To re-execute from scratch, use the following commands:

### Phase 8 — Validation Parameter Grid Search
Runs the 108-configuration parameter exploration across the 8 validation records:
```bash
python -m qsp.experiments.phase8_validation --config configs/ecg_validation_grid.yaml --seed 1448
```
*Output artifact:* `results/validation_YYYYMMDD_HHMMSS/validation_parameter_grid.csv`

### Phase 9 — Primary MIT-BIH Test Benchmark
Executes the primary evaluation across all 12 test records, 6 noise types, and 6 input SNR levels ($N=324$ conditions per method):
```bash
python -m qsp.experiments.phase9_test --config configs/ecg_frozen_v1.yaml --seed 1448
```
*Output artifact:* `results/test_20261013_204319/test_benchmark_results.csv` and `paired_statistics.csv`

### Phase 10 — External QTDB Morphology Validation
Executes external generalizability testing on QTDB records:
```bash
python -m qsp.experiments.phase10_qtdb --config configs/ecg_frozen_v1.yaml --seed 1448
```
*Output artifact:* `results/qtdb_20261013_211001/qtdb_benchmark_results.csv`

### Ablation Studies
Executes Grover iteration ($r \in \{0, 1, 2, 3\}$), frame size ($M \in \{64, 128, 256\}$), and oracle architecture ($\mathcal{O}_1$ vs $\mathcal{O}_2$) ablations:
```bash
python -m qsp.experiments.ablations --config configs/ecg_frozen_v1.yaml --seed 1448
```
*Output artifact:* `results/ablations_20261013_203512/`

---

## 5. One-Command Publication Build

To generate all publication LaTeX tables, high-resolution vector figures, architecture diagrams, and supplementary materials in a single execution without re-running expensive quantum simulations:

```bash
python -m qsp.publication.build
```

### Generated Artifacts Summary

1. **Camera-Ready LaTeX Tables (`paper/tables/`):**
   - `table_dataset_summary.tex`: Dataset demographics and record splits.
   - `table_validation_parameters.tex`: Phase 8 validation performance.
   - `table_main_results.tex`: Primary MIT-BIH test metrics (Raw, Butterworth, Wavelet DB6, Adaptive FFT, QFT-Grover).
   - `table_statistics.tex`: Paired differences, bootstrap CIs, Cliff's $\delta$, Wilcoxon $p$-values.
   - `table_quantum_resources.tex`: Circuit depth, CX count, transpiled gates, simulation runtime.
   - `table_grover_ablation.tex`: Performance metrics across $r \in \{0, 1, 2, 3\}$.
   - `table_segment_ablation.tex`: Metrics across frame sizes $M \in \{64, 128, 256\}$.
   - `table_oracle_ablation.tex`: Comparison of $\mathcal{O}_1$ vs $\mathcal{O}_2$ implementations.
   - `table_qtdb_morphology.tex`: External validation on QTDB.
   - `table_noise_type_results.tex`: Subgroup analysis across 6 noise types.
   - `table_snr_level_results.tex`: Subgroup analysis across 6 input SNR levels.

2. **Vector PDF & High-Res PNG Figures (`paper/figures/`):**
   - `noise_type_snr.pdf`, `noise_type_prd.pdf`, `noise_type_f1.pdf`
   - `snr_input_vs_improvement.pdf`, `snr_input_vs_prd.pdf`, `snr_input_vs_f1.pdf`
   - `grover_tradeoff.pdf`, `circuit_scaling.pdf`, `qtdb_preservation.pdf`

3. **Architecture Diagram Sources (`paper/figures/source/`):**
   - `architecture.mmd` (Mermaid source)
   - `architecture.dot` (Graphviz DOT source)

4. **Manuscript Sources (`paper/`):**
   - `paper/main.tex`: Complete IEEE Transactions article source.
   - `paper/references.bib`: Verified BibTeX database.

---

## 6. Manuscript Compilation

If a LaTeX distribution is installed (e.g., TeX Live, MiKTeX, MacTeX):

```bash
cd paper
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

---

## 7. Running Test Suite

Verify that all unit tests, publication builders, and regression checks pass:

```bash
pytest tests
```

Expected output:
```text
======================== 56+ passed in <X>s ========================
```
