"""Specialized publication plotting functions for Phase 8 validation grid tuning."""
from pathlib import Path
from typing import Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from qsp.benchmarks.plots import set_publication_style


def generate_validation_plots(
    df_grid: pd.DataFrame,
    df_raw: pd.DataFrame,
    df_resources: pd.DataFrame,
    output_dir: Path,
):
    """Generate all 10 required validation analysis figures."""
    set_publication_style()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Heatmap helper
    def plot_pivot_heatmap(metric_col: str, title: str, filename: str, cmap: str = "viridis", fmt: str = ".2f"):
        pivot_data = df_grid.pivot_table(
            index="segment_size",
            columns="grover_iterations",
            values=metric_col,
            aggfunc="median",
        )
        fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
        im = ax.imshow(pivot_data.values, cmap=cmap, aspect="auto")
        ax.set_xticks(range(len(pivot_data.columns)))
        ax.set_xticklabels([f"r={c}" for c in pivot_data.columns])
        ax.set_yticks(range(len(pivot_data.index)))
        ax.set_yticklabels([f"M={idx}" for idx in pivot_data.index])
        ax.set_xlabel("Grover Iterations (r)", fontsize=10, fontweight="bold")
        ax.set_ylabel("Segment Size (M)", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold", pad=12)

        cbar = fig.colorbar(im, ax=ax)
        cbar.ax.tick_params(labelsize=8)

        # Annotate cell values
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                val = pivot_data.values[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:{fmt}}", ha="center", va="center", color="white" if val < pivot_data.values.mean() else "black", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(output_dir / filename, dpi=300)
        plt.close(fig)

    # Heatmaps
    plot_pivot_heatmap("median_snr_improvement", "Validation SNR Improvement (dB)", "validation_snr_heatmap.png", cmap="magma")
    plot_pivot_heatmap("median_r_peak_f1", "Validation R-Peak Detection F1", "validation_f1_heatmap.png", cmap="viridis")
    plot_pivot_heatmap("median_prd", "Validation PRD (%)", "validation_prd_heatmap.png", cmap="Blues_r")
    plot_pivot_heatmap("median_rmse", "Validation RMSE", "validation_rmse_heatmap.png", cmap="Purples_r", fmt=".4f")

    # 5. SNR vs Grover iterations
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    for m_val in sorted(df_grid["segment_size"].unique()):
        sub = df_grid[df_grid["segment_size"] == m_val].groupby("grover_iterations")["median_snr_improvement"].median()
        ax.plot(sub.index, sub.values, marker="o", label=f"M={m_val}", linewidth=2)
    ax.set_xlabel("Grover Iterations (r)", fontsize=10)
    ax.set_ylabel("Median SNR Improvement (dB)", fontsize=10)
    ax.set_title("SNR Improvement vs Grover Iterations", fontsize=11, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "snr_vs_grover_iterations.png", dpi=300)
    plt.close(fig)

    # 6. F1 vs Grover iterations
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    for m_val in sorted(df_grid["segment_size"].unique()):
        sub = df_grid[df_grid["segment_size"] == m_val].groupby("grover_iterations")["median_r_peak_f1"].median()
        ax.plot(sub.index, sub.values, marker="s", label=f"M={m_val}", linewidth=2)
    ax.set_xlabel("Grover Iterations (r)", fontsize=10)
    ax.set_ylabel("Median R-Peak F1 Score", fontsize=10)
    ax.set_title("ECG Morphology (F1) vs Grover Iterations", fontsize=11, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "f1_vs_grover_iterations.png", dpi=300)
    plt.close(fig)

    # 7. Depth vs Grover iterations
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    for m_val in sorted(df_resources["segment_size"].unique()):
        sub = df_resources[df_resources["segment_size"] == m_val].groupby("grover_iterations")["circuit_depth"].mean()
        ax.plot(sub.index, sub.values, marker="^", label=f"M={m_val}", linewidth=2)
    ax.set_xlabel("Grover Iterations (r)", fontsize=10)
    ax.set_ylabel("Logical Circuit Depth", fontsize=10)
    ax.set_title("Quantum Circuit Depth vs Grover Iterations", fontsize=11, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "depth_vs_grover_iterations.png", dpi=300)
    plt.close(fig)

    # 8. CX count vs Grover iterations
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    for m_val in sorted(df_resources["segment_size"].unique()):
        sub = df_resources[df_resources["segment_size"] == m_val].groupby("grover_iterations")["cx_count"].mean()
        ax.plot(sub.index, sub.values, marker="D", label=f"M={m_val}", linewidth=2)
    ax.set_xlabel("Grover Iterations (r)", fontsize=10)
    ax.set_ylabel("Transpiled CX Gate Count", fontsize=10)
    ax.set_title("Transpiled CX Count vs Grover Iterations", fontsize=11, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_dir / "cx_vs_grover_iterations.png", dpi=300)
    plt.close(fig)

    # 9. SNR vs Segment size
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    sub = df_grid.groupby("segment_size")["median_snr_improvement"].median()
    ax.bar([str(m) for m in sub.index], sub.values, color="#1976d2", alpha=0.85, width=0.5)
    ax.set_xlabel("Segment Size (M)", fontsize=10)
    ax.set_ylabel("Median SNR Improvement (dB)", fontsize=10)
    ax.set_title("SNR Improvement vs Segment Size", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "snr_vs_segment_size.png", dpi=300)
    plt.close(fig)

    # 10. Depth vs Segment size
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    sub = df_resources.groupby("segment_size")["transpiled_depth"].mean()
    ax.plot([str(m) for m in sub.index], sub.values, marker="o", color="#d32f2f", linewidth=2.5)
    ax.set_xlabel("Segment Size (M)", fontsize=10)
    ax.set_ylabel("Transpiled Depth", fontsize=10)
    ax.set_title("Transpiled Circuit Depth vs Segment Size", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "depth_vs_segment_size.png", dpi=300)
    plt.close(fig)
