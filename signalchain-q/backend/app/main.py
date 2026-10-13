"""FastAPI application entrypoint for SignalChain-Q (Section 27)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.benchmark import router as benchmark_router
from backend.app.api.datasets import router as datasets_router
from backend.app.api.ecg import router as ecg_router
from backend.app.api.health import router as health_router

app = FastAPI(
    title="SignalChain-Q API",
    description="ECG-First Classical + Quantum DSP Research Platform API",
    version="0.1.0",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(ecg_router, prefix="/api/ecg", tags=["ECG Processing"])
app.include_router(datasets_router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(benchmark_router, prefix="/api/benchmark", tags=["Benchmark"])


@app.get("/")
def read_root():
    return {
        "project": "SignalChain-Q",
        "description": "ECG-First Classical + Quantum DSP Research Platform",
        "version": "0.1.0",
        "disclaimer": "RESEARCH USE ONLY. NOT A DIAGNOSTIC DEVICE. No guaranteed quantum advantage claimed.",
        "docs_url": "/docs",
    }
