# SignalChain-Q — ECG-First Classical + Quantum DSP Research Platform
## Complete Project Execution Plan for Codex

**Purpose:** This file is the implementation contract for the ECG-first version of SignalChain-Q. Treat every item marked **MUST** as required unless a later section explicitly overrides it.

**Project type:** Web-based research software platform  
**Primary modality:** ECG  
**Long-term goal:** Add EEG/EMG/PPG, generic time-series, audio, RF/communication, images, remote-sensing, seismic, radar/sonar and video only after ECG v1 is complete.

---

# 0. Executive Summary

Build a reproducible web platform that sends the **same ECG input** through:

1. classical DSP baselines,
2. quantum DSP denoising,
3. a fair classical-vs-quantum benchmark,
4. quantum resource analysis,
5. publication-ready evaluation.

Primary research question:

> Can an ECG-aware quantum frequency-domain denoiser based on QFT + an adaptive band-pass oracle + amplitude amplification + IQFT preserve ECG morphology while suppressing both baseline wander and high-frequency noise, and how does it compare with classical DSP once state preparation, circuit depth, gate count and reconstruction cost are included?

This is a **research/benchmark system**, not a diagnosis product.

---

# 1. Scientific Rules

Codex MUST follow these rules:

1. Do not claim quantum advantage unless measured data supports it.
2. Do not call the system diagnostic.
3. Classical and quantum methods MUST receive the same noisy input and the same clean reference when available.
4. Record every preprocessing operation.
5. Separate algorithm runtime from total end-to-end runtime.
6. Report state-preparation cost separately from QFT/Grover cost.
7. Report logical and transpiled circuit statistics separately.
8. Never treat measurement probabilities as ECG amplitudes.
9. Ideal statevector simulation is the primary waveform-producing quantum mode for Phase 1.
10. Shot/noise experiments must explicitly describe reconstruction.
11. Default project random seed: `1448`.
12. Dataset splits must be deterministic and frozen to disk.
13. Never commit PhysioNet waveform data to Git.
14. Do not break the existing SignalChain Android/audio project.
15. Reuse engineering patterns from the existing repository, not audio-specific processing.

---

# 2. Reuse from the Existing SignalChain Repository

Existing repository:

`raghavkp2006-ux/DSP-based-classical-signal-processing-`

Useful patterns already present:

- modular pipeline functions,
- deterministic ablation runners,
- before/after processing,
- CSV summaries,
- metrics aggregation,
- decision/routing architecture,
- separate runtime and offline evaluation code.

Reuse conceptually:

- `run_pipeline(...)` orchestration style,
- deterministic benchmark runner,
- result CSV + summary CSV,
- publication-style plots,
- stage logs,
- configuration-driven processing.

Do NOT reuse these audio-specific stages for ECG:

- speech pre-emphasis,
- VAD,
- speech noise PSD estimation,
- voice EQ,
- speech compression,
- speech CNN,
- STOI,
- audio SNR routing rules.

---

# 3. Repository Layout

Create:

```text
signalchain-q/
```

inside the current repository.

Target structure:

```text
signalchain-q/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── health.py
│       │   ├── ecg.py
│       │   ├── benchmark.py
│       │   └── datasets.py
│       ├── schemas/
│       └── services/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── qsp/
│   ├── core/
│   │   ├── types.py
│   │   ├── framing.py
│   │   ├── metrics.py
│   │   ├── timing.py
│   │   └── reproducibility.py
│   ├── modalities/
│   │   └── ecg/
│   │       ├── io.py
│   │       ├── preprocessing.py
│   │       ├── noise.py
│   │       ├── morphology.py
│   │       └── pipeline.py
│   ├── classical/
│   │   ├── bandpass.py
│   │   ├── wavelet.py
│   │   ├── fft_adaptive.py
│   │   └── registry.py
│   ├── quantum/
│   │   ├── encoding.py
│   │   ├── qft.py
│   │   ├── oracle.py
│   │   ├── amplitude_amplification.py
│   │   ├── reconstruction.py
│   │   ├── resource_metrics.py
│   │   ├── noise_models.py
│   │   └── pipeline.py
│   └── benchmarks/
│       ├── runner.py
│       ├── statistics.py
│       ├── reports.py
│       └── plots.py
├── configs/
│   ├── ecg_mvp.yaml
│   ├── ecg_publication.yaml
│   └── splits/
├── scripts/
│   ├── download_datasets.py
│   ├── build_ecg_manifest.py
│   ├── generate_noisy_ecg.py
│   ├── run_ecg_benchmark.py
│   └── export_results.py
├── data/
│   ├── raw/
│   ├── derived/
│   └── manifests/
├── results/
│   ├── pilot/
│   ├── publication/
│   └── figures/
├── docs/
│   ├── ALGORITHM_SPEC.md
│   ├── DATASET_CARD.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── NOVELTY_NOTES.md
│   └── WEB_PRODUCT_SPEC.md
└── tests/
    ├── unit/
    ├── integration/
    ├── quantum/
    └── api/
```

