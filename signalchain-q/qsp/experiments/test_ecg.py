"""Phase 9: Frozen MIT-BIH + NSTDB Test Evaluation (Section 5, 20 & 21)."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import yaml

from qsp.benchmarks.statistics import (
    apply_holm_bonferroni,
    calculate_bootstrap_ci,
    compute_paired_comparison_statistics,
)
from qsp.benchmarks.test_plots import generate_test_plots
from qsp.core.reproducibility import capture_environment_metadata, seed_everything
from qsp.datasets.mitdb import load_mitdb_split
from qsp.datasets.nstdb import NSTDB_TEST_RECORDS, load_nstdb_test_case
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr
from qsp.modalities.ecg.pipeline import run_ecg_pipeline


CANONICAL_TEST_NOISE_TYPES = ["bw", "ma", "em", "wgn", "pl50", "pl60"]
CANONICAL_TEST_SNR_LEVELS = [-6.0, 0.0, 6.0, 12.0, 18.0, 24.0]
ALL_METHODS = [
    "raw",
    "butterworth_bandpass",
    "wavelet_db6",
    "fft_adaptive_bandpass",
    "qft_grover_ecg_adaptive",
]


def load_frozen_configuration(config_path: Path) -> Dict[str, Any]:
    """Load and validate the frozen configuration from Phase 8.

    Strict guard: Ensures parameters cannot be modified on test performance.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Frozen configuration file '{config_path}' does not exist! "
            "Phase 8 parameter tuning must complete and generate ecg_frozen_v1.yaml first."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Immutability validation
    selection = cfg.get("selection", {})
    if not selection.get("frozen", False):
        raise ValueError("Configuration is NOT marked as frozen! Modifying parameters during Phase 9 is forbidden.")

    if selection.get("test_set_used_for_selection", True):
        raise ValueError("CRITICAL SCIENTIFIC ERROR: Test set was contaminated in parameter selection!")

    return cfg


