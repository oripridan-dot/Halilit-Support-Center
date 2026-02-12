"""
Pipeline Telemetry — Observability for the Ingestion Pipeline

Provides structured metrics tracking for every pipeline run:
- Per-phase timing (harvest, normalize, validate, enrich, visual, cross-validate, publish)
- Success rates and throughput (items/second)
- Error aggregation
- Pipeline health dashboard across historical runs
- Persistent history for trend analysis

Usage:
    telemetry = PipelineTelemetry()

    with telemetry.run("harvest-2024") as run:
        with run.phase("harvest") as phase:
            phase.items_input = 100
            # ... do work ...
            phase.items_output = 95
            phase.items_failed = 5

        with run.phase("normalize") as phase:
            phase.items_input = 95
            # ...

    # Later: check health
    print(telemetry.get_health_status())
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from contextlib import contextmanager

logger = logging.getLogger("PipelineTelemetry")


# ---------------------------------------------------------------------------
# Phase metrics
# ---------------------------------------------------------------------------

@dataclass
class PhaseMetrics:
    """Metrics for a single pipeline phase execution."""
    phase_name: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    items_input: int = 0
    items_output: int = 0
    items_failed: int = 0
    items_skipped: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Fraction of items that succeeded."""
        total = self.items_input or 1
        return (total - self.items_failed) / total

    @property
    def throughput(self) -> float:
        """Items processed per second."""
        if self.duration_ms <= 0:
            return 0.0
        return self.items_output / (self.duration_ms / 1000)

    def summary(self) -> dict:
        return {
            "phase": self.phase_name,
            "duration": f"{self.duration_ms / 1000:.1f}s",
            "items": f"{self.items_output}/{self.items_input}",
            "failed": self.items_failed,
            "skipped": self.items_skipped,
            "success_rate": f"{self.success_rate:.1%}",
            "throughput": f"{self.throughput:.1f}/s",
        }


# ---------------------------------------------------------------------------
# Pipeline run
# ---------------------------------------------------------------------------

@dataclass
class PipelineRun:
    """Full pipeline run with all phase metrics."""
    run_id: str
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None
    total_duration_ms: float = 0.0
    phases: List[PhaseMetrics] = field(default_factory=list)
    products_in: int = 0
    products_out: int = 0
    overall_success: bool = False
    trigger: str = "manual"  # "manual" | "scheduled" | "api" | "webhook"

    @property
    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "trigger": self.trigger,
            "duration": f"{self.total_duration_ms / 1000:.1f}s",
            "products": f"{self.products_out}/{self.products_in}",
            "success": self.overall_success,
            "phases": {
                p.phase_name: p.summary() for p in self.phases
            },
        }


# ---------------------------------------------------------------------------
# Run context (yielded from telemetry.run())
# ---------------------------------------------------------------------------