---

# 4. Technology Stack

Backend/research:

- Python 3.11+
- NumPy
- SciPy
- pandas
- WFDB
- PyWavelets
- scikit-learn
- statsmodels
- matplotlib
- FastAPI
- Uvicorn
- Pydantic
- Qiskit
- Qiskit Aer

Frontend:

- Next.js
- React
- TypeScript
- Plotly.js or equivalent React wrapper

Every benchmark output MUST record:

- Python version,
- package versions,
- Qiskit version,
- Qiskit Aer version,
- OS,
- CPU,
- config hash,
- Git commit SHA,
- dataset manifest hash,
- random seed.

---

# 5. Required ECG Datasets

## D1 — MIT-BIH Noise Stress Test Database (NSTDB)

Official source:

`https://physionet.org/content/nstdb/1.0.0/`

Version:

`1.0.0`

Use as the **primary paired clean/noisy benchmark**.

Important records:

```text
118e24
118e18
118e12
118e06
118e00
118e_6

119e24
119e18
119e12
119e06
119e00
119e_6
```

Canonical SNRs:

```text
24, 18, 12, 6, 0, -6 dB
```

Official noise-only records:

```text
bw = baseline wander
ma = muscle/EMG artifact
em = electrode motion artifact
```

Use for:

- canonical stress-test table,
- paired SNR/PRD/RMSE/correlation,
- final test benchmark.

Do NOT tune final parameters on the canonical test results.

---

## D2 — MIT-BIH Arrhythmia Database

Official source:

`https://physionet.org/content/mitdb/1.0.0/`

Version:

`1.0.0`

Facts used by this project:

- 48 approximately half-hour recordings,
- 47 subjects,
- two channels,
- 360 Hz,
- expert-reviewed beat annotations.

Use for:

- development,
- validation,
- subject-diverse synthetic-noise benchmark.

Phase 1 rule:

```text
channel_index = 0
```

Store the original channel label in metadata.

Split rule:

```text
seed = 1448
70% development
15% validation
15% test
```

Use subject/group-aware splitting.

Records `201` and `202` MUST stay in the same split.

Exclude `118` and `119` from tuning if NSTDB is used as canonical final testing.

Save exact split IDs once to:

```text
configs/splits/mitdb_v1.json
```

Never silently regenerate.

---

## D3 — QT Database

Official source:

`https://physionet.org/content/qtdb/1.0.0/`

Version:

`1.0.0`

Role:

**external morphology-preservation validation**

Use a deterministic 20-record subset selected with seed 1448.

For external validation:

```text
channel = 0
noise = bw, ma, em
SNR = 0, 6, 12 dB
```

Evaluate timing of available P/QRS/T annotations.

Do not tune on this dataset if reported as external validation.

---

## D4 — PTB-XL

Official source:

`https://physionet.org/content/ptb-xl/1.0.3/`

Version:

`1.0.3`

Role:

future large-scale, 12-lead generalization.

Not required for ECG MVP.

Only add after:

- single-lead pipeline passes all gates,
- benchmark runner is stable,
- quantum segment scaling is characterized.

---

# 6. Dataset Downloader + Manifests

Implement:

```bash
python scripts/download_datasets.py --dataset nstdb
python scripts/download_datasets.py --dataset mitdb
python scripts/download_datasets.py --dataset qtdb
```

Optional later:

```bash
python scripts/download_datasets.py --dataset ptbxl
```

Raw data:

```text
data/raw/<dataset>/
```

`data/` MUST be Git-ignored.

Create:

```text
data/manifests/dataset_manifest.csv
```

Columns:

```text
dataset
version
record_id
subject_group
channel_index
channel_label
sampling_rate_hz
duration_sec
source_url
local_path
sha256
split
```

Create:

```text
data/manifests/ecg_pairs.csv
```

Columns:

```text
pair_id
dataset
clean_record_id
clean_path
noisy_path
noise_source
noise_type
target_snr_db
measured_snr_db
sampling_rate_hz
segment_start_sample
segment_length
channel_index
split
seed
```

---

# 7. Synthetic Noise Generation

Implement:

```text
qsp/modalities/ecg/noise.py
```

Supported noise:

```text
baseline_wander
muscle_artifact
electrode_motion
white_gaussian
powerline_50hz
powerline_60hz
```

Publication-primary noise:

```text
bw
ma
em
```

Main SNR grid:

```text
[-6, 0, 6, 12, 18, 24] dB
```

For clean ECG `x` and zero-mean noise `n`:

