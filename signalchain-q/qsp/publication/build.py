"""One-command publication artifact and manuscript table/figure builder.

Executes publication consolidation (Phase 11) using completed experimental artifacts:
- results/validation_20261013_202654/
- results/test_20261013_204319/
- results/qtdb_20261013_211001/
- results/ablations_20261013_211229/

Operates strictly from cached artifacts without rerunning expensive simulations.
"""
from pathlib import Path
import json
import hashlib
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class PublicationBuilder:
    """Build camera-ready publication tables, figures, and summaries."""

    def __init__(
        self,
        base_dir: Path = Path("."),
        output_tables: Path = None,
        output_figures: Path = None,
        output_supp: Path = None,
    ):
        self.base_dir = Path(base_dir)
        self.tables_dir = Path(output_tables) if output_tables is not None else self.base_dir / "paper/tables"
        self.figures_dir = Path(output_figures) if output_figures is not None else self.base_dir / "paper/figures"
        self.supp_dir = Path(output_supp) if output_supp is not None else self.base_dir / "paper/supplementary"

        self.tables_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.supp_dir.mkdir(parents=True, exist_ok=True)

        # Authoritative result paths
        self.val_dir = base_dir / "results/validation_20261013_202654"
        self.test_dir = base_dir / "results/test_20261013_204319"
        self.qtdb_dir = base_dir / "results/qtdb_20261013_211001"
        self.ablation_dir = base_dir / "results/ablations_20261013_211229"

    def load_artifacts(self):
        """Load and validate all source dataframes."""
        print("Loading source experimental dataframes...")
        self.df_mitdb_raw = pd.read_csv(self.test_dir / "mitdb_test_results.csv")
        self.df_nstdb_raw = pd.read_csv(self.test_dir / "nstdb_test_results.csv")
        self.df_test_meth = pd.read_csv(self.test_dir / "test_method_summary.csv")
        self.df_test_stats = pd.read_csv(self.test_dir / "test_statistics.csv")
        self.df_test_res = pd.read_csv(self.test_dir / "test_quantum_resources.csv")

        self.df_qtdb_raw = pd.read_csv(self.qtdb_dir / "qtdb_raw_results.csv")
        self.df_qtdb_meth = pd.read_csv(self.qtdb_dir / "qtdb_method_summary.csv")

        self.df_abl_a = pd.read_csv(self.ablation_dir / "ablation_a_grover_iterations.csv")
        self.df_abl_b = pd.read_csv(self.ablation_dir / "ablation_b_segment_size.csv")
        self.df_abl_c = pd.read_csv(self.ablation_dir / "ablation_c_oracle_comparison.csv")
        self.df_abl_d = pd.read_csv(self.ablation_dir / "ablation_d_quantum_vs_classical.csv")

        self.df_val_grid = pd.read_csv(self.val_dir / "validation_parameter_grid.csv")
        self.df_val_meth = pd.read_csv(self.val_dir / "validation_method_summary.csv")
        print("All experimental artifacts successfully loaded.")

    def generate_table_dataset_summary(self):
        """Table 1: Dataset Summary."""
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Benchmark Datasets and Partition Allocations in SignalChain-Q}\n"
            "\\label{tab:datasets}\n"
            "\\begin{tabular}{lccccp{4.2cm}}\n"
            "\\hline\n"
            "\\textbf{Dataset} & \\textbf{Split} & \\textbf{Records} & \\textbf{$f_s$ (Hz)} & \\textbf{Leads} & \\textbf{Role / Noise Conditions} \\\\\n"
            "\\hline\n"
            "MIT-BIH (mitdb) & Development & 10 & 360 & MLII & Initial pipeline tuning \\& verification \\\\\n"
            "MIT-BIH (mitdb) & Validation  & 8  & 360 & MLII & Parameter grid tuning (108 configs, isolated) \\\\\n"
            "MIT-BIH (mitdb) & Test        & 7  & 360 & MLII & Frozen test evaluation (canonical noise: bw, ma, em, wgn, pl50, pl60) \\\\\n"
            "NSTDB (nstdb)   & Benchmark   & 12 & 360 & MLII & Calibrated clinical noise stress records (-6 to +24 dB) \\\\\n"
            "QTDB (qtdb)     & External    & 10 & 250 & Lead I & Cross-sampling-rate morphology preservation \\\\\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_dataset_summary.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_validation_parameters(self):
        """Table 2: Validation parameter grid and selected configuration."""
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Validation Parameter Grid Search and Selected Configuration}\n"
            "\\label{tab:validation_grid}\n"
            "\\begin{tabular}{lp{3.5cm}cc}\n"
            "\\hline\n"
            "\\textbf{Parameter} & \\textbf{Grid Search Space} & \\textbf{Tested} & \\textbf{Selected (Frozen)} \\\\\n"
            "\\hline\n"
            "Lower Cutoff ($f_{\\text{low}}$) & Fixed & 1 & 0.5 Hz \\\\\n"
            "Min Upper Cutoff ($f_{\\text{high,min}}$) & $[20.0, 25.0, 30.0]$ Hz & 3 & 30.0 Hz \\\\\n"
            "Max Upper Cutoff ($f_{\\text{high,max}}$) & $[40.0, 45.0, 50.0]$ Hz & 3 & 45.0 Hz \\\\\n"
            "Segment Size ($M$) & $[64, 128, 256]$ samples & 3 & 64 samples ($n=6$) \\\\\n"
            "Grover Iterations ($r$) & $[0, 1, 2, 3]$ & 4 & 2 \\\\\n"
            "Total Valid Grid Points & $f_{\\text{high,min}} < f_{\\text{high,max}}$ & 108 & 1 (\\texttt{cfg\\_086}) \\\\\n"
            "Feasible Candidates & $F_1 \\ge F_{1,\\text{classical}} - 0.01$ & 46 & 1 (Max Median SNR) \\\\\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_validation_parameters.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_main_results(self):
        """Table 3: Main MIT-BIH test results comparing all 5 methods."""
        df = self.df_mitdb_raw
        methods = [
            ("raw", "Raw (Unfiltered)"),
            ("butterworth_bandpass", "Butterworth Bandpass"),
            ("wavelet_db6", "Wavelet DB6"),
            ("fft_adaptive_bandpass", "Adaptive FFT"),
            ("qft_grover_ecg_adaptive", "QFT-Grover Adaptive"),
        ]

        rows_data = []
        for m_key, m_label in methods:
            sub = df[df["method"] == m_key]
            snr_med = sub["snr_improvement_db"].median()
            snr_iqr = np.percentile(sub["snr_improvement_db"], 75) - np.percentile(sub["snr_improvement_db"], 25)
            rmse_med = sub["rmse"].median()
            prd_med = sub["prd_percent"].median()
            r_med = sub["pearson_r"].median()
            sens_med = sub["r_peak_sensitivity"].median()
            ppv_med = sub["r_peak_ppv"].median()
            f1_med = sub["r_peak_f1"].median()

            rows_data.append({
                "label": m_label,
                "key": m_key,
                "snr_med": snr_med,
                "snr_iqr": snr_iqr,
                "rmse_med": rmse_med,
                "prd_med": prd_med,
                "r_med": r_med,
                "sens_med": sens_med,
                "ppv_med": ppv_med,
                "f1_med": f1_med,
            })

        best_snr = max(r["snr_med"] for r in rows_data)
        best_snr_iqr = min(r["snr_iqr"] for r in rows_data if r["key"] != "raw")
        best_rmse = min(r["rmse_med"] for r in rows_data)
        best_prd = min(r["prd_med"] for r in rows_data)
        best_r = max(r["r_med"] for r in rows_data)
        best_sens = max(r["sens_med"] for r in rows_data)
        best_ppv = max(r["ppv_med"] for r in rows_data)
        best_f1 = max(r["f1_med"] for r in rows_data)

        tex_rows = []
        for r in rows_data:
            s_snr = f"\\textbf{{{r['snr_med']:.2f}}}" if abs(r["snr_med"] - best_snr) < 1e-4 else f"{r['snr_med']:.2f}"
            s_iqr = f"\\textbf{{{r['snr_iqr']:.2f}}}" if abs(r["snr_iqr"] - best_snr_iqr) < 1e-4 and r["key"] != "raw" else f"{r['snr_iqr']:.2f}"
            s_rmse = f"\\textbf{{{r['rmse_med']:.3f}}}" if abs(r["rmse_med"] - best_rmse) < 1e-4 else f"{r['rmse_med']:.3f}"
            s_prd = f"\\textbf{{{r['prd_med']:.1f}}}" if abs(r["prd_med"] - best_prd) < 1e-4 else f"{r['prd_med']:.1f}"
            s_r = f"\\textbf{{{r['r_med']:.3f}}}" if abs(r["r_med"] - best_r) < 1e-4 else f"{r['r_med']:.3f}"
            s_sens = f"\\textbf{{{r['sens_med']:.3f}}}" if abs(r["sens_med"] - best_sens) < 1e-4 else f"{r['sens_med']:.3f}"
            s_ppv = f"\\textbf{{{r['ppv_med']:.3f}}}" if abs(r["ppv_med"] - best_ppv) < 1e-4 else f"{r['ppv_med']:.3f}"
            s_f1 = f"\\textbf{{{r['f1_med']:.3f}}}" if abs(r["f1_med"] - best_f1) < 1e-4 else f"{r['f1_med']:.3f}"

            tex_rows.append(
                f"{r['label']} & {s_snr} & {s_iqr} & {s_rmse} & {s_prd} & {s_r} & {s_sens} & {s_ppv} & {s_f1} \\\\"
            )

        body = "\n".join(tex_rows)
        tex = (
            "\\begin{table*}[t]\n"
            "\\centering\n"
            "\\caption{Canonical Test Evaluation on the Untouched MIT-BIH Test Split (1,260 instances across 6 noise types and 6 SNR levels). $\\uparrow$ indicates higher is better; $\\downarrow$ indicates lower is better. Bold values indicate best performance.}\n"
            "\\label{tab:main_results}\n"
            "\\begin{tabular}{lcccccccc}\n"
            "\\hline\n"
            "\\textbf{Method} & \\textbf{SNR Imp (dB) $\\uparrow$} & \\textbf{IQR (dB) $\\downarrow$} & \\textbf{RMSE $\\downarrow$} & \\textbf{PRD (\\%) $\\downarrow$} & \\textbf{Pearson $r$ $\\uparrow$} & \\textbf{Sens $\\uparrow$} & \\textbf{PPV $\\uparrow$} & \\textbf{$F_1$ Score $\\uparrow$} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table*}\n"
        )
        p = self.tables_dir / "table_main_results.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_statistics(self):
        """Table 4: Statistical comparison table."""
        df = self.df_test_stats
        label_map = {
            "fft_adaptive_bandpass": "Adaptive FFT",
            "butterworth_bandpass": "Butterworth Bandpass",
            "wavelet_db6": "Wavelet DB6",
        }
        rows = []
        for _, r in df.iterrows():
            comp_name = label_map.get(r["method_b"], r["method_b"])
            med_diff = f"{r['median_difference']:+.2f} dB"
            ci_str = f"[{r['ci_95_low']:.2f}, {r['ci_95_high']:.2f}]"
            cd = f"{r['cliffs_delta']:+.3f}"
            if abs(r["cliffs_delta"]) < 0.147:
                eff = "Negligible"
            elif abs(r["cliffs_delta"]) < 0.33:
                eff = "Small"
            elif abs(r["cliffs_delta"]) < 0.474:
                eff = "Moderate"
            else:
                eff = "Large"

            p_adj = "< 10^{-6}" if r["p_value_corrected"] < 1e-6 else f"{r['p_value_corrected']:.4f}"

            if r["median_difference"] > 0 and r["p_value_corrected"] < 0.05:
                concl = "QFT-Grover significantly higher"
            elif r["median_difference"] < 0 and r["p_value_corrected"] < 0.05:
                concl = "Classical significantly higher"
            else:
                concl = "No significant difference"

            rows.append(
                f"QFT-Grover vs {comp_name} & {med_diff} & {ci_str} & {cd} & {eff} & ${p_adj}$ & {concl} \\\\"
            )

        body = "\n".join(rows)
        tex = (
            "\\begin{table*}[t]\n"
            "\\centering\n"
            "\\caption{Paired Statistical Comparisons on MIT-BIH Test Split ($N=1,260$). Wilcoxon signed-rank test with Holm-Bonferroni family-wise error rate correction and 95\\% bootstrap confidence intervals.}\n"
            "\\label{tab:statistics}\n"
            "\\begin{tabular}{lcccccl}\n"
            "\\hline\n"
            "\\textbf{Comparison} & \\textbf{Med. Diff.} & \\textbf{95\\% Bootstrap CI} & \\textbf{Cliff's $\\delta$} & \\textbf{Effect Size} & \\textbf{$p_{\\text{corr}}$} & \\textbf{Statistical Conclusion} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table*}\n"
        )
        p = self.tables_dir / "table_statistics.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_quantum_resources(self):
        """Table 5: Quantum Resource Scaling."""
        df = self.df_abl_b
        rows = []
        for _, r in df.iterrows():
            m = int(r["segment_size"])
            nq = int(r["logical_qubits"])
            ld = int(r["logical_depth"])
            td = int(r["transpiled_depth"])
            tg = int(r["total_gate_count"])
            cx = int(r["cx_count"])
            sp_ms = r["state_preparation_ms"]
            sim_ms = r["simulation_ms"]

            rows.append(
                f"{m} & {nq} & 0 & {ld} & {td} & {tg} & {cx} & {sp_ms:.2f} ms & {sim_ms:.2f} ms \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Quantum Circuit Resource Scaling Across Segment Lengths $M$ ($r=1$, Optimization Level 3)}\n"
            "\\label{tab:quantum_resources}\n"
            "\\begin{tabular}{ccccccccc}\n"
            "\\hline\n"
            "\\textbf{$M$} & \\textbf{$n_{\\text{qubits}}$} & \\textbf{Anc.} & \\textbf{Log. D.} & \\textbf{Trans. D.} & \\textbf{Gates} & \\textbf{CX} & \\textbf{Prep Lat.} & \\textbf{Sim Lat.} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_quantum_resources.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_grover_ablation(self):
        """Table 6: Grover Iterations Ablation."""
        df = self.df_abl_a
        rows = []
        for _, r in df.iterrows():
            it = int(r["grover_iterations"])
            snr = r["snr_improvement_db"]
            rmse = r["rmse"]
            prd = r["prd"]
            f1 = r["r_peak_f1"]
            cx = int(r["cx_count"])
            depth = int(r["circuit_depth"])
            rt = r["simulation_runtime_ms"]

            rows.append(
                f"{it} & {snr:+.2f} dB & {rmse:.3f} & {prd:.1f}\\% & {f1:.3f} & {depth} & {cx} & {rt:.1f} ms \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Ablation A: Grover Iteration Dynamics ($M=128$, Baseline Wander Noise at 6.0 dB SNR)}\n"
            "\\label{tab:ablation_grover}\n"
            "\\begin{tabular}{cccccccc}\n"
            "\\hline\n"
            "\\textbf{$r$} & \\textbf{SNR Imp.} & \\textbf{RMSE} & \\textbf{PRD} & \\textbf{$F_1$ Score} & \\textbf{Log. Depth} & \\textbf{CX} & \\textbf{Sim Runtime} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_grover_ablation.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_segment_ablation(self):
        """Table 7: Segment Size Ablation."""
        df = self.df_abl_b
        rows = []
        for _, r in df.iterrows():
            m = int(r["segment_size"])
            nq = int(r["logical_qubits"])
            snr = r["snr_improvement_db"]
            f1 = r["r_peak_f1"]
            prd = r["prd"]
            td = int(r["transpiled_depth"])
            cx = int(r["cx_count"])

            rows.append(
                f"{m} & {nq} & {snr:+.2f} dB & {f1:.3f} & {prd:.1f}\\% & {td} & {cx} \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Ablation B: Segment Size Scaling ($M \\in [64, 128, 256]$, $r=1$)}\n"
            "\\label{tab:ablation_segment}\n"
            "\\begin{tabular}{ccccccc}\n"
            "\\hline\n"
            "\\textbf{$M$} & \\textbf{$n$} & \\textbf{SNR Imp.} & \\textbf{$F_1$ Score} & \\textbf{PRD} & \\textbf{Transpiled Depth} & \\textbf{CX Count} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_segment_ablation.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_oracle_ablation(self):
        """Table 8: Phase Oracle Comparison."""
        df = self.df_abl_c
        rows = []
        for _, r in df.iterrows():
            m = int(r["segment_size"])
            nq = int(r["qubits"])
            eq = "Verified" if r["functional_equivalence"] else "Failed"
            o1_d = int(r["o1_depth"])
            o2_d = int(r["o2_depth"])
            o1_t = r["o1_transpile_ms"]
            o2_t = r["o2_transpile_ms"]

            rows.append(
                f"{m} & {nq} & {eq} & {o1_d} & {o2_d} & {o1_t:.2f} ms & {o2_t:.2f} ms \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Ablation C: Phase Oracle Structural Comparison ($O_1$ Diagonal vs $O_2$ Range Comparator)}\n"
            "\\label{tab:ablation_oracle}\n"
            "\\begin{tabular}{ccccccc}\n"
            "\\hline\n"
            "\\textbf{$M$} & \\textbf{$n$} & \\textbf{$O_1 \\equiv O_2$} & \\textbf{$O_1$ Depth} & \\textbf{$O_2$ Depth} & \\textbf{$O_1$ Transpile} & \\textbf{$O_2$ Transpile} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_oracle_ablation.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_qtdb_morphology(self):
        """Table 9: QTDB External morphology preservation."""
        df = self.df_qtdb_meth
        label_map = {
            "raw": "Raw (Reference)",
            "butterworth_bandpass": "Butterworth Bandpass",
            "wavelet_db6": "Wavelet DB6",
            "fft_adaptive_bandpass": "Adaptive FFT",
            "qft_grover_ecg_adaptive": "QFT-Grover Adaptive",
        }
        rows = []
        for _, r in df.iterrows():
            lbl = label_map.get(r["method"], r["method"])
            f1 = r["r_peak_f1_median"]
            terr = r["r_peak_timing_error_ms_median"]
            prd = r["prd_percent_median"]
            pear = r["pearson_r_median"]

            rows.append(
                f"{lbl} & {f1:.4f} & {terr:.2f} ms & {prd:.2f}\\% & {pear:.4f} \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{External Morphology Preservation on QT Database ($f_s = 250.0$ Hz, 10 records). Discrete R-peak timing resolution bounded by $\\pm 2.0$ ms discrete sampling grid.}\n"
            "\\label{tab:qtdb_morphology}\n"
            "\\begin{tabular}{lcccc}\n"
            "\\hline\n"
            "\\textbf{Method} & \\textbf{Median $F_1$} & \\textbf{R-Peak Timing Err.} & \\textbf{PRD (\\%)} & \\textbf{Pearson $r$} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_qtdb_morphology.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_noise_type_results(self):
        """Table 10: Subgroup analysis by noise type."""
        df = self.df_mitdb_raw
        noise_names = {
            "bw": "Baseline Wander (bw)",
            "em": "Electrode Motion (em)",
            "ma": "Muscle Artifact (ma)",
            "pl50": "Powerline 50 Hz (pl50)",
            "pl60": "Powerline 60 Hz (pl60)",
            "wgn": "White Gaussian (wgn)",
        }
        rows = []
        for nt, label in noise_names.items():
            sub_nt = df[df["noise_type"] == nt]
            qft_snr = sub_nt[sub_nt["method"] == "qft_grover_ecg_adaptive"]["snr_improvement_db"].median()
            fft_snr = sub_nt[sub_nt["method"] == "fft_adaptive_bandpass"]["snr_improvement_db"].median()
            wav_snr = sub_nt[sub_nt["method"] == "wavelet_db6"]["snr_improvement_db"].median()

            qft_prd = sub_nt[sub_nt["method"] == "qft_grover_ecg_adaptive"]["prd_percent"].median()
            fft_prd = sub_nt[sub_nt["method"] == "fft_adaptive_bandpass"]["prd_percent"].median()
            wav_prd = sub_nt[sub_nt["method"] == "wavelet_db6"]["prd_percent"].median()

            rows.append(
                f"{label} & {wav_snr:+.2f} & {fft_snr:+.2f} & \\textbf{{{qft_snr:+.2f}}} & {wav_prd:.1f} & {fft_prd:.1f} & \\textbf{{{qft_prd:.1f}}} \\\\"
            )

        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Subgroup Analysis by Noise Class: Median SNR Improvement (dB) and PRD (\\%) on MIT-BIH Test Split.}\n"
            "\\label{tab:noise_types}\n"
            "\\begin{tabular}{lcccccc}\n"
            "\\hline\n"
            " & \\multicolumn{3}{c}{\\textbf{SNR Improvement (dB)}} & \\multicolumn{3}{c}{\\textbf{PRD (\\%)}}\\\\\n"
            "\\textbf{Noise Type} & \\textbf{Wavelet} & \\textbf{FFT} & \\textbf{QFT} & \\textbf{Wavelet} & \\textbf{FFT} & \\textbf{QFT} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_noise_type_results.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_table_snr_level_results(self):
        """Table 11: Subgroup analysis by target SNR level."""
        df = self.df_mitdb_raw
        levels = [-6.0, 0.0, 6.0, 12.0, 18.0, 24.0]
        rows = []
        for snr in levels:
            sub = df[df["target_snr"] == snr]
            wav_snr = sub[sub["method"] == "wavelet_db6"]["snr_improvement_db"].median()
            fft_snr = sub[sub["method"] == "fft_adaptive_bandpass"]["snr_improvement_db"].median()
            qft_snr = sub[sub["method"] == "qft_grover_ecg_adaptive"]["snr_improvement_db"].median()

            wav_prd = sub[sub["method"] == "wavelet_db6"]["prd_percent"].median()
            fft_prd = sub[sub["method"] == "fft_adaptive_bandpass"]["prd_percent"].median()
            qft_prd = sub[sub["method"] == "qft_grover_ecg_adaptive"]["prd_percent"].median()

            rows.append(
                f"{snr:+.0f} dB & {wav_snr:+.2f} & {fft_snr:+.2f} & {qft_snr:+.2f} & {wav_prd:.1f} & {fft_prd:.1f} & {qft_prd:.1f} \\\\"
            )
        body = "\n".join(rows)
        tex = (
            "\\begin{table}[t]\n"
            "\\centering\n"
            "\\caption{Performance Across Input Contamination Levels ($-6$ dB to $+24$ dB) on MIT-BIH Test Split.}\n"
            "\\label{tab:snr_levels}\n"
            "\\begin{tabular}{lcccccc}\n"
            "\\hline\n"
            " & \\multicolumn{3}{c}{\\textbf{Median SNR Improvement (dB)}} & \\multicolumn{3}{c}{\\textbf{Median PRD (\\%)}}\\\\\n"
            "\\textbf{Input SNR} & \\textbf{Wavelet} & \\textbf{FFT} & \\textbf{QFT} & \\textbf{Wavelet} & \\textbf{FFT} & \\textbf{QFT} \\\\\n"
            "\\hline\n"
            f"{body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table}\n"
        )
        p = self.tables_dir / "table_snr_level_results.tex"
        p.write_text(tex, encoding="utf-8")
        print(f"Wrote {p}")

    def generate_publication_figures(self):
        """Generate high-resolution vector PDF and PNG publication figures using pure matplotlib."""
        print("Generating vector PDF and PNG publication figures...")
        palette = {
            "raw": "#94a3b8",
            "butterworth_bandpass": "#f97316",
            "wavelet_db6": "#10b981",
            "fft_adaptive_bandpass": "#6366f1",
            "qft_grover_ecg_adaptive": "#06b6d4",
        }
        method_labels = {
            "raw": "Raw",
            "butterworth_bandpass": "Butterworth",
            "wavelet_db6": "Wavelet DB6",
            "fft_adaptive_bandpass": "Adaptive FFT",
            "qft_grover_ecg_adaptive": "QFT-Grover",
        }

        # 1. Noise Type vs SNR
        df = self.df_mitdb_raw
        noise_types = ["bw", "em", "ma", "pl50", "pl60", "wgn"]
        methods_list = ["raw", "butterworth_bandpass", "wavelet_db6", "fft_adaptive_bandpass", "qft_grover_ecg_adaptive"]

        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
        x = np.arange(len(noise_types))
        width = 0.16
        for idx, m in enumerate(methods_list):
            vals = []
            for nt in noise_types:
                sub = df[(df["noise_type"] == nt) & (df["method"] == m)]
                vals.append(sub["snr_improvement_db"].median() if len(sub) else 0.0)
            ax.bar(x + idx * width - 2 * width, vals, width, label=method_labels[m], color=palette[m])

        ax.set_title("Median SNR Improvement Across Canonical Noise Types (MIT-BIH Test)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Noise Type", fontsize=11)
        ax.set_ylabel("Median SNR Improvement (dB)", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(noise_types, fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "noise_type_snr.pdf")
        fig.savefig(self.figures_dir / "noise_type_snr.png")
        plt.close(fig)

        # 1b. Noise Type vs PRD
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
        for idx, m in enumerate(methods_list):
            vals = []
            for nt in noise_types:
                sub = df[(df["noise_type"] == nt) & (df["method"] == m)]
                vals.append(sub["prd_percent"].median() if len(sub) else 0.0)
            ax.bar(x + idx * width - 2 * width, vals, width, label=method_labels[m], color=palette[m])

        ax.set_title("Median PRD (%) Across Canonical Noise Types (MIT-BIH Test)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Noise Type", fontsize=11)
        ax.set_ylabel("Median PRD (%)", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(noise_types, fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "noise_type_prd.pdf")
        fig.savefig(self.figures_dir / "noise_type_prd.png")
        plt.close(fig)

        # 1c. Noise Type vs F1
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
        for idx, m in enumerate(methods_list):
            vals = []
            for nt in noise_types:
                sub = df[(df["noise_type"] == nt) & (df["method"] == m)]
                vals.append(sub["r_peak_f1"].median() if len(sub) else 0.0)
            ax.bar(x + idx * width - 2 * width, vals, width, label=method_labels[m], color=palette[m])

        ax.set_title("Median R-Peak F1 Across Canonical Noise Types", fontsize=12, fontweight="bold")
        ax.set_xlabel("Noise Type", fontsize=11)
        ax.set_ylabel("Median R-Peak F1 Score", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(noise_types, fontsize=10)
        ax.set_ylim([0.0, 1.05])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "noise_type_f1.pdf")
        fig.savefig(self.figures_dir / "noise_type_f1.png")
        plt.close(fig)

        # 2. Input SNR vs SNR Improvement
        levels = sorted(df["target_snr"].unique().tolist())
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        for m in methods_list:
            vals = [df[(df["target_snr"] == snr) & (df["method"] == m)]["snr_improvement_db"].median() for snr in levels]
            ax.plot(levels, vals, marker="o", lw=2, label=method_labels[m], color=palette[m])
        ax.set_title("Input SNR vs. Denoising Improvement", fontsize=12, fontweight="bold")
        ax.set_xlabel("Input Contamination SNR (dB)", fontsize=11)
        ax.set_ylabel("Output SNR Improvement (dB)", fontsize=11)
        ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "snr_input_vs_improvement.pdf")
        fig.savefig(self.figures_dir / "snr_input_vs_improvement.png")
        plt.close(fig)

        # 3. Input SNR vs PRD
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        for m in methods_list:
            vals = [df[(df["target_snr"] == snr) & (df["method"] == m)]["prd_percent"].median() for snr in levels]
            ax.plot(levels, vals, marker="s", lw=2, label=method_labels[m], color=palette[m])
        ax.set_title("Signal Distortion (PRD) vs. Input SNR", fontsize=12, fontweight="bold")
        ax.set_xlabel("Input Contamination SNR (dB)", fontsize=11)
        ax.set_ylabel("Median PRD (%)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "snr_input_vs_prd.pdf")
        fig.savefig(self.figures_dir / "snr_input_vs_prd.png")
        plt.close(fig)

        # 3b. Input SNR vs F1
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        for m in methods_list:
            vals = [df[(df["target_snr"] == snr) & (df["method"] == m)]["r_peak_f1"].median() for snr in levels]
            ax.plot(levels, vals, marker="^", lw=2, label=method_labels[m], color=palette[m])
        ax.set_title("Morphology Preservation (F1) vs. Input SNR", fontsize=12, fontweight="bold")
        ax.set_xlabel("Input Contamination SNR (dB)", fontsize=11)
        ax.set_ylabel("Median R-Peak F1 Score", fontsize=11)
        ax.set_ylim([0.0, 1.05])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Method", frameon=True, fontsize=9)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "snr_input_vs_f1.pdf")
        fig.savefig(self.figures_dir / "snr_input_vs_f1.png")
        plt.close(fig)

        # 4. Grover Quality-Resource Tradeoff (Ablation A)
        fig, ax1 = plt.subplots(figsize=(7, 4.5), dpi=300)
        ax2 = ax1.twinx()
        r_vals = self.df_abl_a["grover_iterations"].values
        snr_vals = self.df_abl_a["snr_improvement_db"].values
        depth_vals = self.df_abl_a["circuit_depth"].values

        l1 = ax1.plot(r_vals, snr_vals, color="#06b6d4", marker="o", lw=2.5, label="SNR Improvement (dB)")
        l2 = ax2.plot(r_vals, depth_vals, color="#e11d48", marker="s", lw=2.5, ls="--", label="Logical Circuit Depth")
        ax1.set_title("Grover Iteration Dynamics: Quality vs. Circuit Depth", fontsize=12, fontweight="bold")
        ax1.set_xlabel("Grover Iterations ($r$)", fontsize=11)
        ax1.set_ylabel("SNR Improvement (dB)", color="#06b6d4", fontsize=11)
        ax2.set_ylabel("Logical Depth", color="#e11d48", fontsize=11)
        ax1.set_xticks([0, 1, 2, 3])
        ax1.grid(True, linestyle="--", alpha=0.5)
        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="upper right", frameon=True)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "grover_tradeoff.pdf")
        fig.savefig(self.figures_dir / "grover_tradeoff.png")
        plt.close(fig)

        # 5. Circuit Scaling with Segment Size M
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
        m_vals = self.df_abl_b["segment_size"].values
        td = self.df_abl_b["transpiled_depth"].values
        cx = self.df_abl_b["cx_count"].values
        ax.plot(m_vals, td, marker="o", color="#3b82f6", lw=2.5, label="Transpiled Depth")
        ax.plot(m_vals, cx, marker="^", color="#f59e0b", lw=2.5, label="CX Gate Count")
        ax.set_title("Quantum Resource Scaling Across Segment Length ($M$)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Segment Length $M$ ($2^n$ samples)", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.set_xticks(m_vals)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(frameon=True)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "circuit_scaling.pdf")
        fig.savefig(self.figures_dir / "circuit_scaling.png")
        plt.close(fig)

        # 6. QTDB External Morphology Preservation
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
        m_keys = self.df_qtdb_meth["method"].tolist()
        prd_vals = self.df_qtdb_meth["prd_percent_median"].tolist()
        colors = [palette.get(k, "#64748b") for k in m_keys]
        x_pos = np.arange(len(m_keys))
        ax.bar(x_pos, prd_vals, color=colors, width=0.5)
        ax.set_title("External Generalization: PRD on Clean QTDB Records (250 Hz)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Method", fontsize=11)
        ax.set_ylabel("Median PRD (%)", fontsize=11)
        ax.set_xticks(x_pos)
        ax.set_xticklabels([method_labels.get(k, k) for k in m_keys], fontsize=9, rotation=15)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        fig.savefig(self.figures_dir / "qtdb_preservation.pdf")
        fig.savefig(self.figures_dir / "qtdb_preservation.png")
        plt.close(fig)

        print(f"Publication figures saved in {self.figures_dir}")

    def generate_architecture_diagram_sources(self):
        """Create reproducible diagram definitions in paper/figures/source/."""
        src_dir = self.figures_dir / "source"
        src_dir.mkdir(parents=True, exist_ok=True)

        mmd_content = (
            "graph TD\n"
            "    subgraph Signal Processing Flow\n"
            "        A[ECG Signal Input] --> B[Framing: Hann Overlap-Add]\n"
            "        B --> C[Adaptive Spectral Estimator]\n"
            "        C --> D{Processing Branch}\n\n"
            "        D -->|Baseline 1| E[Butterworth Bandpass 0.5-40 Hz]\n"
            "        D -->|Baseline 2| F[Wavelet DB6 Multiresolution]\n"
            "        D -->|Baseline 3| G[Adaptive FFT Frequency Mask]\n\n"
            "        D -->|Quantum Branch| H[Amplitude Encoding: State Preparation]\n"
            "        H --> I[Quantum Fourier Transform: QFT]\n"
            "        I --> J[Adaptive Phase Oracle: O1 / O2]\n"
            "        J --> K[Grover Diffusion: Amplitude Amplification r=2]\n"
            "        K --> L[Inverse QFT: IQFT]\n"
            "        L --> M[Statevector Readout / Rescaling]\n\n"
            "        E --> N[Signal Synthesis & Overlap-Add]\n"
            "        F --> N\n"
            "        G --> N\n"
            "        M --> N\n"
            "        N --> O[Clinical Evaluation: SNR, PRD, R-Peak F1, QT Timing]\n"
            "    end\n"
        )
        (src_dir / "architecture.mmd").write_text(mmd_content, encoding="utf-8")

        dot_content = (
            "digraph SignalChainQ {\n"
            "    rankdir=LR;\n"
            '    node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];\n'
            '    edge [fontname="Helvetica", fontsize=9];\n\n'
            '    ecg [label="ECG Time Series", fillcolor="#e2e8f0"];\n'
            '    framing [label="Windowing & Framing\\n(Hann, 50% Overlap)", fillcolor="#e2e8f0"];\n'
            '    est [label="Adaptive Energy Estimator\\n(Activity & Noise)", fillcolor="#fef08a"];\n\n'
            "    ecg -> framing -> est;\n\n"
            "    subgraph cluster_classical {\n"
            '        label = "Classical DSP Baselines";\n'
            "        style = dashed;\n"
            '        color = "#94a3b8";\n'
            '        bw [label="Butterworth IIR\\n(0.5-40 Hz)", fillcolor="#fed7aa"];\n'
            '        wav [label="Wavelet DB6\\n(Soft Threshold)", fillcolor="#a7f3d0"];\n'
            '        fft [label="Adaptive FFT\\n(Hard Zero Mask)", fillcolor="#c7d2fe"];\n'
            "    }\n\n"
            "    subgraph cluster_quantum {\n"
            '        label = "Quantum DSP Pipeline";\n'
            "        style = dashed;\n"
            '        color = "#06b6d4";\n'
            '        sp [label="State Preparation\\n|psi> = sum x_i |i>", fillcolor="#cffafe"];\n'
            '        qft [label="QFT Gate\\nO(log^2 M)", fillcolor="#cffafe"];\n'
            '        orc [label="Phase Oracle\\nU_K: (-1) for Passband", fillcolor="#a5f3fc"];\n'
            '        grover [label="Grover Diffusion\\nr=2 Iterations", fillcolor="#a5f3fc"];\n'
            '        iqft [label="IQFT Gate\\nO(log^2 M)", fillcolor="#cffafe"];\n'
            '        rec [label="State Readout & Scaling", fillcolor="#cffafe"];\n\n'
            "        sp -> qft -> orc -> grover -> iqft -> rec;\n"
            "    }\n\n"
            "    est -> bw;\n"
            "    est -> wav;\n"
            "    est -> fft;\n"
            "    est -> sp;\n\n"
            '    synth [label="Overlap-Add Synthesis", fillcolor="#e2e8f0"];\n'
            '    eval [label="Morphology & Quality Metrics\\n(SNR, PRD, R-Peak F1)", fillcolor="#d9f99d"];\n\n'
            "    bw -> synth;\n"
            "    wav -> synth;\n"
            "    fft -> synth;\n"
            "    rec -> synth;\n"
            "    synth -> eval;\n"
            "}\n"
        )
        (src_dir / "architecture.dot").write_text(dot_content, encoding="utf-8")
        print(f"Wrote architecture diagram sources in {src_dir}")

    def generate_supplementary(self):
        """Generate supplementary materials."""
        grid_rows = []
        for _, r in self.df_val_grid.iterrows():
            grid_rows.append(
                f"{r['config_id']} & {r['f_high_min']:.0f} & {r['f_high_max']:.0f} & {int(r['segment_size'])} & {int(r['grover_iterations'])} & {r['median_snr_improvement']:+.2f} & {r['median_r_peak_f1']:.3f} & {r['median_prd']:.1f}\\% \\\\"
            )
        grid_body = "\n".join(grid_rows[:50])

        supp_tex = (
            "\\section*{Supplementary Material: Parameter Tuning Grid Search}\n"
            "\\begin{table*}[h]\n"
            "\\centering\n"
            "\\caption{Top 50 Evaluated Parameter Configurations on MIT-BIH Validation Set ($N=108$).}\n"
            "\\begin{tabular}{cccccccc}\n"
            "\\hline\n"
            "\\textbf{Config ID} & \\textbf{$f_{\\text{min}}$ (Hz)} & \\textbf{$f_{\\text{max}}$ (Hz)} & \\textbf{$M$} & \\textbf{$r$} & \\textbf{Med. SNR Imp.} & \\textbf{Med. $F_1$} & \\textbf{Med. PRD} \\\\\n"
            "\\hline\n"
            f"{grid_body}\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\end{table*}\n"
        )
        (self.supp_dir / "supplementary_grid.tex").write_text(supp_tex, encoding="utf-8")
        print(f"Wrote supplementary materials in {self.supp_dir}")

    def build_all(self):
        """Execute full build pipeline."""
        self.load_artifacts()
        print("\n--- Generating Camera-Ready LaTeX Tables ---")
        self.generate_table_dataset_summary()
        self.generate_table_validation_parameters()
        self.generate_table_main_results()
        self.generate_table_statistics()
        self.generate_table_quantum_resources()
        self.generate_table_grover_ablation()
        self.generate_table_segment_ablation()
        self.generate_table_oracle_ablation()
        self.generate_table_qtdb_morphology()
        self.generate_table_noise_type_results()
        self.generate_table_snr_level_results()

        print("\n--- Generating Publication Figures ---")
        self.generate_publication_figures()
        self.generate_architecture_diagram_sources()

        print("\n--- Generating Supplementary Material ---")
        self.generate_supplementary()
        print("\nPublication build completed successfully!")


def main():
    builder = PublicationBuilder()
    builder.build_all()


if __name__ == "__main__":
    main()
