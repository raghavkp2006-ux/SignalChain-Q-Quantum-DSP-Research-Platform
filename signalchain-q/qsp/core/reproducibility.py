"""Reproducibility utilities: deterministic seeding, environment snapshots, and config hashing."""
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
from typing import Any, Dict
import numpy as np

DEFAULT_PROJECT_SEED = 1448


def seed_everything(seed: int = DEFAULT_PROJECT_SEED) -> int:
    """Set random seeds across Python and NumPy for reproducible execution."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    return seed


def get_git_commit_hash(repo_dir: str = ".") -> str:
    """Get the current git commit SHA if available."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "git_commit_unavailable"


def compute_config_hash(config_dict: Dict[str, Any]) -> str:
    """Compute deterministic SHA256 hex digest of a configuration dictionary."""
    serialized = json.dumps(config_dict, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def capture_environment_metadata(repo_dir: str = ".") -> Dict[str, Any]:
    """Capture runtime environment snapshot as required by Section 4 and Section 24."""
    packages = {}
    tracked = [
        "numpy",
        "scipy",
        "pandas",
        "wfdb",
        "pywt",
        "sklearn",
        "statsmodels",
        "matplotlib",
        "fastapi",
        "uvicorn",
        "pydantic",
        "qiskit",
        "qiskit_aer",
    ]
    for pkg in tracked:
        try:
            mod = __import__(pkg)
            packages[pkg] = getattr(mod, "__version__", "installed")
        except ImportError:
            packages[pkg] = "not_installed"

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "system": platform.system(),
        "git_commit": get_git_commit_hash(repo_dir),
        "packages": packages,
    }
