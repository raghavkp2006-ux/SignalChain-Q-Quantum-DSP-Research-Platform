"""Benchmark runner, statistics, reports, and plotting."""
from qsp.benchmarks.plots import plot_circuit_scaling, plot_metric_by_method
from qsp.benchmarks.reports import save_benchmark_run_artifacts
from qsp.benchmarks.runner import REQUIRED_METHODS, run_benchmark_on_segments
from qsp.benchmarks.statistics import (
    apply_holm_bonferroni,
    calculate_bootstrap_ci,
    calculate_cliffs_delta,
    compute_paired_comparison_statistics,
)

__all__ = [
    "REQUIRED_METHODS",
    "run_benchmark_on_segments",
    "calculate_bootstrap_ci",
    "calculate_cliffs_delta",
    "apply_holm_bonferroni",
    "compute_paired_comparison_statistics",
    "save_benchmark_run_artifacts",
    "plot_metric_by_method",
    "plot_circuit_scaling",
]