```text
Px = mean((x - mean(x))^2)
Pn = mean((n - mean(n))^2)

alpha = sqrt(Px / (Pn * 10^(SNR_target/10)))

y = x + alpha * n
```

Recalculate actual SNR.

Acceptance:

```text
abs(measured_snr_db - target_snr_db) <= 0.25 dB
```

Otherwise fail generation.

Noise offset must be deterministic from:

```text
seed + pair_id
```

Different pair IDs should use different deterministic noise offsets.

---

# 8. ECG Segmentation

For 360 Hz Phase 1:

```yaml
segment_length: 256
hop_length: 128
window: hann
```

This means:

```text
signal qubits = log2(256) = 8
segment duration ≈ 0.711 s
overlap = 50%
```

Ablation:

```text
segment_length ∈ {32,64,128,256}
```

Only powers of two allowed for quantum processing.

Windowed analysis:

```text
xw = x * hann
```

Weighted overlap-add:

```text
numerator += processed_window * hann
denominator += hann^2
output = numerator / (denominator + eps)
```

Use reflection padding.

Identity reconstruction test:

```text
RMSE < 1e-8
```

excluding padded boundary effects.

---

# 9. Classical DSP Baselines

## C0 — raw

Identifier:

```text
raw
```

No processing.

---

## C1 — Butterworth ECG band-pass

Identifier:

```text
butterworth_bandpass
```

Parameters:

```yaml
type: butterworth
order: 4
implementation: second_order_sections
zero_phase: true
lowcut_hz: 0.5
highcut_hz: 40.0
```

Use:

```text
scipy.signal.butter(..., output="sos")
scipy.signal.sosfiltfilt(...)
```

Optional powerline variant:

```yaml
notch_hz: 50.0
notch_q: 30.0
```

Do not use notch in the primary table unless the noise condition contains powerline interference.

---

## C2 — Wavelet denoising

Identifier:

```text
wavelet_db6
```

Parameters:

```yaml
wavelet: db6
threshold_mode: soft
noise_sigma_estimator: MAD
mad_scale: 0.6745
threshold: universal
max_level: 5
```

Level:

```text
level = min(5, pywt.dwt_max_level(N, wavelet.dec_len))
```

Noise estimate:

```text
sigma = median(abs(detail_coefficients)) / 0.6745
```

Threshold:

```text
T = sigma * sqrt(2 * ln(N))
```

Soft-threshold details, reconstruct, trim to original length.

---

## C3 — Classical adaptive FFT equivalent

Identifier:

```text
fft_adaptive_bandpass
```

This is the primary fair quantum comparison.

MUST use the same:

- segmentation,
- windowing,
- adaptive threshold,
- marked frequency range

as the quantum method.

Pipeline:

```text
FFT -> hard binary mask -> IFFT
```

Hard mask:

```text
mask[k] = 1 if marked
mask[k] = 0 otherwise
```

A separate soft-mask experiment may be added later.

---

# 10. ECG-Aware Adaptive Threshold

For segment `x_j`:

```text
A_j = mean(abs(x_j - median(x_j)))
```

Across the recording:

```text
q10 = percentile(A, 10)
q90 = percentile(A, 90)
```

Normalize:

```text
u_j = clip((A_j - q10) / (q90 - q10 + 1e-12), 0, 1)
```

Adaptive high cutoff:

```text
f_high_j = f_high_min + u_j * (f_high_max - f_high_min)
```

Defaults:

```yaml
f_low_hz: 0.5
f_high_min_hz: 25.0
f_high_max_hz: 45.0
```

Convert to bins:

```text
k_low = ceil(f_low_hz * M / fs)
k_high = floor(f_high_j * M / fs)
```

Symmetric marked set:

```text
marked(k) =
    k_low <= k <= k_high
    OR
    M - k_high <= k <= M - k_low
```

DC (`k=0`) is unmarked.

Store per segment:

```text
A_j
u_j
f_high_j
k_low
k_high
marked_count
```

This adaptive band-pass rule is a **research hypothesis**, not a proven improvement until validated.

---

# 11. Quantum DSP Pipeline

Main identifier:

```text
qft_grover_ecg_adaptive
```

Pipeline:

```text
ECG segment
→ Hann window
→ amplitude state preparation
→ QFT
→ ECG-aware band-pass phase oracle
→ Grover amplitude amplification
→ IQFT
→ ideal statevector reconstruction
→ rescale
→ weighted overlap-add
```

---

# 12. State Preparation

For windowed vector `v`:

```text
scale = ||v||2
```

If:

```text
scale < 1e-12
```

return an all-zero segment.

Otherwise:

```text
v_norm = v / scale
```

Prepare:

```text
|psi> = Σ_i v_norm[i] |i>
```

using Qiskit `StatePreparation` or current documented equivalent.

