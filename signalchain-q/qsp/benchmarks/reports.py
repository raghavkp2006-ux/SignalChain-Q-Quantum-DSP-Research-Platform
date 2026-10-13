"""Benchmark report generation, CSV export, and run artifact saving (Section 24)."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import yaml
from qsp.core.reproducibility import capture_environment_metadata


def save_benchmark_run_artifacts(
    run_dir: Path,
    config: Dict[str, Any],
    results_records: List[Dict[str, Any]],
    quantum_records: List[Dict[str, Any]],
    stats_records: List[Dict[str, Any]],
    manifest_df: Optional[pd.DataFrame] = None,
) -> None:
    """Save all Section 24 benchmark files in results/<run-id>/."""
    run_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = run_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. config.yaml
    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False)

    # 2. environment.json & git.json
    env_meta = capture_environment_metadata()
    with open(run_dir / "environment.json", "w", encoding="utf-8") as f:
        json.dump(env_meta, f, indent=2)

    with open(run_dir / "git.json", "w", encoding="utf-8") as f:
        json.dump({"git_commit": env_meta.get("git_commit", "unknown")}, f, indent=2)

    # 3. dataset_manifest_snapshot.csv
    if manifest_df is not None:
        manifest_df.to_csv(run_dir / "dataset_manifest_snapshot.csv", index=False)

    # 4. segment_results.csv
    seg_df = pd.DataFrame(results_records)
    seg_df.to_csv(run_dir / "segment_results.csv", index=False)

    # 5. method_summary.csv
    if not seg_df.empty and "method" in seg_df.columns:
        method_summary = seg_df.groupby("method").agg(
            median_snr_imp=("snr_improvement_db", "median"),
            median_rmse=("rmse", "median"),
            median_prd=("prd", "median"),
            median_corr=("pearson_r", "median"),
            median_f1=("r_peak_f1", "median"),
            count=("snr_improvement_db", "count"),
        ).reset_index()
        method_summary.to_csv(run_dir / "method_summary.csv", index=False)

    # 6. subject_summary.csv
    if not seg_df.empty and "record_id" in seg_df.columns:
        subj_summary = seg_df.groupby(["record_id", "method"]).agg(
            median_snr_imp=("snr_improvement_db", "median"),
            median_rmse=("rmse", "median"),
            median_prd=("prd", "median"),
        ).reset_index()
        subj_summary.to_csv(run_dir / "subject_summary.csv", index=False)

    # 7. quantum_resources.csv
    q_df = pd.DataFrame(quantum_records)
    q_df.to_csv(run_dir / "quantum_resources.csv", index=False)

    # 8. statistics.csv
    st_df = pd.DataFrame(stats_records)
    st_df.to_csv(run_dir / "statistics.csv", index=False)

    # 9. run.log
    with open(run_dir / "run.log", "w", encoding="utf-8") as f:
        f.write(f"Run completed successfully with {len(results_records)} segment evaluations.\n")
