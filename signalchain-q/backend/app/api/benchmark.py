"""Web interactive benchmark API endpoint (Section 25 & 27)."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
import numpy as np
from pydantic import BaseModel, Field

from backend.app.schemas.ecg import ProcessECGRequest
from qsp.benchmarks.runner import REQUIRED_METHODS
from qsp.modalities.ecg.io import generate_synthetic_lead
from qsp.modalities.ecg.pipeline import run_ecg_pipeline

router = APIRouter()


class MiniBenchmarkRequest(BaseModel):
    signal: Optional[List[float]] = None
    clean_reference: Optional[List[float]] = None
    sampling_rate_hz: float = Field(default=360.0, gt=0)
    methods: Optional[List[str]] = None
    max_duration_sec: float = Field(default=3.0, le=5.0)  # strict web limit


@router.post("/ecg")
def run_interactive_benchmark(req: MiniBenchmarkRequest):
    """Run an interactive 5-method comparison for web UI with strict execution limits."""
    fs = req.sampling_rate_hz

    if req.signal is not None:
        signal_data = np.array(req.signal, dtype=np.float64)
        clean_ref = np.array(req.clean_reference, dtype=np.float64) if req.clean_reference else None
    else:
        # Generate default synthetic demo
        demo = generate_synthetic_lead(duration_sec=min(req.max_duration_sec, 3.0), fs=fs)
        signal_data = demo.signal
        clean_ref = demo.signal

    # Web safety limit: cap at 1500 samples (~4 seconds at 360 Hz)
    max_samples = int(req.max_duration_sec * fs)
    if len(signal_data) > max_samples:
        signal_data = signal_data[:max_samples]
        if clean_ref is not None:
            clean_ref = clean_ref[:max_samples]

    methods_to_run = req.methods or REQUIRED_METHODS
    benchmark_results = []

    for m in methods_to_run:
        try:
            res = run_ecg_pipeline(
                signal=signal_data,
                method=m,
                fs=fs,
                clean_reference=clean_ref,
            )
            benchmark_results.append({
                "method": m,
                "output_snr_db": res.metrics.output_snr_db,
                "snr_improvement_db": res.metrics.snr_improvement_db,
                "rmse": res.metrics.rmse,
                "prd": res.metrics.prd,
                "pearson_r": res.metrics.pearson_r,
                "r_peak_f1": res.metrics.r_peak_f1,
                "runtime_ms": res.stage_timings_ms.get("total_ms", 0.0),
                "quantum_resources": res.quantum_resources.to_dict() if res.quantum_resources else None,
            })
        except Exception as e:
            benchmark_results.append({
                "method": m,
                "error": str(e),
            })

    return {
        "status": "success",
        "sample_count": len(signal_data),
        "sampling_rate_hz": fs,
        "results": benchmark_results,
        "disclaimer": "RESEARCH USE ONLY. NOT A DIAGNOSTIC DEVICE.",
    }