Record separately:

```text
encoding_time_ms
encoding_depth
encoding_gate_count
```

Do not hide this cost inside QFT runtime.

---

# 13. QFT + IQFT Correctness

Signal qubits:

```text
m = log2(M)
```

For M=256:

```text
m = 8
```

Required test:

```text
StatePreparation -> QFT -> IQFT
```

with no filtering must produce:

```text
state fidelity >= 0.999999999
```

under ideal simulation.

---

# 14. Oracle Implementations

Implement both.

## O1 — diagonal_reference

Create phase vector:

```text
phase[k] = -1 if marked(k)
phase[k] = +1 otherwise
```

Use as correctness reference.

---

## O2 — range_oracle

Implement interval/range-comparison logic for the two symmetric frequency bands.

Purpose:

- structured circuit,
- resource study,
- future hardware relevance.

For:

```text
M = 16 and 32
```

O1 and O2 MUST mark equivalent states.

---

# 15. Amplitude Amplification

Phase 1 mode:

```text
paper_grover
```

Use:

```text
oracle -> diffusion
```

Let:

```text
L = marked-state count
M = total states
```

Heuristic:

```text
r_est = floor((pi/4) * sqrt(M / max(L,1)))
```

Default:

```text
r = clip(r_est, 0, 3)
```

Ablation:

```text
r ∈ {0,1,2,3,4,5}
```

Tune on validation only.

Advanced later:

```text
state_reflection_amplitude_amplification
```

Do not block MVP on this.

---

# 16. Quantum Reconstruction

Primary waveform mode:

```text
Aer ideal statevector
```

After IQFT:

1. obtain amplitudes,
2. verify imaginary residual,
3. reconstruct real window.

Acceptance:

```text
max(abs(imag(amplitudes))) < 1e-8
```

when a real reconstruction is expected.

Reconstruct:

```text
processed_window = real(amplitudes) * original_scale
```

Then overlap-add.

Never use:

```text
measurement counts = waveform amplitudes
```

---

# 17. Noisy / Shot-Based Quantum Study

This is separate from the Phase 1 waveform benchmark.

Suggested Aer sweeps:

```yaml
single_qubit_depolarizing:
  - 0
  - 0.0001
  - 0.001
  - 0.01

two_qubit_depolarizing:
  - 0
  - 0.001
  - 0.01
  - 0.03
```

Optional:

```text
phase damping
bit flip
```

Store exact noise configuration.

Primary noisy-study outputs:

- state fidelity to ideal processed state,
- circuit/resource metrics,
- robustness vs error probability.

Do not pretend computational-basis shots recover phase.

Optional tomography only for:

```text
M ∈ {16,32}
shots ∈ {1024,4096,16384}
```

Report tomography overhead explicitly.

---

# 18. Quantum Resource Metrics

Every quantum run MUST store:

```text
segment_length
signal_qubits
ancilla_qubits
total_qubits
stateprep_depth
algorithm_depth
total_logical_depth
transpiled_depth
total_gate_count
single_qubit_gate_count
two_qubit_gate_count
cx_count
qft_depth
oracle_depth
grover_depth
iqft_depth
grover_iterations
transpile_optimization_level
simulator_backend
stateprep_time_ms
circuit_build_time_ms
transpile_time_ms
simulation_time_ms
reconstruction_time_ms
total_pipeline_time_ms
```

Default:

```text
optimization_level = 3
```

Also run optimization level 0 on a small resource-study subset.

---

# 19. Evaluation Metrics

## Reference metrics

SNR:

```text
SNR = 10 log10(sum(clean^2) / sum((clean - test)^2))
```

Store:

```text
input_snr_db
output_snr_db
snr_improvement_db
```

RMSE:

```text
sqrt(mean((clean-test)^2))
```

MAE:

```text
mean(abs(clean-test))
```

PRD:

```text
100 * ||clean-test||2 / ||clean||2
```

Pearson correlation:

```text
r(clean, processed)
```

---

## Morphology metrics

Use one documented detector, e.g. WFDB XQRS, consistently for every method.

Report:

```text
R_peak_sensitivity
R_peak_positive_predictivity
R_peak_F1
median_absolute_R_peak_timing_error_ms
```

QTDB external validation where annotations exist:

```text
P_onset_error_ms
QRS_onset_error_ms
QRS_end_error_ms
T_end_error_ms
QT_interval_error_ms
```

---

## Runtime

Store:

```text
preprocessing_ms
algorithm_ms
postprocessing_ms
total_ms
```

Quantum also stores Section 18 metrics.

---

# 20. Fair Comparison Set

Required methods:

```text
raw
butterworth_bandpass
wavelet_db6
fft_adaptive_bandpass
qft_grover_ecg_adaptive
```

Optional:

