"""Publication-quality plotting functions for ECG benchmark results (Section 24 & 34)."""
from pathlib import Path
from typing import List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def set_publication_style():
    """Apply clean academic styling to Matplotlib figures."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8


def plot_metric_by_method(
    df: pd.DataFrame,
    metric_col: str,
    output_path: Path,
    title: str,
    ylabel: str,
):
    """Plot metric distribution grouped by denoising method."""
    set_publication_style()
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    methods = df["method"].unique()
    data_by_method = [df[df["method"] == m][metric_col].dropna().values for m in methods]

    bp = ax.boxplot(
        data_by_method,
        tick_labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black"},
    )

    colors = ["#90caf9", "#a5d6a7", "#ffe082", "#b39ddb", "#ef9a9a"]
    for patch, color in zip(bp["boxes"], colors * (len(methods) // len(colors) + 1)):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_circuit_scaling(
    segment_sizes: List[int],
    depths: List[int],
    gate_counts: List[int],
    output_dir: Path,
):
    """Plot circuit depth and gate count vs segment size (powers of 2)."""
    set_publication_style()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Depth vs segment size
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    ax.plot(segment_sizes, depths, "o-", color="#1976d2", linewidth=2, markersize=6)
    ax.set_xlabel("Segment Size (M)", fontsize=10)
    ax.set_ylabel("Transpiled Circuit Depth", fontsize=10)
    ax.set_title("Quantum Circuit Depth vs Segment Size", fontsize=11, fontweight="bold")
    ax.set_xscale("log", base=2)
    plt.tight_layout()
    plt.savefig(output_dir / "circuit_depth_vs_segment_size.png", dpi=300)
    plt.close(fig)

    # 2. Gate count vs segment size
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    ax.plot(segment_sizes, gate_counts, "s-", color="#388e3c", linewidth=2, markersize=6)
    ax.set_xlabel("Segment Size (M)", fontsize=10)
    ax.set_ylabel("Total Gate Count", fontsize=10)
    ax.set_title("Total Gate Count vs Segment Size", fontsize=11, fontweight="bold")
    ax.set_xscale("log", base=2)
    plt.tight_layout()
    plt.savefig(output_dir / "gate_count_vs_segment_size.png", dpi=300)
    plt.close(fig)