class _RunContext:
    """
    Helper context for tracking phases within a pipeline run.
    Yielded by PipelineTelemetry.run() for structured phase tracking.
    """

    def __init__(self, pipeline_run: PipelineRun):
        self._run = pipeline_run

    @contextmanager
    def phase(self, phase_name: str):
        """
        Context manager for a single pipeline phase.

        Usage:
            with run.phase("harvest") as phase:
                phase.items_input = 100
                # ... do work ...
                phase.items_output = 95
        """
        metrics = PhaseMetrics(
            phase_name=phase_name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        start = time.monotonic()

        try:
            yield metrics
        except Exception as e:
            metrics.errors.append(str(e))
            raise
        finally:
            metrics.duration_ms = (time.monotonic() - start) * 1000
            metrics.completed_at = datetime.now(timezone.utc).isoformat()
            self._run.phases.append(metrics)

    @property
    def products_in(self) -> int:
        return self._run.products_in

    @products_in.setter
    def products_in(self, value: int):
        self._run.products_in = value

    @property
    def products_out(self) -> int:
        return self._run.products_out

    @products_out.setter
    def products_out(self, value: int):
        self._run.products_out = value


# ---------------------------------------------------------------------------
# Telemetry system
# ---------------------------------------------------------------------------

class PipelineTelemetry:
    """
    Tracks pipeline execution with structured, persistent metrics.

    Features:
    - Context-manager API for clean phase tracking
    - Auto-persists run history to JSON
    - Health status computation across recent runs
    - Last-N-runs history retrieval for dashboards
    """

    def __init__(
        self,
        history_path: Optional[Path] = None,
        max_history: int = 50,
    ):
        self.history_path = history_path or Path(
            "backend/data/pipeline_history.json"
        )
        self.max_history = max_history
        self._runs: List[dict] = []
        self._load_history()

    def _load_history(self):
        """Load run history from disk."""
        if self.history_path.exists():
            try:
                self._runs = json.loads(self.history_path.read_text())
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load pipeline history: {e}")
                self._runs = []

    def save(self):
        """Persist run history to disk."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        trimmed = self._runs[-self.max_history:]
        self.history_path.write_text(
            json.dumps(trimmed, indent=2, default=str)
        )

    @contextmanager
    def run(self, run_id: str, trigger: str = "manual"):
        """
        Context manager for a full pipeline run.

        Usage:
            with telemetry.run("run-001") as run:
                with run.phase("harvest") as phase:
                    ...
        """
        pipeline_run = PipelineRun(run_id=run_id, trigger=trigger)
        start = time.monotonic()

        try:
            yield _RunContext(pipeline_run)
            pipeline_run.overall_success = True
        except Exception as e:
            pipeline_run.overall_success = False
            logger.error(f"Pipeline run {run_id} failed: {e}")
            raise
        finally:
            pipeline_run.total_duration_ms = (time.monotonic() - start) * 1000
            pipeline_run.completed_at = datetime.now(timezone.utc).isoformat()
            self._runs.append(asdict(pipeline_run))
            self.save()

            # Log summary
            logger.info(
                f"Pipeline run {run_id} completed in "
                f"{pipeline_run.total_duration_ms / 1000:.1f}s: "
                f"{pipeline_run.products_out}/{pipeline_run.products_in} products"
            )

    def get_last_run(self) -> Optional[dict]:
        """Get the most recent pipeline run."""
        return self._runs[-1] if self._runs else None

    def get_history(self, limit: int = 10) -> List[dict]:
        """Get recent pipeline run history."""
        return self._runs[-limit:]

    def get_health_status(self) -> dict:
        """
        Compute overall pipeline health from recent runs.

        Returns status: healthy | degraded | unhealthy | no_data
        """
        if not self._runs:
            return {
                "status": "no_data",
                "message": "No pipeline runs recorded",
            }

        last = self._runs[-1]
        recent = self._runs[-5:]
        success_count = sum(1 for r in recent if r.get("overall_success"))
        success_rate = success_count / len(recent)

        if success_rate >= 0.8:
            status = "healthy"
        elif success_rate >= 0.5:
            status = "degraded"
        else:
            status = "unhealthy"

        # Compute average duration
        durations = [
            r.get("total_duration_ms", 0) for r in recent
            if r.get("overall_success")
        ]
        avg_duration_ms = (
            sum(durations) / len(durations) if durations else 0
        )

        return {
            "status": status,
            "last_run_id": last.get("run_id"),
            "last_success": last.get("overall_success"),
            "last_completed": last.get("completed_at"),
            "recent_success_rate": f"{success_rate:.0%}",
            "avg_duration_seconds": round(avg_duration_ms / 1000, 1),
            "total_runs": len(self._runs),
        }

    def get_phase_averages(self, limit: int = 10) -> dict:
        """Compute average metrics per phase across recent runs."""
        recent = self._runs[-limit:]
        phase_totals: dict = {}

        for run in recent:
            for phase in run.get("phases", []):
                name = phase.get("phase_name", "unknown")
                if name not in phase_totals:
                    phase_totals[name] = {
                        "duration_ms": [],
                        "success_rate": [],
                        "items": [],
                    }
                phase_totals[name]["duration_ms"].append(
                    phase.get("duration_ms", 0)
                )
                inputs = phase.get("items_input", 0)
                failed = phase.get("items_failed", 0)
                rate = (inputs - failed) / max(inputs, 1)
                phase_totals[name]["success_rate"].append(rate)
                phase_totals[name]["items"].append(
                    phase.get("items_output", 0)
                )

        averages = {}
        for name, totals in phase_totals.items():
            n = len(totals["duration_ms"])
            averages[name] = {
                "avg_duration_ms": round(
                    sum(totals["duration_ms"]) / max(n, 1), 1
                ),
                "avg_success_rate": round(
                    sum(totals["success_rate"]) / max(n, 1), 4
                ),
                "avg_items": round(
                    sum(totals["items"]) / max(n, 1), 1
                ),
                "sample_count": n,
            }

        return averages


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_pipeline_telemetry: Optional[PipelineTelemetry] = None


def get_pipeline_telemetry() -> PipelineTelemetry:
    """Get or create the singleton PipelineTelemetry."""
    global _pipeline_telemetry
    if _pipeline_telemetry is None:
        _pipeline_telemetry = PipelineTelemetry()
    return _pipeline_telemetry