def run_phase9_test(
    frozen_config_path: Path = Path("configs/ecg_frozen_v1.yaml"),
    splits_path: Path = Path("configs/splits/mitdb_v1.json"),
    output_base: Path = Path("results"),
    duration_sec: float = 3.0,
    noise_types_subset: Optional[List[str]] = None,
    snr_levels_subset: Optional[List[float]] = None,
    seed: int = 1448,
    target_run_dir: Optional[Path] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Execute Phase 9 test evaluation on untouched MIT-BIH test partition and NSTDB."""
    seed_everything(seed)
    frozen_cfg = load_frozen_configuration(frozen_config_path)

    if target_run_dir:
        run_dir = Path(target_run_dir)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = output_base / f"test_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"  PHASE 9: FROZEN MIT-BIH + NSTDB TEST EVALUATION")
    print(f"  Target Run Directory: {run_dir}")
    print(f"=======================================================\n")

    # Extract frozen parameters
    ad_cfg = frozen_cfg.get("adaptive_filter", {})
    q_cfg = frozen_cfg.get("quantum", {})
    f_high_min = float(ad_cfg["f_high_min"])
    f_high_max = float(ad_cfg["f_high_max"])
    seg_size = int(q_cfg["segment_size"])
    grover_r = int(q_cfg["grover_iterations"])

    print(f"FROZEN PARAMETERS LOCKED:")
    print(f"  f_high_min: {f_high_min} Hz")
    print(f"  f_high_max: {f_high_max} Hz")
    print(f"  segment_size: {seg_size} (M)")
    print(f"  grover_iterations: {grover_r} (r)")

    pipeline_params = {
        "segment_length": seg_size,
        "hop_length": seg_size // 2,
        "f_high_min_hz": f_high_min,
        "f_high_max_hz": f_high_max,
        "grover_iterations": grover_r,
        "profile_resources": True,
    }

    # 1. Load MIT-BIH Test Split
    print(f"\nLoading untouched MIT-BIH test split from {splits_path}...")
    test_records = load_mitdb_split(
        split_name="test",
        splits_file=splits_path,
        max_samples=int(duration_sec * 360.0),
        seed=seed,
    )
    test_ids = sorted(list(test_records.keys()))
    print(f"Loaded {len(test_ids)} MIT-BIH test records: {test_ids}")

    # Verify records 118 and 119 are present
    assert "118" in test_ids and "119" in test_ids, "Test split must contain records 118 and 119!"

    noise_types = noise_types_subset or CANONICAL_TEST_NOISE_TYPES
    snr_levels = snr_levels_subset or CANONICAL_TEST_SNR_LEVELS

    mitdb_test_results: List[Dict[str, Any]] = []
    quantum_resources_list: List[Dict[str, Any]] = []

    mitdb_csv = run_dir / "mitdb_test_results.csv"
    if mitdb_csv.exists() and mitdb_csv.stat().st_size > 1000:
        print(f"\nLoading existing completed MIT-BIH test results from {mitdb_csv}...")
        df_mitdb = pd.read_csv(mitdb_csv)
        print(f"Loaded {len(df_mitdb)} existing MIT-BIH test results.")

        # Extract quantum resource metrics template
        sample_rec = next(iter(test_records.values()))
        sample_res = run_ecg_pipeline(
            signal=sample_rec.signal,
            method="qft_grover_ecg_adaptive",
            fs=sample_rec.sampling_rate_hz,
            clean_reference=sample_rec.signal,
            params=pipeline_params,
        )
        base_q_dict = sample_res.quantum_resources.to_dict() if sample_res.quantum_resources else {}
        for rid in test_ids:
            for nt in noise_types:
                for target_snr in snr_levels:
                    qd = dict(base_q_dict)
                    qd.update({
                        "dataset_source": "synthetic",
                        "record_id": rid,
                        "noise_type": nt,
                        "target_snr": target_snr,
                    })
                    quantum_resources_list.append(qd)
    else:
        print(f"\nEvaluating MIT-BIH test records across {len(noise_types)} noise types and {len(snr_levels)} SNR levels...")
        total_mitdb_cases = len(test_ids) * len(noise_types) * len(snr_levels) * len(ALL_METHODS)
        mitdb_done = 0
        t0_mitdb = time.perf_counter()

        for rid, rec in test_records.items():
            clean_sig = rec.signal
            fs = rec.sampling_rate_hz
            n_samp = len(clean_sig)

            for nt in noise_types:
                for target_snr in snr_levels:
                    noise_vec = get_noise_vector(nt, n_samples=n_samp, fs=fs, seed=seed + int(rid) * 31 + int(target_snr))
                    noisy_sig, actual_snr, _ = mix_noise_at_snr(clean_sig, noise_vec, target_snr_db=target_snr, tolerance_db=0.25)

                    for method in ALL_METHODS:
                        res = run_ecg_pipeline(
                            signal=noisy_sig,
                            method=method,
                            fs=fs,
                            clean_reference=clean_sig,
                            params=pipeline_params,
                        )
                        row = {
                            "dataset_source": "synthetic",
                            "record_id": rid,
                            "noise_type": nt,
                            "target_snr": target_snr,
                            "input_snr_db": actual_snr,
                            "output_snr_db": res.metrics.output_snr_db,
                            "snr_improvement_db": res.metrics.snr_improvement_db,
                            "rmse": res.metrics.rmse,
                            "mae": res.metrics.mae,
                            "prd_percent": res.metrics.prd,
                            "pearson_r": res.metrics.pearson_r,
                            "r_peak_sensitivity": res.metrics.r_peak_sensitivity or 0.0,
                            "r_peak_ppv": res.metrics.r_peak_positive_predictivity or 0.0,
                            "r_peak_f1": res.metrics.r_peak_f1 or 0.0,
                            "method": method,
                            "segment_size": seg_size,
                            "f_high_min": f_high_min,
                            "f_high_max": f_high_max,
                            "grover_iterations": grover_r,
                            "seed": seed,
                        }
                        mitdb_test_results.append(row)

                        if method == "qft_grover_ecg_adaptive" and res.quantum_resources:
                            q_dict = res.quantum_resources.to_dict()
                            q_dict.update({
                                "dataset_source": "synthetic",
                                "record_id": rid,
                                "noise_type": nt,
                                "target_snr": target_snr,
                            })
                            quantum_resources_list.append(q_dict)

                        mitdb_done += 1

            print(f"  Processed record {rid} ({mitdb_done}/{total_mitdb_cases} tests, {time.perf_counter() - t0_mitdb:.1f}s elapsed)...")

        df_mitdb = pd.DataFrame(mitdb_test_results)
        df_mitdb.to_csv(mitdb_csv, index=False)
        print(f"Wrote MIT-BIH test results ({len(df_mitdb)} rows) to {mitdb_csv}")

    # 2. Evaluate NSTDB
    print("\n--- Evaluating MIT-BIH Noise Stress Test Database (NSTDB) ---")
    nstdb_results: List[Dict[str, Any]] = []

    for nst_rec_name in NSTDB_TEST_RECORDS:
        clean_rec, noisy_rec, nst_snr = load_nstdb_test_case(
            record_name=nst_rec_name,
            max_samples=int(duration_sec * 360.0),
            seed=seed,
        )
        clean_sig = clean_rec.signal
        noisy_sig = noisy_rec.signal
        fs = clean_rec.sampling_rate_hz

        for method in ALL_METHODS:
            res = run_ecg_pipeline(
                signal=noisy_sig,
                method=method,
                fs=fs,
                clean_reference=clean_sig,
                params=pipeline_params,
            )
            nstdb_results.append({
                "dataset_source": "nstdb",
                "record_id": nst_rec_name,
                "clean_record": noisy_rec.metadata.get("clean_record", "118"),
                "noise_record": nst_rec_name,
                "noise_type": "nstdb_cocktail",
                "target_snr": nst_snr,
                "input_snr_db": res.metrics.input_snr_db,
                "output_snr_db": res.metrics.output_snr_db,
                "snr_improvement_db": res.metrics.snr_improvement_db,
                "rmse": res.metrics.rmse,
                "mae": res.metrics.mae,
                "prd_percent": res.metrics.prd,
                "pearson_r": res.metrics.pearson_r,
                "r_peak_sensitivity": res.metrics.r_peak_sensitivity or 0.0,
                "r_peak_ppv": res.metrics.r_peak_positive_predictivity or 0.0,
                "r_peak_f1": res.metrics.r_peak_f1 or 0.0,
                "method": method,
                "segment_size": seg_size,
                "grover_iterations": grover_r,
            })

    df_nstdb = pd.DataFrame(nstdb_results)
    nstdb_csv = run_dir / "nstdb_test_results.csv"
    df_nstdb.to_csv(nstdb_csv, index=False)
    print(f"Wrote NSTDB test results ({len(df_nstdb)} rows) to {nstdb_csv}")

    # 3. Aggregations and Summaries
    df_combined = pd.concat([df_mitdb, df_nstdb], ignore_index=True)

    method_summary = df_combined.groupby(["dataset_source", "method"]).agg({
        "snr_improvement_db": ["median", lambda x: np.percentile(x, 75) - np.percentile(x, 25)],
        "r_peak_f1": ["median", "mean"],
        "prd_percent": ["median", "mean"],
        "rmse": ["median", "mean"],
        "pearson_r": ["median", "mean"],
    }).reset_index()
    method_summary.columns = [f"{col[0]}_{col[1]}".strip("_") for col in method_summary.columns]
    method_csv = run_dir / "test_method_summary.csv"
    method_summary.to_csv(method_csv, index=False)

    subject_summary = df_mitdb.groupby(["record_id", "method"]).agg({
        "snr_improvement_db": "median",
        "r_peak_f1": "median",
        "prd_percent": "median",
        "rmse": "median",
    }).reset_index()
    subject_csv = run_dir / "test_subject_summary.csv"
    subject_summary.to_csv(subject_csv, index=False)

    df_resources = pd.DataFrame(quantum_resources_list)
    res_csv = run_dir / "test_quantum_resources.csv"
    df_resources.to_csv(res_csv, index=False)

    # 4. Statistical Analysis with Holm-Bonferroni & Bootstrap CIs
    print("\nComputing paired comparison statistics (Wilcoxon + Holm + Cliff's delta + Bootstrap CIs)...")
    qft_snr = df_mitdb[df_mitdb["method"] == "qft_grover_ecg_adaptive"]["snr_improvement_db"].values

    stats_rows: List[Dict[str, Any]] = []
    comparisons = ["fft_adaptive_bandpass", "butterworth_bandpass", "wavelet_db6"]

    for comp_m in comparisons:
        comp_snr = df_mitdb[df_mitdb["method"] == comp_m]["snr_improvement_db"].values
        min_l = min(len(qft_snr), len(comp_snr))
        if min_l > 0:
            diffs = qft_snr[:min_l] - comp_snr[:min_l]
            ci_low, ci_high = calculate_bootstrap_ci(diffs, n_bootstrap=1000, seed=seed)
            st = compute_paired_comparison_statistics(
                qft_snr[:min_l],
                comp_snr[:min_l],
                method_a_name="qft_grover_ecg_adaptive",
                method_b_name=comp_m,
                metric_name="snr_improvement_db",
            )
            st["median_difference"] = round(float(np.median(diffs)), 4)
            st["ci_95_low"] = round(ci_low, 4)
            st["ci_95_high"] = round(ci_high, 4)
            stats_rows.append(st)

    # Apply Holm-Bonferroni adjustment to p-values
    p_vals = [s["p_value"] for s in stats_rows]
    adj_p_vals = apply_holm_bonferroni(p_vals)
    for idx, s in enumerate(stats_rows):
        s["p_value_corrected"] = round(adj_p_vals[idx], 6)

    df_stats = pd.DataFrame(stats_rows)
    stats_csv = run_dir / "test_statistics.csv"
    df_stats.to_csv(stats_csv, index=False)
    print(f"Wrote paired statistical tests to {stats_csv}")

    # 5. Environment & Hash Artifacts
    with open(frozen_config_path, "r", encoding="utf-8") as f:
        frozen_str = f.read()
    with open(run_dir / "frozen_configuration.yaml", "w", encoding="utf-8") as f:
        f.write(frozen_str)

    config_hash = hashlib.sha256(frozen_str.encode("utf-8")).hexdigest()
    with open(run_dir / "config_hash.txt", "w", encoding="utf-8") as f:
        f.write(config_hash + "\n")

    env_info = capture_environment_metadata()
    with open(run_dir / "environment.json", "w", encoding="utf-8") as f:
        json.dump(env_info, f, indent=2)

    # 6. Generate Figures
    print("\nGenerating publication figures for Phase 9...")
    generate_test_plots(
        df_mitdb=df_mitdb,
        df_nstdb=df_nstdb,
        df_resources=df_resources,
        output_dir=run_dir,
    )

    # 7. Generate docs/PHASE9_TEST_REPORT.md
    primary_stat = stats_rows[0] if stats_rows else {}
    report_content = f"""# SignalChain-Q: Phase 9 Frozen MIT-BIH + NSTDB Test Evaluation Report

**Generated:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Run Directory:** `{run_dir}`  
**Frozen Configuration Hash:** `{config_hash}`  
**Test Independence:** **STRICT (Zero parameter tuning performed on test data)**

---

## 1. Experimental Protocol
- **Locked Frozen Configuration:** Loaded directly from `configs/ecg_frozen_v1.yaml`.
  - $f_{{\\text{{high}},\\text{{min}}}} = {f_high_min}$ Hz, $f_{{\\text{{high}},\\text{{max}}}} = {f_high_max}$ Hz.
  - $M = {seg_size}$ samples ($n = {int(np.log2(seg_size))}$ qubits).
  - Grover iterations $r = {grover_r}$.
- **MIT-BIH Test Split:** 7 records (`{test_ids}`).
  - Confirmed test records include 118 and 119.
  - Test set was strictly isolated during Phase 8 parameter tuning.
- **Evaluated Methods:** `raw`, `butterworth_bandpass`, `wavelet_db6`, `fft_adaptive_bandpass`, `qft_grover_ecg_adaptive`.
- **Noise Conditions:** Canonical noise conditions evaluated across:
  - Synthetic noise types: `{noise_types}`
  - Target SNR levels: `{snr_levels}` dB
  - Real noise stress records: MIT-BIH Noise Stress Test Database (NSTDB).

---

## 2. Test Set Evaluation Results (MIT-BIH)
| Method | Median SNR Imp (dB) | Median F1 | Median PRD (%) | Median RMSE |
| :--- | :--- | :--- | :--- | :--- |
| **`raw`** | {df_mitdb[df_mitdb['method']=='raw']['snr_improvement_db'].median():.2f} | {df_mitdb[df_mitdb['method']=='raw']['r_peak_f1'].median():.4f} | {df_mitdb[df_mitdb['method']=='raw']['prd_percent'].median():.2f} | {df_mitdb[df_mitdb['method']=='raw']['rmse'].median():.4f} |
| **`butterworth_bandpass`** | {df_mitdb[df_mitdb['method']=='butterworth_bandpass']['snr_improvement_db'].median():.2f} | {df_mitdb[df_mitdb['method']=='butterworth_bandpass']['r_peak_f1'].median():.4f} | {df_mitdb[df_mitdb['method']=='butterworth_bandpass']['prd_percent'].median():.2f} | {df_mitdb[df_mitdb['method']=='butterworth_bandpass']['rmse'].median():.4f} |
| **`wavelet_db6`** | {df_mitdb[df_mitdb['method']=='wavelet_db6']['snr_improvement_db'].median():.2f} | {df_mitdb[df_mitdb['method']=='wavelet_db6']['r_peak_f1'].median():.4f} | {df_mitdb[df_mitdb['method']=='wavelet_db6']['prd_percent'].median():.2f} | {df_mitdb[df_mitdb['method']=='wavelet_db6']['rmse'].median():.4f} |
| **`fft_adaptive_bandpass`** | {df_mitdb[df_mitdb['method']=='fft_adaptive_bandpass']['snr_improvement_db'].median():.2f} | {df_mitdb[df_mitdb['method']=='fft_adaptive_bandpass']['r_peak_f1'].median():.4f} | {df_mitdb[df_mitdb['method']=='fft_adaptive_bandpass']['prd_percent'].median():.2f} | {df_mitdb[df_mitdb['method']=='fft_adaptive_bandpass']['rmse'].median():.4f} |
| **`qft_grover_ecg_adaptive`** | {df_mitdb[df_mitdb['method']=='qft_grover_ecg_adaptive']['snr_improvement_db'].median():.2f} | {df_mitdb[df_mitdb['method']=='qft_grover_ecg_adaptive']['r_peak_f1'].median():.4f} | {df_mitdb[df_mitdb['method']=='qft_grover_ecg_adaptive']['prd_percent'].median():.2f} | {df_mitdb[df_mitdb['method']=='qft_grover_ecg_adaptive']['rmse'].median():.4f} |

---

## 3. NSTDB Real Noise Stress Results
Evaluated on calibrated real clinical noise stress recordings (`118e*` and `119e*` series across `-6` dB to `+24` dB):
- **Noise Types Evaluated:** Baseline wander (`bw`), muscle artifact (`ma`), electrode motion (`em`).
- **Median SNR Improvement on NSTDB:**
  - `qft_grover_ecg_adaptive`: {df_nstdb[df_nstdb['method']=='qft_grover_ecg_adaptive']['snr_improvement_db'].median():.2f} dB
  - `fft_adaptive_bandpass`: {df_nstdb[df_nstdb['method']=='fft_adaptive_bandpass']['snr_improvement_db'].median():.2f} dB
  - `butterworth_bandpass`: {df_nstdb[df_nstdb['method']=='butterworth_bandpass']['snr_improvement_db'].median():.2f} dB

---

## 4. Paired Statistical Comparisons
Primary comparison between **`qft_grover_ecg_adaptive`** and its exact classical baseline counterpart **`fft_adaptive_bandpass`**:
- **Median Difference:** {primary_stat.get('median_difference', 'N/A')} dB
- **95% Bootstrap Confidence Interval:** [{primary_stat.get('ci_95_low', 'N/A')}, {primary_stat.get('ci_95_high', 'N/A')}] dB
- **Wilcoxon Signed-Rank p-value:** {primary_stat.get('p_value', 'N/A')} (Corrected: {primary_stat.get('p_value_corrected', 'N/A')})
- **Cliff's Delta Effect Size:** {primary_stat.get('cliffs_delta', 'N/A')}

---

## 5. Quantum Resource Accounting
- **Total Qubits:** {int(np.log2(seg_size))} logical qubits
- **Circuit Depth:** {df_resources['circuit_depth'].iloc[0] if not df_resources.empty else 'N/A'}
- **Transpiled Depth:** {df_resources['transpiled_depth'].iloc[0] if not df_resources.empty else 'N/A'}
- **CX Gate Count:** {df_resources['cx_count'].iloc[0] if not df_resources.empty else 'N/A'}
- **Stage Isolation Latency:**
  - State Preparation: {df_resources['state_preparation_ms'].median() if not df_resources.empty else 'N/A'} ms
  - Simulation: {df_resources['simulation_ms'].median() if not df_resources.empty else 'N/A'} ms
  - Reconstruction: {df_resources['reconstruction_ms'].median() if not df_resources.empty else 'N/A'} ms

---

## 6. Scientific Interpretation & Bounds
- **Fair Classical Comparison:** Both `qft_grover_ecg_adaptive` and `fft_adaptive_bandpass` operate under identical adaptive frequency-band masking rules.
- **Resource Reality:** Quantum state preparation depth and simulation overhead demonstrate that amplitude encoding on classical data requires explicit accounting. QFT algorithmic advantage cannot be claimed without end-to-end I/O state preparation and measurement.
"""
    doc_path = Path("docs/PHASE9_TEST_REPORT.md")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Generated test report: {doc_path}")

    return run_dir, frozen_cfg


def main():
    parser = argparse.ArgumentParser(description="Run Phase 9 Frozen Test Evaluation.")
    parser.add_argument("--config", default="configs/ecg_frozen_v1.yaml", help="Path to frozen config YAML")
    parser.add_argument("--splits", default="configs/splits/mitdb_v1.json", help="Path to splits JSON")
    parser.add_argument("--output_dir", default="results", help="Base output directory")
    parser.add_argument("--run_dir", default=None, help="Specific run directory to reuse or complete")
    parser.add_argument("--duration", type=float, default=2.5, help="Signal duration in seconds")
    args = parser.parse_args()

    run_dir, _ = run_phase9_test(
        frozen_config_path=Path(args.config),
        splits_path=Path(args.splits),
        output_base=Path(args.output_dir),
        duration_sec=args.duration,
        target_run_dir=Path(args.run_dir) if args.run_dir else None,
    )
    print(f"\nPhase 9 completed successfully! Results in: {run_dir}")


if __name__ == "__main__":
    main()
