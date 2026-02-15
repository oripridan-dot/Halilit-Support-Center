"""
Pipeline Review Agent — JIT Architecture

Single agent that observes the full ingestion pipeline (commercial → enrich → sync → rebuild-catalog),
validates each phase output, and proactively improves on the fly:
- Validates product counts, file existence, and catalog health after rebuild
- Triggers retries with backoff on phase failure
- Suggests and can trigger resolve_catalog when health drops
- Logs all decisions and improvements for audit

Usage:
  Used by conductor_main.py when running: ingest-all --with-review-agent
  Or run standalone to validate current state: python -m backend.ingestion.pipeline_review_agent --validate-now
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Allow running as script
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logger = logging.getLogger("PipelineReviewAgent")

# Minimum acceptable health score before suggesting resolution (0–100)
HEALTH_SCORE_FLOOR = 40
# Max retries per phase before giving up
MAX_PHASE_RETRIES = 2
# Backoff seconds between retries
RETRY_BACKOFF_BASE = 10


class PipelineReviewAgent:
    """
    Reviews the entire ingestion process: validates after each phase and can
    trigger retries or corrective actions (e.g. resolve_catalog) on the fly.
    """

    def __init__(
        self,
        frontend_data_dir: Optional[Path] = None,
        health_floor: int = HEALTH_SCORE_FLOOR,
        max_retries: int = MAX_PHASE_RETRIES,
        on_improve: Optional[Callable[[str, Dict], None]] = None,
    ):
        self.frontend_data_dir = frontend_data_dir or (ROOT / "frontend" / "public" / "data")
        self.health_floor = health_floor
        self.max_retries = max_retries
        self.on_improve = on_improve or (lambda phase, data: None)
        self._phase_results: Dict[str, Dict[str, Any]] = {}
        self._decisions: List[Dict[str, Any]] = []

    def _record_decision(self, phase: str, action: str, reason: str, detail: Optional[Dict] = None):
        entry = {
            "phase": phase,
            "action": action,
            "reason": reason,
            "detail": detail or {},
            "ts": time.time(),
        }
        self._decisions.append(entry)
        logger.info(f"[Review] {phase}: {action} — {reason}")

    def validate_after_commercial(self) -> Tuple[bool, str, Dict]:
        """
        After commercial-ingest: check brand JSONs exist and have products.
        Returns (ok, message, stats).
        """
        if not self.frontend_data_dir.exists():
            return False, "frontend data dir missing", {}
        exclude = {"index", "search_index", "search_index_min", "galaxy_db", "sample", "inventory"}
        total = 0
        brands = []
        for f in self.frontend_data_dir.glob("*.json"):
            if f.stem in exclude:
                continue
            try:
                with open(f) as fp:
                    data = json.load(fp)
                count = len(data) if isinstance(data, list) else len(data.get("products", []))
                total += count
                brands.append(f.stem)
            except Exception as e:
                self._record_decision("commercial", "warn", f"Failed to read {f.name}: {e}")
        ok = total > 0 and len(brands) > 0
        msg = f"{total} products across {len(brands)} brands" if ok else "no products or brands found"
        stats = {"total_products": total, "brands": brands, "brand_count": len(brands)}
        self._phase_results["commercial"] = {"ok": ok, "message": msg, "stats": stats}
        return ok, msg, stats

    def validate_after_enrich(self) -> Tuple[bool, str, Dict]:
        """After enrich: same as commercial (we still have brand JSONs)."""
        return self.validate_after_commercial()

    def validate_after_sync(self) -> Tuple[bool, str, Dict]:
        """After sync: index and search artifacts should exist."""
        index_file = self.frontend_data_dir / "index.json"
        ok = index_file.exists()
        msg = "index.json present" if ok else "index.json missing"
        stats = {"index_exists": ok}
        self._phase_results["sync"] = {"ok": ok, "message": msg, "stats": stats}
        return ok, msg, stats

    def validate_after_rebuild_catalog(self) -> Tuple[bool, str, Dict]:
        """
        After rebuild-catalog: build catalog in memory and run health check.
        If health is below floor, suggest/trigger resolve and re-build.
        """
        try:
            from backend.product_normalizer import build_catalog
            catalog = build_catalog(str(self.frontend_data_dir), resolve=False)
            products = catalog.get("products", [])
            if not products:
                self._phase_results["rebuild_catalog"] = {"ok": False, "message": "no products in catalog", "stats": {}}
                return False, "no products in catalog", {}

            from backend.catalog_validator import validate_catalog, resolve_catalog
            health = validate_catalog(products)
            score = health.get("health_score", 0)
            status = health.get("health_status", "MINIMAL")
            ok = score >= self.health_floor
            msg = f"health_score={score} ({status})"
            stats = {
                "total_products": len(products),
                "health_score": score,
                "health_status": status,
                "top_issues": health.get("top_issues", [])[:3],
            }
            self._phase_results["rebuild_catalog"] = {"ok": ok, "message": msg, "stats": stats, "health": health}

            if not ok and score > 0:
                self._record_decision(
                    "rebuild_catalog",
                    "suggest_resolve",
                    f"Health {score} below floor {self.health_floor}; run with resolve=True or call resolve_catalog",
                    {"health_score": score, "health_floor": self.health_floor},
                )
                self.on_improve("rebuild_catalog", {"suggested": "resolve_catalog", "health": health})
            return ok, msg, stats
        except Exception as e:
            logger.warning(f"Review: rebuild_catalog validation failed: {e}")
            self._phase_results["rebuild_catalog"] = {"ok": False, "message": str(e), "stats": {}}
            return False, str(e), {}

    def run_with_review(
        self,
        run_commercial: Callable[[], bool],
        run_enrich: Callable[[], bool],
        run_sync: Callable[[], bool],
        run_rebuild_catalog: Callable[[], None],
    ) -> bool:
        """
        Execute the full pipeline with review after each phase. On validation failure,
        retry the phase up to max_retries (with backoff). Proactively suggest resolve
        when final health is low.
        """
        steps = [
            ("commercial", run_commercial, self.validate_after_commercial),
            ("enrich", run_enrich, self.validate_after_enrich),
            ("sync", run_sync, self.validate_after_sync),
            ("rebuild_catalog", run_rebuild_catalog, self.validate_after_rebuild_catalog),
        ]
        for phase_name, run_fn, validate_fn in steps:
            for attempt in range(self.max_retries + 1):
                if attempt > 0:
                    wait = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                    self._record_decision(phase_name, "retry", f"Attempt {attempt + 1} after {wait}s backoff", {"attempt": attempt})
                    time.sleep(wait)
                # Run phase (rebuild_catalog is no-arg)
                if phase_name == "rebuild_catalog":
                    try:
                        run_rebuild_catalog()
                    except Exception as e:
                        logger.warning(f"Phase {phase_name} failed: {e}")
                        ok, msg, stats = False, str(e), {}
                    else:
                        ok, msg, stats = validate_fn()
                else:
                    success = run_fn()
                    ok, msg, stats = validate_fn()
                    if not success and attempt < self.max_retries:
                        ok = False
                        msg = "phase returned failure"
                logger.info(f"[Review] {phase_name} -> ok={ok} ({msg})")
                if ok:
                    break
                if attempt == self.max_retries:
                    self._record_decision(phase_name, "fail", f"Failed after {self.max_retries + 1} attempts", {"message": msg})
                    return False
        return True

    def get_decisions(self) -> List[Dict[str, Any]]:
        return list(self._decisions)

    def get_phase_results(self) -> Dict[str, Dict]:
        return dict(self._phase_results)


def main_validate_now():
    """CLI: validate current pipeline state without running ingestion."""
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    agent = PipelineReviewAgent()
    agent.validate_after_commercial()
    agent.validate_after_sync()
    # Rebuild not run — just load catalog if possible and validate health
    try:
        from backend.product_normalizer import build_catalog
        data_dir = str(ROOT / "frontend" / "public" / "data")
        catalog = build_catalog(data_dir, resolve=False)
        from backend.catalog_validator import validate_catalog
        health = validate_catalog(catalog.get("products", []))
        print(json.dumps(health, indent=2))
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Pipeline Review Agent — validate or run with review")
    p.add_argument("--validate-now", action="store_true", help="Validate current data state and print health")
    args = p.parse_args()
    if args.validate_now:
        sys.exit(main_validate_now())
    p.print_help()
    sys.exit(0)
