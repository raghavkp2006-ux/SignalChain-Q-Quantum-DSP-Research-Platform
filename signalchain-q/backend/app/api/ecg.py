"""ECG processing and method discovery API endpoints (Section 27)."""
import io
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile
import numpy as np
from backend.app.schemas.ecg import ECGProcessResponse, ProcessECGRequest
from qsp.modalities.ecg.io import load_ecg_csv
from qsp.modalities.ecg.pipeline import run_ecg_pipeline

router = APIRouter()

AVAILABLE_METHODS = [
    {
        "id": "raw",
        "name": "Raw Passthrough (C0)",
        "type": "classical",
        "description": "Baseline unfilter pass without modification.",
    },
    {
        "id": "butterworth_bandpass",
        "name": "Butterworth Bandpass (C1)",
        "type": "classical",
        "description": "4th-order SOS zero-phase Butterworth filter (0.5 - 40 Hz).",
    },
    {
        "id": "wavelet_db6",
        "name": "Wavelet Denoising (C2)",
        "type": "classical",
        "description": "Daubechies-6 wavelet with MAD universal soft-thresholding.",
    },
    {
        "id": "fft_adaptive_bandpass",
        "name": "Adaptive FFT Bandpass (C3)",
        "type": "classical",
        "description": "Classical fair equivalent applying exact adaptive marked band on identical segments.",
    },
    {
        "id": "qft_grover_ecg_adaptive",
        "name": "QFT + Adaptive Oracle + Grover (QSP)",
        "type": "quantum",
        "description": "ECG-aware quantum frequency denoiser using QFT, adaptive bandpass oracle, Grover amplification, and IQFT.",
    },
]


@router.get("/methods")
def get_available_methods():
    """List available classical DSP and quantum denoising pipelines."""
    return {"methods": AVAILABLE_METHODS}


@router.post("/process", response_model=ECGProcessResponse)
async def process_ecg_signal(request: Request):
    """Process an ECG signal via JSON body or uploaded multipart CSV."""
    clean_ref = None
    params = {}
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        method = str(form.get("method", "fft_adaptive_bandpass"))
        fs = float(form.get("sampling_rate_hz", 360.0))

        if not file or not hasattr(file, "read"):
            raise HTTPException(status_code=400, detail="Missing uploaded file.")
        content = await file.read()
        try:
            signal_data, fs, _ = load_ecg_csv(io.BytesIO(content), sampling_rate_hz=fs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
    else:
        try:
            body = await request.json()
            payload = ProcessECGRequest(**body)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON request: {str(e)}")

        if payload.signal is None:
            raise HTTPException(status_code=400, detail="Missing ECG data: provide 'signal' array.")

        signal_data = np.array(payload.signal, dtype=np.float64)
        fs = payload.sampling_rate_hz
        method = payload.method
        params = payload.parameters
        if payload.clean_reference is not None:
            clean_ref = np.array(payload.clean_reference, dtype=np.float64)

    # Validation
    if len(signal_data) < 64:
        raise HTTPException(status_code=400, detail="Signal too short: minimum 64 samples required.")
    if not np.all(np.isfinite(signal_data)):
        raise HTTPException(status_code=400, detail="Invalid numeric values: signal contains NaN or Inf.")

    try:
        res = run_ecg_pipeline(
            signal=signal_data,
            method=method,
            fs=fs,
            clean_reference=clean_ref,
            params=params,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    q_res = res.quantum_resources.to_dict() if res.quantum_resources else None

    return ECGProcessResponse(
        method=res.method_name,
        sampling_rate_hz=fs,
        input_samples_count=len(signal_data),
        input_signal=signal_data.tolist(),
        processed_signal=res.processed_signal.tolist(),
        metrics=res.metrics.to_dict(),
        stage_timings_ms=res.stage_timings_ms,
        quantum_resources=q_res,
        disclaimer="RESEARCH USE ONLY. NOT A DIAGNOSTIC DEVICE.",
    )
