"""Precise execution timing utilities for classical and quantum pipelines."""
import time
from typing import Dict


class StageTimer:
    """Timer supporting multiple named execution stages."""

    def __init__(self):
        self._timings_ms: Dict[str, float] = {}
        self._start_times: Dict[str, float] = {}

    def start(self, stage_name: str) -> None:
        """Start recording time for a given stage."""
        self._start_times[stage_name] = time.perf_counter()

    def stop(self, stage_name: str) -> float:
        """Stop timing the stage and record elapsed milliseconds."""
        if stage_name not in self._start_times:
            raise ValueError(f"Stage '{stage_name}' was never started.")
        elapsed = (time.perf_counter() - self._start_times.pop(stage_name)) * 1000.0
        self._timings_ms[stage_name] = self._timings_ms.get(stage_name, 0.0) + elapsed
        return elapsed

    def record(self, stage_name: str, duration_ms: float) -> None:
        """Manually record a stage duration in milliseconds."""
        self._timings_ms[stage_name] = self._timings_ms.get(stage_name, 0.0) + duration_ms

    def get_stage_ms(self, stage_name: str) -> float:
        """Return elapsed milliseconds for a single stage."""
        return self._timings_ms.get(stage_name, 0.0)

    def to_dict(self) -> Dict[str, float]:
        """Return a copy of all recorded stage timings in milliseconds."""
        return dict(self._timings_ms)

    def total_ms(self) -> float:
        """Total elapsed milliseconds across all recorded stages."""
        return sum(self._timings_ms.values())

    class _ContextStage:
        def __init__(self, timer: "StageTimer", stage_name: str):
            self.timer = timer
            self.stage_name = stage_name

        def __enter__(self):
            self.timer.start(self.stage_name)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.timer.stop(self.stage_name)

    def time_stage(self, stage_name: str):
        """Context manager to measure execution time of a code block."""
        return self._ContextStage(self, stage_name)