```text
qft_fixed_bandpass
qft_grover_ecg_adaptive_noisy_sim
```

Most important pair:

```text
fft_adaptive_bandpass
vs
qft_grover_ecg_adaptive
```

because they share the same frequency selection rule.

Measured runtime and theoretical complexity MUST be reported separately.

---

# 21. Pilot Benchmark

Use:

```text
10 deterministic ECG segments
per noise type
per SNR
```

Noise:

```text
bw
ma
em
```

SNR:

```text
-6, 0, 6, 12, 18, 24 dB
```

Methods:

```text
5 required methods
```

Total:

```text
10 × 3 × 6 × 5 = 900 method-runs
```

Use only for debugging and stability.

Do not make paper claims from pilot results.

---

# 22. Full Benchmark

Synthetic MIT-BIH test:

At least:

```text
50 deterministic test segments
per noise type
per SNR
```

If computationally practical:

```text
100
```

Do not let one subject dominate by contributing many more overlapping segments than others.

Also run canonical NSTDB records separately.

Keep synthetic and canonical tables separate.

---

# 23. Statistics

For every metric:

- segment-level results,
- subject/record-level aggregation,
- bootstrap 95% CI,
- paired comparisons.

Default paired test:

```text
Wilcoxon signed-rank
```

Multiple comparisons:

```text
Holm correction
```

Effect size:

```text
Cliff's delta
```

Report:

```text
median
IQR
95% CI
p
adjusted p
effect size
```

Do not report p-values alone.

---

# 24. Benchmark Output

Each run:

```text
results/<run-id>/
```

Must contain:

```text
config.yaml
environment.json
git.json
dataset_manifest_snapshot.csv
segment_results.csv
subject_summary.csv
method_summary.csv
quantum_resources.csv
statistics.csv
run.log
figures/
```

Required figures:

```text
snr_improvement_by_method.png
prd_by_method.png
rmse_by_method.png
correlation_by_method.png
morphology_f1_by_method.png
circuit_depth_vs_segment_size.png
gate_count_vs_segment_size.png
quality_vs_circuit_depth.png
quality_vs_grover_iterations.png
```

Never overwrite old runs.

---

# 25. Web Product

Pages:

```text
/
 /ecg
 /benchmark
 /research
```

## `/`

Show:

- project purpose,
- classical vs quantum concept,
- ECG-first status,
- research-use-only notice.

## `/ecg`

Allow:

- CSV upload,
- built-in PhysioNet example,
- sample-rate entry,
- method selection,
- segment-size selection.

Display:

- input ECG,
- processed ECG,
- frequency spectrum,
- metrics,
- timing,
- quantum resources if applicable.

## `/benchmark`

Allow a small interactive benchmark only.

Do not allow the UI to trigger the full publication experiment accidentally.

## `/research`

Show:

- algorithm flow,
- dataset citations,
- QFT/Grover details,
- qubit count,
- depth,
- gate count,
- current research status.

---

# 26. ECG Upload Format

MVP:

```text
.csv
```

Supported:

```csv
amplitude
0.123
0.128
```

or:

```csv
time,amplitude
0.000,0.123
0.00278,0.128
```

If time is absent, user must supply:

```text
sampling_rate_hz
```

Later:

```text
.npy
WFDB .hea/.dat
```

Do not block MVP on those.

---

# 27. Backend API

Implement:

```http
GET /api/health
GET /api/ecg/methods
GET /api/datasets/ecg/examples
POST /api/ecg/process
POST /api/benchmark/ecg
```

`POST /api/ecg/process` input:

- ECG CSV,
- sampling rate,
- method,
- parameters.

Response:

```text
input trace
processed trace
metrics
runtime
quantum metrics when relevant
```

Web benchmark endpoint MUST enforce a small run limit.

---

# 28. Main Config

Create:

```text
configs/ecg_mvp.yaml
```

with:

```yaml
project_seed: 1448

ecg:
  channel_index: 0

segmentation:
  segment_length: 256
  hop_length: 128
  window: hann

classical:
  butterworth:
    order: 4
    lowcut_hz: 0.5
    highcut_hz: 40.0
    zero_phase: true

  wavelet:
    family: db6
    mode: soft
    max_level: 5
    mad_scale: 0.6745

adaptive_threshold:
  activity_statistic: mean_absolute_deviation_from_median
  lowcut_hz: 0.5
  highcut_min_hz: 25.0
  highcut_max_hz: 45.0
  lower_percentile: 10
  upper_percentile: 90

quantum:
  simulator: aer_statevector
  encoding: amplitude
  oracle: diagonal_reference
  amplitude_amplification: paper_grover
  grover_iteration_mode: estimated_capped
  grover_iteration_cap: 3
  transpile_optimization_level: 3

benchmark:
  noise_types:
    - bw
    - ma
    - em
  snr_db:
    - -6
    - 0
    - 6
    - 12
    - 18
    - 24
```

