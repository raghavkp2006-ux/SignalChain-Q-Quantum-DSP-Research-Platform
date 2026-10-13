# SignalChain-Q Dataset Card

## 1. Datasets & Roles

| Dataset | PhysioNet Slug | Version | Primary Role | Sampling Rate | Channels |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NSTDB** | `nstdb` | 1.0.0 | Primary paired clean/noisy benchmark | 360 Hz | 2 (Lead 0) |
| **MIT-BIH** | `mitdb` | 1.0.0 | Development & subject-diverse synthetic noise | 360 Hz | 2 (Lead 0) |
| **QTDB** | `qtdb` | 1.0.0 | External morphology-preservation validation | 250 Hz | 2 (Lead 0) |

## 2. Deterministic MIT-BIH Arrhythmia Database Split

- **Config Path:** `configs/splits/mitdb_v1.json`
- **Random Seed:** `1448`
- **Subject-Aware Grouping:** Records `201` and `202` (originating from the same patient) are kept in the same split (`validation`).
- **Clean Baselines:** Records `118` and `119` are excluded from tuning and placed strictly in `test`.

### Split Partitioning:
- **Development (70%):** 33 records (100, 101, 102, 103, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 117, 121, 122, 123, 124, 200, 203, 205, 208, 209, 210, 212, 213, 214, 219, 220, 221, 228)
- **Validation (15%):** 8 records (104, 201, 202, 215, 217, 222, 223, 230)
- **Test (15%):** 7 records (118, 119, 207, 231, 232, 233, 234)

## 3. Data Integrity & Git Rules
- Waveform binaries (`.dat`, `.hea`, `.atr`) are strictly **Git-ignored** under `data/raw/` and `data/derived/`.
- Every downloaded record is tracked with SHA256 checksums in `data/manifests/dataset_manifest.csv`.
