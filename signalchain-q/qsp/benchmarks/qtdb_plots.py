"""Publication plotting functions for Phase 10 QTDB external morphology validation."""
from pathlib import Path
from typing import Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from qsp.benchmarks.plots import set_publication_style


def generate_qtdb_plots(
    df_raw: pd.DataFrame,
    output_dir: Path,
):
    """Generate the 4 required morphology preservation plots for QTDB."""
    set_publication_style()
    output_dir.mkdir(parents=True, exist_ok=True)

    method_palette = {
        "raw": "#9e9e9e",
        "butterworth_bandpass": "#42a5f5",
        "wavelet_db6": "#66bb6a",
        "fft_adaptive_bandpass": "#ffa726",
        "qft_grover_ecg_adaptive": "#ab47bc",
    }

    methods = [m for m in ["raw", "butterworth_bandpass", "wavelet_db6", "fft_adaptive_bandpass", "qft_grover_ecg_adaptive"] if m in df_raw["method"].unique()]

    # 1. R-peak F1 by method
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    data_f1 = [df_raw[df_raw["method"] == m]["r_peak_f1"].dropna().values for m in methods]
    bp1 = ax.boxplot(
        data_f1,
        tick_labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 5},
    )
    for patch, m in zip(bp1["boxes"], methods):
        patch.set_facecolor(method_palette.get(m, "#90caf9"))
        patch.set_alpha(0.85)
    ax.set_title("QTDB External Validation: R-Peak Morphology F1 Score", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("F1 Score", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "qtdb_rpeak_f1_by_method.png", dpi=300)
    plt.close(fig)

    # 2. R-peak Timing Error (ms)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    col_timing = "median_absolute_r_peak_timing_error_ms" if "median_absolute_r_peak_timing_error_ms" in df_raw.columns else "r_peak_timing_error_ms"
    data_time = [df_raw[df_raw["method"] == m][col_timing].dropna().values for m in methods]
    bp2 = ax.boxplot(
        data_time,
        tick_labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 5},
    )
    for patch, m in zip(bp2["boxes"], methods):
        patch.set_facecolor(method_palette.get(m, "#90caf9"))
        patch.set_alpha(0.85)
    ax.set_title("QTDB External Validation: R-Peak Temporal Timing Error", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Absolute Timing Error (ms)", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "qtdb_rpeak_timing_error.png", dpi=300)
    plt.close(fig)

    # 3. QRS Error
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    qrs_col = "qrs_duration_error_ms" if "qrs_duration_error_ms" in df_raw.columns else col_timing
    data_qrs = [df_raw[df_raw["method"] == m][qrs_col].dropna().values for m in methods]
    bp3 = ax.boxplot(
        data_qrs,
        tick_labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 5},
    )
    for patch, m in zip(bp3["boxes"], methods):
        patch.set_facecolor(method_palette.get(m, "#90caf9"))
        patch.set_alpha(0.85)
    ax.set_title("QTDB External Validation: QRS Duration Timing Error", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("QRS Error (ms)", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "qtdb_qrs_error.png", dpi=300)
    plt.close(fig)

    # 4. QT Error
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    qt_col = "qt_interval_error_ms" if "qt_interval_error_ms" in df_raw.columns else col_timing
    data_qt = [df_raw[df_raw["method"] == m][qt_col].dropna().values for m in methods]
    bp4 = ax.boxplot(
        data_qt,
        tick_labels=methods,
        patch_artist=True,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": 5},
    )
    for patch, m in zip(bp4["boxes"], methods):
        patch.set_facecolor(method_palette.get(m, "#90caf9"))
        patch.set_alpha(0.85)
    ax.set_title("QTDB External Validation: QT Interval Timing Error", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("QT Interval Error (ms)", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "qtdb_qt_error.png", dpi=300)
    plt.close(fig)
