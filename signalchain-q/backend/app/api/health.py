"""Health check API endpoint (Section 27)."""
import sys
from fastapi import APIRouter
from backend.app.schemas.ecg import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Verify backend health and runtime availability."""
    try:
        import qiskit
        qiskit_ok = True
    except ImportError:
        qiskit_ok = False

    try:
        import qiskit_aer
        aer_ok = True
    except ImportError:
        aer_ok = False

    return HealthResponse(
        status="ok",
        service="SignalChain-Q API",
        version="0.1.0",
        python_version=sys.version.split()[0],
        qiskit_available=qiskit_ok,
        aer_available=aer_ok,
    )
