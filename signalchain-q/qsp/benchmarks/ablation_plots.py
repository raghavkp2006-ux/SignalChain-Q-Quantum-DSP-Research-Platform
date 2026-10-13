"""Publication plotting functions for Ablation Studies A, B, C, and D."""
from pathlib import Path
from typing import Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from qsp.benchmarks.plots import set_publication_style


def generate_ablation_plots(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    df_c: pd.DataFrame,
    df_d: pd.DataFrame,
    output_dir: Path,
):
    """Generate all required publication ablation plots."""
    set_publication_style()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ablation A: Quality vs Grover iterations
    fig, ax1 = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    ax1.plot(df_a["grover_iterations"], df_a["snr_improvement_db"], "o-", color="#1976d2", linewidth=2.5, label="SNR Improvement (dB)")
    ax1.plot(df_a["grover_iterations"], df_a["r_peak_f1"] * 10.0, "s-", color="#388e3c", linewidth=2.5, label="R-Peak F1 (x10)")
    ax1.set_xlabel("Grover Iterations (r)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Quality Metrics", fontsize=10)
    ax1.set_title("Ablation A: Signal Quality vs Grover Iterations", fontsize=11, fontweight="bold")
    ax1.set_xticks(df_a["grover_iterations"])
    ax1.legend(loc="lower left", frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_a_quality_vs_grover.png", dpi=300)
    plt.close(fig)

    # Ablation A: Depth vs Grover iterations
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    ax.plot(df_a["grover_iterations"], df_a["circuit_depth"], "^-", color="#d32f2f", linewidth=2.5, label="Logical Depth")
    ax.plot(df_a["grover_iterations"], df_a["cx_count"], "d-", color="#7b1fa2", linewidth=2.5, label="Transpiled CX Count")
    ax.set_xlabel("Grover Iterations (r)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Quantum Resource Count", fontsize=10)
    ax.set_title("Ablation A: Circuit Cost Scaling vs Grover Iterations", fontsize=11, fontweight="bold")
    ax.set_xticks(df_a["grover_iterations"])
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_a_depth_vs_grover.png", dpi=300)
    plt.close(fig)

    # Ablation B: Scaling vs M
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    ax.plot(df_b["segment_size"], df_b["transpiled_depth"], "o-", color="#1976d2", linewidth=2.5, label="Transpiled Depth")
    ax.plot(df_b["segment_size"], df_b["total_gate_count"], "s-", color="#e65100", linewidth=2.5, label="Total Gates")
    ax.set_xlabel("Segment Size (M)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Resource Count", fontsize=10)
    ax.set_title("Ablation B: Quantum Gate & Depth Scaling vs M", fontsize=11, fontweight="bold")
    ax.set_xscale("log", base=2)
    ax.set_xticks(df_b["segment_size"])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_b_scaling_vs_m.png", dpi=300)
    plt.close(fig)

    # Ablation B: Quality vs M
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    ax.plot(df_b["segment_size"], df_b["snr_improvement_db"], "o-", color="#2e7d32", linewidth=2.5, label="SNR Improvement (dB)")
    ax.plot(df_b["segment_size"], df_b["r_peak_f1"], "s-", color="#0288d1", linewidth=2.5, label="R-Peak F1")
    ax.set_xlabel("Segment Size (M)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Metric Value", fontsize=10)
    ax.set_title("Ablation B: Filter Performance vs Window Size M", fontsize=11, fontweight="bold")
    ax.set_xscale("log", base=2)
    ax.set_xticks(df_b["segment_size"])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_b_quality_vs_m.png", dpi=300)
    plt.close(fig)

    # Ablation C: Oracle Depth Comparison (O1 Diagonal vs O2 Range)
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    x_indices = np.arange(len(df_c))
    width = 0.35
    ax.bar(x_indices - width/2, df_c["o1_depth"], width, label="O1: Diagonal Reference", color="#42a5f5", alpha=0.85)
    ax.bar(x_indices + width/2, df_c["o2_depth"], width, label="O2: Range / Comparator", color="#ab47bc", alpha=0.85)
    ax.set_xlabel("Segment Size (M)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Oracle Circuit Depth", fontsize=10)
    ax.set_title("Ablation C: Oracle Implementation Circuit Depth", fontsize=11, fontweight="bold")
    ax.set_xticks(x_indices)
    ax.set_xticklabels([f"M={int(m)}" for m in df_c["segment_size"]])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_c_oracle_depth_comparison.png", dpi=300)
    plt.close(fig)

    # Ablation C: CX Count Comparison
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    ax.bar(x_indices - width/2, df_c["o1_cx"], width, label="O1: Diagonal Reference", color="#42a5f5", alpha=0.85)
    ax.bar(x_indices + width/2, df_c["o2_cx"], width, label="O2: Range / Comparator", color="#ab47bc", alpha=0.85)
    ax.set_xlabel("Segment Size (M)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Transpiled CX Gates", fontsize=10)
    ax.set_title("Ablation C: Oracle CX Gate Scaling Comparison", fontsize=11, fontweight="bold")
    ax.set_xticks(x_indices)
    ax.set_xticklabels([f"M={int(m)}" for m in df_c["segment_size"]])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_c_oracle_cx_comparison.png", dpi=300)
    plt.close(fig)

    # Ablation D: Quantum vs Classical Equivalent
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    methods = ["fft_adaptive_bandpass", "qft_grover_ecg_adaptive"]
    snr_vals = [df_d[df_d["method"] == m]["snr_improvement_db"].median() for m in methods]
    colors = ["#ffa726", "#ab47bc"]
    ax.bar(["Classical Adaptive FFT", "Quantum QFT + Grover"], snr_vals, color=colors, width=0.5, alpha=0.85)
    ax.set_ylabel("Median SNR Improvement (dB)", fontsize=10)
    ax.set_title("Ablation D: Classical vs Quantum Equivalent (Identical Rules)", fontsize=11, fontweight="bold")
    for idx, v in enumerate(snr_vals):
        ax.text(idx, v + 0.1, f"{v:.2f} dB", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "ablation_d_snr_comparison.png", dpi=300)
    plt.close(fig)