Create `ecg_publication.yaml` only after validation.

---

# 29. Tests

## Dataset

- downloader detects missing/corrupt files,
- SHA256 exists,
- split deterministic,
- 201/202 same split,
- 118/119 not used for tuning.

## Noise

- target SNR within ±0.25 dB,
- deterministic rerun is identical,
- different pair IDs use different deterministic offsets.

## Classical DSP

- filter response matches spec,
- zero-phase behavior,
- output length unchanged,
- no NaN/Inf.

## Quantum

Identity:

```text
stateprep -> QFT -> IQFT
```

must achieve:

```text
fidelity >= 0.999999999
```

Oracle:

- frequency bins symmetric,
- diagonal and range oracle equivalent for M=16/32.

Reconstruction:

- no-filter quantum path reproduces original window numerically.

Resource metrics:

- qubits,
- depth,
- gate counts,
- timing always returned.

## Integration

One deterministic ECG pair must run through all five required methods.

## API

Test:

```text
/api/health
/api/ecg/methods
/api/ecg/process
```

---

# 30. Execution Phases

## Phase 0 — Skeleton

Build:

- directories,
- Python package,
- FastAPI health endpoint,
- frontend shell,
- configs,
- test skeleton,
- environment capture.

Gate:

```text
pytest passes
/api/health passes
frontend builds
```

---

## Phase 1 — Datasets

Build:

- NSTDB downloader,
- MIT-BIH downloader,
- dataset manifest,
- frozen group split,
- dataset card.

Gate:

- hashes present,
- splits stored,
- 201/202 grouping test passes.

---

## Phase 2 — Noise generator

Build:

- SNR-controlled injection,
- bw/ma/em support,
- pilot-pair generation.

Gate:

```text
target SNR error <= 0.25 dB
```

and deterministic rerun produces identical hashes.

---

## Phase 3 — Classical ECG DSP

Build:

- Butterworth,
- wavelet,
- adaptive FFT,
- metrics,
- R-peak evaluation.

Gate:

- tests pass,
- pilot metrics CSV generated.

---

## Phase 4 — Quantum core

Build:

- state preparation,
- QFT,
- IQFT,
- statevector simulation,
- resource metrics.

Gate:

```text
identity fidelity >= 0.999999999
```

---

## Phase 5 — ECG quantum oracle

Build:

- activity score,
- adaptive upper cutoff,
- band-pass marked states,
- diagonal oracle,
- Grover diffusion,
- IQFT reconstruction.

Gate:

- 256-sample segment runs,
- symmetric frequency set,
- output waveform valid.

---

## Phase 6 — Resource study

Run:

```text
M = 32,64,128,256
```

Produce:

```text
depth vs M
gate count vs M
stateprep cost vs total cost
```

---

## Phase 7 — Pilot benchmark

Run 900-method pilot.

Gate:

- no missing metrics,
- no crashes,
- summary figures produced.

Stop and inspect before tuning.

---

## Phase 8 — Validation tuning

Tune only on validation records:

```text
highcut_min ∈ {20,25,30}
highcut_max ∈ {40,45,50}
segment_length ∈ {64,128,256}
grover_iterations ∈ {0,1,2,3}
```

Primary objective:

```text
maximize SNR improvement
subject to morphology preservation
```

Freeze chosen parameters.

---

## Phase 9 — Final test

Run:

1. synthetic MIT-BIH test subjects,
2. canonical NSTDB,
3. no tuning.

Generate final statistics and figures.

---

## Phase 10 — QTDB external validation

Use 20 deterministic records.

Inject:

```text
bw/ma/em
0/6/12 dB
```

Evaluate morphology timing.

---

## Phase 11 — Backend

Implement all API routes and CSV processing.

Gate:

API integration tests pass.

---

## Phase 12 — Frontend

Build:

- upload,
- method selector,
- plots,
- metrics,
- quantum resource panel.

Gate:

User can run:

```text
butterworth_bandpass
fft_adaptive_bandpass
qft_grover_ecg_adaptive
```

from browser.

---

## Phase 13 — Reproducibility

Add:

- environment snapshots,
- config hashing,
- table export,
- figure export,
- clean-machine setup instructions.

Gate:

Fresh machine can reproduce pilot.

---

# 31. Publication Novelty Gate

Before using the word “novel”, create:

```text
docs/NOVELTY_NOTES.md
```

and compare at minimum:

1. Dutta et al., **Quantum Algorithm for Signal Denoising**, IEEE Signal Processing Letters, 2024.
2. Laskar et al., **A complexity efficient penta-diagonal quantum smoothing filter for bio-medical signal denoising: a study on ECG**, Scientific Reports, 2024.
3. 2026 conference paper **Quantum Fourier Transform Based Electro Cardio Gram Signal Denoising**.

