"""Pydantic schemas for ECG processing and API requests/responses (Section 27)."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "SignalChain-Q API"
    version: str = "0.1.0"
    python_version: str
    qiskit_available: bool = True
    aer_available: bool = True


class ProcessECGRequest(BaseModel):
    signal: Optional[List[float]] = None
    sampling_rate_hz: float = Field(default=360.0, gt=0)
    method: str = Field(default="fft_adaptive_bandpass")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    clean_reference: Optional[List[float]] = None


class ECGProcessResponse(BaseModel):
    method: str
    sampling_rate_hz: float
    input_samples_count: int
    input_signal: List[float]
    processed_signal: List[float]
    metrics: Dict[str, Any]
    stage_timings_ms: Dict[str, float]
    quantum_resources: Optional[Dict[str, Any]] = None
    disclaimer: str = "RESEARCH USE ONLY. NOT A DIAGNOSTIC DEVICE."


class ECGExampleItem(BaseModel):
    example_id: str
    name: str
    description: str
    sampling_rate_hz: float
    duration_sec: float
    signal_preview: List[float]
