"""PhysioNet connectivity and caching utility to prevent hanging network calls."""
import os
from typing import Optional
import urllib.request


_PHYSIONET_ONLINE: Optional[bool] = None


def is_physionet_online(timeout_sec: float = 1.0) -> bool:
    """Check if PhysioNet is reachable with a fast timeout.

    Caches the result to prevent repeated socket hangs.
    Can be forced offline by setting PHYSIONET_OFFLINE=1 environment variable.
    """
    global _PHYSIONET_ONLINE
    if _PHYSIONET_ONLINE is not None:
        return _PHYSIONET_ONLINE

    if os.environ.get("PHYSIONET_OFFLINE", "0").lower() in ("1", "true", "yes"):
        _PHYSIONET_ONLINE = False
        return False

    try:
        req = urllib.request.Request(
            "https://physionet.org",
            headers={"User-Agent": "SignalChain-Q/1.0 (Research Platform)"},
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            _PHYSIONET_ONLINE = (resp.status == 200)
    except Exception:
        _PHYSIONET_ONLINE = False

    return _PHYSIONET_ONLINE