Therefore, NEVER claim:

```text
"first QFT ECG denoiser"
```

without a much deeper verified literature review.

---

# 32. Candidate Publication Contributions

## A — ECG-aware quantum band-pass oracle

Instead of generic low-frequency preservation, mark a physiological band:

```text
0.5 Hz <= |f| <= adaptive high cutoff
```

This explicitly targets both:

- baseline wander below the band,
- high-frequency artifact above the band.

---

## B — QRS/activity-aware bandwidth

Adaptive high cutoff:

```text
25–45 Hz
```

based on local ECG activity.

Hypothesis:

High-activity/QRS segments need more bandwidth to preserve morphology.

---

## C — Fair FFT vs QFT comparison

Use the same adaptive frequency rule in classical FFT and quantum QFT.

---

## D — End-to-end resource accounting

Report:

- state preparation,
- QFT,
- oracle,
- amplitude amplification,
- IQFT,
- reconstruction,
- circuit depth,
- gate count.

---

## E — Quality/resource tradeoff

Study:

```text
quality vs Grover iterations
quality vs circuit depth
quality vs gate count
```

This may be publication-worthy even if measured quantum runtime is slower.

---

# 33. Research Questions

RQ1. Does ECG-aware adaptive band-pass quantum filtering outperform fixed-threshold QFT denoising?

RQ2. Does adaptive bandwidth preserve ECG morphology better than a fixed cutoff?

RQ3. How does the quantum method compare with Butterworth, wavelet and the equivalent adaptive FFT method under identical noise?

RQ4. How do segment size and Grover iterations affect quality, morphology, depth, gate count and runtime?

RQ5. What fraction of total quantum cost comes from state preparation versus the quantum algorithm itself?

RQ6. Which ECG noise types match or break the method?

Do not hide negative results.

---

# 34. Required Paper Figures

Generate:

1. architecture,
2. ECG quantum pipeline,
3. clean/noisy/classical/quantum waveform,
4. spectra,
5. SNR improvement by method/noise,
6. PRD,
7. morphology F1,
8. timing-error boxplots,
9. circuit depth vs segment size,
10. gate count vs segment size,
11. quality vs Grover iterations,
12. quality vs depth,
13. stateprep cost vs total cost,
14. adaptive cutoff over ECG activity.

---

# 35. Required Ablations

A1:

```text
fixed cutoff vs adaptive cutoff
```

A2:

```text
low-pass oracle vs ECG band-pass oracle
```

A3:

```text
Grover iterations 0/1/2/3/4/5
```

A4:

```text
M = 32/64/128/256
```

A5:

```text
diagonal oracle vs range oracle
```

A6:

```text
runtime excluding stateprep vs full end-to-end runtime
```

A6 is mandatory.

---

# 36. Definition of Done — ECG v1

- [ ] Dataset downloader works.
- [ ] NSTDB manifest reproducible.
- [ ] MIT-BIH split frozen.
- [ ] SNR injection passes tolerance.
- [ ] Butterworth works.
- [ ] Wavelet works.
- [ ] Adaptive FFT works.
- [ ] QFT/IQFT identity passes.
- [ ] ECG-aware quantum oracle works.
- [ ] M=256 quantum segment works.
- [ ] Quantum resources recorded.
- [ ] Pilot benchmark complete.
- [ ] Validation parameters frozen.
- [ ] Full test complete.
- [ ] Canonical NSTDB results separate.
- [ ] QTDB external morphology validation complete.
- [ ] Statistical analysis generated.
- [ ] API works.
- [ ] Web ECG page works.
- [ ] Clean-machine reproduction works.
- [ ] No unsupported quantum-advantage claim.
- [ ] No unsupported “first ever” claim.
- [ ] Research-use-only disclaimer visible.

---

# 37. Future Modality Interface

After ECG v1, each modality goes under:

```text
qsp/modalities/<modality>/
```

Examples:

```text
eeg/
emg/
ppg/
sensor/
audio/
rf/
image/
remote_sensing/
seismic/
radar/
sonar/
video/
```

Each must expose a common interface:

```python
load(...)
validate(...)
segment(...)
preprocess(...)
classical_methods(...)
quantum_methods(...)
metrics(...)
visualize(...)
```

Benchmark runner should remain modality-independent.

Recommended order:

1. ECG
2. EEG/EMG/PPG
3. generic sensors/time-series
4. audio
5. RF/communication
6. image/QVSVD
7. remote sensing
8. seismic
9. radar/sonar
10. video

---

# 38. Future Image/QVSVD Module

Not part of ECG v1.

Later:

