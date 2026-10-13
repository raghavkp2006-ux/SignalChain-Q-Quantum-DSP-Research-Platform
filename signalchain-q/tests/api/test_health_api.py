"""API endpoint integration tests using FastAPI TestClient (Section 29)."""
from fastapi.testclient import TestClient
import pytest
from backend.app.main import app

client = TestClient(app)


def test_api_health():
    """Verify /api/health returns status 'ok' and environment info."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "SignalChain-Q API"
    assert "python_version" in data


def test_api_ecg_methods():
    """Verify /api/ecg/methods returns available methods."""
    response = client.get("/api/ecg/methods")
    assert response.status_code == 200
    data = response.json()
    method_ids = [m["id"] for m in data["methods"]]
    assert "raw" in method_ids
    assert "butterworth_bandpass" in method_ids
    assert "wavelet_db6" in method_ids
    assert "fft_adaptive_bandpass" in method_ids
    assert "qft_grover_ecg_adaptive" in method_ids


def test_api_ecg_process_json():
    """Verify /api/ecg/process with JSON signal array."""
    sig = [0.1 * (i % 10) for i in range(128)]
    payload = {
        "signal": sig,
        "sampling_rate_hz": 360.0,
        "method": "fft_adaptive_bandpass",
    }
    response = client.post("/api/ecg/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "fft_adaptive_bandpass"
    assert len(data["processed_signal"]) == len(sig)
    assert "disclaimer" in data
