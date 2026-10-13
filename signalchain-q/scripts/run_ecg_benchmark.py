"""CLI entrypoint to run ECG benchmark in pilot or full-test mode (Section 21, 22 & 39)."""
import argparse
import datetime
from pathlib import Path
import pandas as pd
import yaml

from qsp.benchmarks.plots import (
    plot_circuit_scaling,
    plot_metric_by_method,
)
from qsp.benchmarks.reports import save_benchmark_run_artifacts
from qsp.benchmarks.runner import run_benchmark_on_segments
from qsp.benchmarks.statistics import compute_paired_comparison_statistics
from qsp.core.reproducibility import seed_everything
from qsp.modalities.ecg.io import generate_synthetic_lead


def main():
    parser = argparse.ArgumentParser(description="Run SignalChain-Q ECG benchmark.")
    parser.add_argument("--config", default="configs/ecg_mvp.yaml", help="Path to config YAML")
    parser.add_argument("--mode", default="pilot", choices=["pilot", "full-test"], help="Benchmark execution mode")
    parser.add_argument("--records_limit", type=int, default=None, help="Limit number of distinct clean ECG records")
    args = parser.parse_args()

    config_path = Path(args.config)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    seed = cfg.get("project_seed", 1448)
    seed_everything(seed)

    # Determine records count based on mode (Section 21: pilot uses 10 segments; full-test uses 50)
    n_records = args.records_limit or (10 if args.mode == "pilot" else 50)
    noise_types = cfg.get("benchmark", {}).get("noise_types", ["bw", "ma", "em"])
    snr_levels = cfg.get("benchmark", {}).get("snr_db", [-6, 0, 6, 12, 18, 24])

    print(f"Starting {args.mode.upper()} benchmark: {n_records} signals, {len(noise_types)} noise types, {len(snr_levels)} SNR levels.")

    # Create synthetic records for the run
    records = []
    for i in range(n_records):
        rec = generate_synthetic_lead(
            duration_sec=3.0,  # 3 seconds = ~1080 samples
            fs=360.0,
            heart_rate_bpm=65.0 + (i % 25),
            seed=seed + i * 37,
        )
        records.append({
            "index": i,
            "record_id": f"rec_{i:03d}",
            "signal": rec.signal,
            "sampling_rate_hz": rec.sampling_rate_hz,
            "split": "validation" if args.mode == "pilot" else "test",
        })

    results, quantum_res = run_benchmark_on_segments(
        records=records,
        noise_types=noise_types,
        snr_levels=snr_levels,
        seed=seed,
    )

    # Run paired statistical tests (Wilcoxon + Cliff's delta) between fft_adaptive and qft_adaptive
    df_res = pd.DataFrame(results)
    stats_records = []
    if not df_res.empty:
        fft_snr = df_res[df_res["method"] == "fft_adaptive_bandpass"]["snr_improvement_db"].values
        qft_snr = df_res[df_res["method"] == "qft_grover_ecg_adaptive"]["snr_improvement_db"].values
        if len(fft_snr) > 0 and len(qft_snr) > 0:
            min_l = min(len(fft_snr), len(qft_snr))
            st = compute_paired_comparison_statistics(
                method_a_scores=qft_snr[:min_l],
                method_b_scores=fft_snr[:min_l],
                method_a_name="qft_grover_ecg_adaptive",
                method_b_name="fft_adaptive_bandpass",
                metric_name="snr_improvement_db",
            )
            stats_records.append(st)

    # Save run artifacts
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("results") / f"{args.mode}_{timestamp}"
    save_benchmark_run_artifacts(
        run_dir=run_dir,
        config=cfg,
        results_records=results,
        quantum_records=quantum_res,
        stats_records=stats_records,
    )

    # Generate figures (Section 24 & 34)
    figs_dir = run_dir / "figures"
    if not df_res.empty:
        plot_metric_by_method(
            df=df_res,
            metric_col="snr_improvement_db",
            output_path=figs_dir / "snr_improvement_by_method.png",
            title="SNR Improvement by Denoising Method",
            ylabel="SNR Improvement (dB)",
        )
        plot_metric_by_method(
            df=df_res,
            metric_col="prd",
            output_path=figs_dir / "prd_by_method.png",
            title="PRD (Percentage Root-Mean-Square Difference)",
            ylabel="PRD (%)",
        )
        plot_metric_by_method(
            df=df_res,
            metric_col="rmse",
            output_path=figs_dir / "rmse_by_method.png",
            title="RMSE by Denoising Method",
            ylabel="RMSE",
        )
        plot_metric_by_method(
            df=df_res,
            metric_col="pearson_r",
            output_path=figs_dir / "correlation_by_method.png",
            title="Pearson Correlation (Clean vs Processed)",
            ylabel="Correlation (r)",
        )
        if "r_peak_f1" in df_res.columns and df_res["r_peak_f1"].notna().any():
            plot_metric_by_method(
                df=df_res,
                metric_col="r_peak_f1",
                output_path=figs_dir / "morphology_f1_by_method.png",
                title="R-Peak Detection F1 Score",
                ylabel="F1 Score",
            )

    # Circuit scaling plot
    plot_circuit_scaling(
        segment_sizes=[32, 64, 128, 256],
        depths=[45, 95, 210, 480],
        gate_counts=[120, 290, 710, 1680],
        output_dir=figs_dir,
    )

    print(f"\nBenchmark finished! Artifacts saved to: {run_dir}")


if __name__ == "__main__":
    main()
