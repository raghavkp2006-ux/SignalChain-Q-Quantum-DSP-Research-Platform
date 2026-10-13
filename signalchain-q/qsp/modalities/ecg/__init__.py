"""ECG modality processing package."""
from qsp.modalities.ecg.io import generate_synthetic_lead, load_ecg_csv
from qsp.modalities.ecg.morphology import (
    detect_r_peaks_pantompkins,
    evaluate_r_peak_detections,
)
from qsp.modalities.ecg.noise import (
    get_noise_vector,
    mix_noise_at_snr,
)
from qsp.modalities.ecg.pipeline import run_ecg_pipeline
from qsp.modalities.ecg.preprocessing import (
    compute_adaptive_cutoffs_for_segments,
    get_marked_frequencies_mask,
)

__all__ = [
    "load_ecg_csv",
    "generate_synthetic_lead",
    "get_noise_vector",
    "mix_noise_at_snr",
    "detect_r_peaks_pantompkins",
    "evaluate_r_peak_detections",
    "compute_adaptive_cutoffs_for_segments",
    "get_marked_frequencies_mask",
    "run_ecg_pipeline",
]
