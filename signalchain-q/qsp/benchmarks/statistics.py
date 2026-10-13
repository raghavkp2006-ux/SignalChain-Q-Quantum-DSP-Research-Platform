"""Statistical testing, effect sizes, and bootstrap confidence intervals (Section 23)."""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def calculate_bootstrap_ci(
    data: np.ndarray,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 1448,
) -> Tuple[float, float]:
    """Compute non-parametric 95% bootstrap confidence interval of the median."""
    if len(data) == 0:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    boot_medians = np.zeros(n_bootstrap)
    n = len(data)
    for i in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        boot_medians[i] = np.median(sample)
    lower = float(np.percentile(boot_medians, 100.0 * (alpha / 2.0)))
    upper = float(np.percentile(boot_medians, 100.0 * (1.0 - alpha / 2.0)))
    return lower, upper


def calculate_cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Cliff's delta non-parametric effect size."""
    n_x, n_y = len(x), len(y)
    if n_x == 0 or n_y == 0:
        return 0.0
    greater = 0
    less = 0
    for val_x in x:
        greater += np.sum(val_x > y)
        less += np.sum(val_x < y)
    return float((greater - less) / (n_x * n_y))


def apply_holm_bonferroni(p_values: List[float]) -> List[float]:
    """Adjust p-values using the Holm step-down method (Section 23)."""
    m = len(p_values)
    if m == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m

    running_max = 0.0
    for rank, (orig_idx, p_val) in enumerate(indexed):
        adj_p = min(1.0, (m - rank) * p_val)
        running_max = max(running_max, adj_p)
        adjusted[orig_idx] = running_max

    return adjusted


def compute_paired_comparison_statistics(
    method_a_scores: np.ndarray,
    method_b_scores: np.ndarray,
    method_a_name: str,
    method_b_name: str,
    metric_name: str,
) -> Dict[str, float]:
    """Perform paired Wilcoxon signed-rank test and compute Cliff's delta."""
    diff = method_a_scores - method_b_scores
    if np.all(diff == 0):
        w_stat, p_val = 0.0, 1.0
    else:
        try:
            res = stats.wilcoxon(method_a_scores, method_b_scores)
            w_stat, p_val = float(res.statistic), float(res.pvalue)
        except Exception:
            w_stat, p_val = 0.0, 1.0

    delta = calculate_cliffs_delta(method_a_scores, method_b_scores)
    med_a = float(np.median(method_a_scores))
    iqr_a = float(stats.iqr(method_a_scores))
    med_b = float(np.median(method_b_scores))
    iqr_b = float(stats.iqr(method_b_scores))

    return {
        "method_a": method_a_name,
        "method_b": method_b_name,
        "metric": metric_name,
        "median_a": round(med_a, 4),
        "iqr_a": round(iqr_a, 4),
        "median_b": round(med_b, 4),
        "iqr_b": round(iqr_b, 4),
        "wilcoxon_stat": round(w_stat, 4),
        "p_value": round(p_val, 6),
        "cliffs_delta": round(delta, 4),
    }