```text
Image
→ matrix
→ Tensorized Pauli Decomposition
→ VQD
→ singular-value information
→ QVSVD reconstruction/compression
```

Do not mix VQD into ECG denoising unless a new ECG-specific reason is established.

---

# 39. Required CLI Commands

From `signalchain-q/`:

```bash
python -m pip install -e .

python scripts/download_datasets.py --dataset nstdb
python scripts/download_datasets.py --dataset mitdb
python scripts/build_ecg_manifest.py

python scripts/generate_noisy_ecg.py   --config configs/ecg_mvp.yaml   --split validation   --limit 10

pytest -q

python scripts/run_ecg_benchmark.py   --config configs/ecg_mvp.yaml   --mode pilot

python scripts/run_ecg_benchmark.py   --config configs/ecg_publication.yaml   --mode full-test

uvicorn backend.app.main:app --reload --port 8000

cd frontend
npm install
npm run dev
```

---

# 40. CI

CI should run:

```text
pytest
frontend typecheck
frontend build
```

Do NOT download datasets or run the full benchmark in CI.

Use tiny synthetic fixtures.

Quantum CI tests:

```text
M <= 16
```

---

# 41. Data/Security Rules

Web MVP:

- temporary uploads only,
- delete after processing,
- do not log raw ECG by default,
- file-size limits,
- numeric validation,
- reject NaN/Inf,
- never execute uploaded content,
- visible “research use only” notice.

Do not add auth/accounts in MVP unless required.

---

# 42. Error Handling

Required user-facing errors:

```text
Unsupported file format
Missing sampling rate
Signal too short
Invalid numeric values
Segment size must be a power of two
Quantum simulation failed
Insufficient memory
Dataset unavailable
```

Backend logs may contain stack traces.

Frontend must not expose internal stack traces.

---

# 43. README Requirements

`signalchain-q/README.md` must explain:

1. objective,
2. ECG-first reasoning,
3. classical methods,
4. quantum method,
5. datasets,
6. install,
7. dataset download,
8. pilot run,
9. web run,
10. limitations,
11. publication status,
12. references.

---

# 44. Key References

## Quantum denoising

Dutta, S., Basarab, A., Kouamé, D., Georgeot, B.  
**Quantum Algorithm for Signal Denoising**  
IEEE Signal Processing Letters, 31, 156–160.  
DOI: `10.1109/LSP.2023.3344071`  
Preprint: `https://arxiv.org/abs/2312.15411`

Core ideas:

```text
QFT
adaptive threshold
amplitude amplification
IQFT
```

## Quantum ECG prior work

Laskar et al.  
**A complexity efficient penta-diagonal quantum smoothing filter for bio-medical signal denoising: a study on ECG**  
Scientific Reports 14, 10580 (2024)  
`https://www.nature.com/articles/s41598-024-59851-5`

## PhysioNet

MIT-BIH Arrhythmia Database:  
`https://physionet.org/content/mitdb/1.0.0/`

MIT-BIH Noise Stress Test Database:  
`https://physionet.org/content/nstdb/1.0.0/`

QT Database:  
`https://physionet.org/content/qtdb/1.0.0/`

PTB-XL:  
`https://physionet.org/content/ptb-xl/1.0.3/`

---

# 45. Final Product Statement

Use:

> **SignalChain-Q is a web-based classical–quantum signal-processing research platform that benchmarks ECG denoising methods under identical noise conditions. It combines conventional ECG DSP baselines with QFT-based quantum denoising, an ECG-aware adaptive band-pass oracle, amplitude amplification and detailed quantum resource accounting.**

Do NOT describe it as:

```text
a medical diagnosis system
a guaranteed quantum-advantage system
a real-time quantum ECG device
the first QFT ECG denoiser
```

---

# 46. Immediate First Codex Task

Codex should begin with ONLY:

```text
1. Create signalchain-q/ skeleton.
2. Add Python project config.
3. Add FastAPI /api/health.
4. Add Next.js frontend shell.
5. Implement NSTDB + MIT-BIH downloader.
6. Build dataset manifest.
7. Build deterministic MIT-BIH split.
8. Implement SNR-controlled noise mixing.
9. Add tests for split and target SNR.
10. STOP and produce a Phase 0–2 status report before quantum circuits.
```

Status report must list:

```text
files created
tests passed
datasets downloaded
manifest counts
split counts
known issues
next exact phase
```

Only continue into classical/quantum DSP after Phase 0–2 gates pass.

---

# 47. Final Rule

The project succeeds if it produces a **reproducible scientific result**, even if the quantum method is worse than the classical method.

A result such as:

> “The quantum method preserves ECG morphology under selected noise regimes but has significantly larger end-to-end cost because of state preparation and circuit depth.”

is scientifically useful and stronger than an unsupported claim of quantum advantage.
