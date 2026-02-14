"""
Unified Learning System v8.5 (Slim)
====================================

Provides:
- LearningSystem: thin wrapper around LearningPatternRepository (used by tasks.py, streams.py)
- LearningOptimizerEngine: analyses product JSON quality, generates per-agent feedback
- FastAPI router: exposes learning/health/audit endpoints

Removed in v8.5 slim:
- LearningEnabledAgent, LearningEnabledTrinitySwarm (unused wrappers)
- run_enhanced_training + helpers (verbose training loop, never called in prod)
- AgentImprovementEngine (moved to orchestrator, then deleted — fake data)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Query

from backend.unified_quality_gates import (
    feedback_engine, FeedbackType, audit_logger, AuditLevel, AuditCategory,
)
from backend.unified_learning_repository import LearningPatternRepository, LearningPattern

logger = logging.getLogger("UnifiedLearningSystem")


# ============================================================================
# ENUMS & DATACLASSES
# ============================================================================

class ImprovementArea(Enum):
    CATEGORIZATION = "categorization"
    PRICING = "pricing"
    DATA_QUALITY = "data_quality"
    IMAGE_DETECTION = "image_detection"
    CONFIDENCE_CALIBRATION = "confidence"
    EDGE_CASES = "edge_cases"
    VALIDATION_RULES = "validation_rules"


@dataclass
class QualityAuditRecord:
    """Complete record of a product's quality journey through the pipeline."""
    product_id: str
    timestamp: datetime
    brand: str
    product_name: str
    completeness_score_before: float
    completeness_score_after: float
    accuracy_score: float
    security_score: float
    consistency_score: float
    scout_status: str
    verifier_status: str
    auditor_status: str
    scout_weaknesses: List[str]
    verifier_improvements: List[str]
    auditor_violations: List[str]
    final_tier: str
    final_score: float
    improvement_actions: List[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


@dataclass
class LearningMetric:
    agent_name: str
    metric_type: str
    current_value: float
    target_value: float
    improvement_percent: float
    category: ImprovementArea
    timestamp: str


@dataclass
class CycleResult:
    cycle_number: int
    timestamp: str
    agents_improved: List[str]
    accuracy_improvement: float
    metrics: List[Dict[str, Any]]
    bottlenecks: List[str]
    next_focus_areas: List[str]


# ============================================================================
# LEARNING SYSTEM — thin wrapper (used by tasks.py + streams.py)
# ============================================================================

class LearningSystem:
    def __init__(self):
        self.repo = LearningPatternRepository()

    def get_brand_insights(self, brand: str):
        return self.repo.get_brand_insights(brand)

    def get_most_recent_insight(self):
        return self.repo.get_most_recent_insight()

    def save_insight(self, brand, insight, product_id=None, category="General", confidence=0.8):
        self.repo.save_pattern(LearningPattern(
            pattern_id=f"auto_{int(datetime.now().timestamp())}",
            brand=brand,
            category=category,
            insight=insight,
            confidence=confidence,
            created_at=datetime.now().isoformat(),
            source="LearningSystem_Wrapper",
        ))


# ============================================================================
# LEARNING OPTIMIZER — analyses product data quality, generates feedback
# ============================================================================

class LearningOptimizerEngine:
    """Optimizes agent performance through feedback and learning cycles."""

    AGENT_NAMES = ["CommercialScout", "OfficialVerifier", "ExternalValidator"]

    def __init__(self):
        _backend = Path(__file__).resolve().parent
        self.learning_dir = _backend / "logs" / "learning_cycles"
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = _backend.parent / "frontend" / "public" / "data"
        self._prev_success_rate: float = 0.0

    # ── Quality metrics ────────────────────────────────────────────────

    def _get_quality_metrics(self) -> Dict[str, Any]:
        """Scan product JSON files and return quality statistics."""
        report: Dict[str, Any] = {
            "total_products": 0,
            "total_brands": 0,
            "avg_products_per_brand": 0,
            "quality_issues": {
                "missing_images": 0,
                "missing_prices": 0,
                "uncategorized": 0,
                "low_confidence_categories": 0,
            },
            "success_rate": 0.0,
            "categories_used": [],
        }
        total = 0
        brands = 0

        for bf in self.data_dir.glob("*.json"):
            if bf.stat().st_size <= 10:
                continue
            try:
                with open(bf) as f:
                    data = json.load(f)
                products = data if isinstance(
                    data, list) else data.get("products", [])
                if not products:
                    continue
                brands += 1
                total += len(products)
                for p in products:
                    if not p.get("official_images"):
                        report["quality_issues"]["missing_images"] += 1
                    if not p.get("price_il"):
                        report["quality_issues"]["missing_prices"] += 1
                    if not p.get("category"):
                        report["quality_issues"]["uncategorized"] += 1
                    if p.get("category_confidence", 100) < 80:
                        report["quality_issues"]["low_confidence_categories"] += 1
                    if p.get("category"):
                        report["categories_used"].append(p["category"])
            except Exception as e:
                logger.warning(f"Error analysing {bf.name}: {e}")

        report["total_products"] = total
        report["total_brands"] = brands
        report["avg_products_per_brand"] = total / brands if brands else 0
        if total:
            issues = sum(report["quality_issues"].values())
            report["success_rate"] = ((total - issues) / total) * 100
        report["categories_used"] = list(set(report["categories_used"]))
        return report

    # ── Per-agent feedback ─────────────────────────────────────────────

    def _agent_feedback(self, name: str, qm: Dict) -> Dict[str, Any]:
        fb: Dict[str, Any] = {"agent": name,
                              "focus_areas": [], "recommendations": []}
        issues = qm["quality_issues"]
        total = qm["total_products"]

        if name == "CommercialScout":
            fb["focus_areas"] = ["categorization", "data_quality"]
            if issues["uncategorized"]:
                fb["recommendations"].append(
                    f"Improve categorization: {issues['uncategorized']} products lack category"
                )
        elif name == "OfficialVerifier":
            fb["focus_areas"] = ["image_detection", "pricing"]
            if issues["missing_images"]:
                fb["recommendations"].append(
                    f"Improve image detection: {issues['missing_images']} missing images"
                )
            if issues["missing_prices"]:
                fb["recommendations"].append(
                    f"Enhance price extraction: {issues['missing_prices']} missing prices"
                )
        elif name == "ExternalValidator":
            fb["focus_areas"] = ["edge_cases", "validation_rules"]
            if qm["success_rate"] < 85:
                fb["recommendations"].append(
                    f"Relax validation rules: pass rate is {qm['success_rate']:.1f}%"
                )
        return fb

    # ── Learning cycle ─────────────────────────────────────────────────

    def run_learning_cycle(self, cycle_number: int = 1) -> CycleResult:
        logger.info(f"🔄 LEARNING CYCLE #{cycle_number}")
        qm = self._get_quality_metrics()
        prev_rate = self._prev_success_rate

        agents_improved = []
        metrics_data = []

        for agent in self.AGENT_NAMES:
            afb = self._agent_feedback(agent, qm)

            decision_id = feedback_engine.record_decision(
                agent_name=agent,
                decision_type=f"learning_cycle_{cycle_number}",
                input_data={"quality_metrics": qm},
                decision_output={"focus_areas": afb["focus_areas"],
                                 "recommendations": afb["recommendations"]},
                confidence=min(100, qm["success_rate"] + 10),
                reasoning=f"Identified {len(afb['focus_areas'])} improvement areas",
            )
            audit_logger.log_agent_action(
                agent_name=agent,
                action=f"completed_learning_cycle_{cycle_number}",
                input_data={"quality_metrics": qm},
                output_data={
                    "focus_areas": afb["focus_areas"], "decision_id": decision_id},
                success=True,
            )
            agents_improved.append(agent)

            m = LearningMetric(
                agent_name=agent,
                metric_type="learning_cycle",
                current_value=qm["success_rate"],
                target_value=98.0,
                improvement_percent=round(qm["success_rate"] - prev_rate, 2),
                category=ImprovementArea.DATA_QUALITY,
                timestamp=datetime.now().isoformat(),
            )
            md = asdict(m)
            md["category"] = md["category"].value
            metrics_data.append(md)

        actual_improvement = round(qm["success_rate"] - prev_rate, 2)
        self._prev_success_rate = qm["success_rate"]

        result = CycleResult(
            cycle_number=cycle_number,
            timestamp=datetime.now().isoformat(),
            agents_improved=agents_improved,
            accuracy_improvement=actual_improvement,
            metrics=metrics_data,
            bottlenecks=self._bottlenecks(qm),
            next_focus_areas=[ImprovementArea.IMAGE_DETECTION.value,
                              ImprovementArea.CATEGORIZATION.value],
        )

        # Persist
        try:
            out = self.learning_dir / \
                f"cycle_{cycle_number}_{datetime.now().isoformat()}.json"
            out.write_text(json.dumps(asdict(result), indent=2, default=str))
            logger.info(f"✅ Cycle #{cycle_number} saved to {out.name}")
        except Exception as e:
            logger.error(f"Failed to save cycle result: {e}")

        return result

    def _bottlenecks(self, qm: Dict) -> List[str]:
        total = qm["total_products"]
        if total == 0:
            return ["No products ingested yet"]
        issues = qm["quality_issues"]
        bs = []
        if issues["missing_images"] > total * 0.2:
            bs.append(
                f"Image Detection: {issues['missing_images']} products lack images")
        if issues["uncategorized"] > total * 0.1:
            bs.append(
                f"Categorization: {issues['uncategorized']} products lack categories")
        if issues["missing_prices"] > total * 0.15:
            bs.append(
                f"Pricing: {issues['missing_prices']} products lack prices")
        return bs or ["System performing well — minor optimisation opportunities only"]

    def get_learning_summary(self) -> Dict[str, Any]:
        cycles = []
        if self.learning_dir.exists():
            for f in sorted(self.learning_dir.glob("cycle_*.json")):
                try:
                    cycles.append(json.loads(f.read_text()))
                except Exception as exc:
                    logger.debug("Skipping corrupt cycle file: %s", exc)
        summary: Dict[str, Any] = {
            "total_cycles_completed": len(cycles),
            "cycles": cycles,
            "learning_status": "active" if cycles else "not_started",
            "timestamp": datetime.now().isoformat(),
        }
        if cycles:
            summary["latest_improvement_path"] = cycles[-1]
        return summary


# ============================================================================
# FASTAPI ROUTES — Learning Endpoints
# ============================================================================

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/health")
async def pipeline_health():
    try:
        health = feedback_engine.get_pipeline_health_report()
        return {
            "status": "healthy" if health["pipeline_accuracy"] > 70 else "needs_attention",
            "data": health,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/learning")
async def agent_learning_summary(agent_name: str):
    try:
        return {"agent": agent_name,
                "summary": feedback_engine.get_agent_learning_summary(agent_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/trail")
async def audit_trail(
    agent_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        trail = audit_logger.get_audit_trail(
            agent_name=agent_name, limit=limit)
        return {"count": len(trail), "events": trail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/security")
async def security_audit():
    try:
        audit = audit_logger.get_security_audit()
        return {"status": "secure" if audit["critical_events"] == 0 else "alert", "data": audit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def performance_metrics():
    try:
        perf = audit_logger.get_performance_report()
        return {"timestamp": perf["timestamp"], "metrics": perf["by_agent"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edge-cases")
async def edge_cases(agent_name: Optional[str] = Query(None)):
    try:
        cases = feedback_engine.get_edge_cases(agent_name=agent_name)
        return {"count": len(cases), "edge_cases": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{decision_id}")
async def submit_feedback(
    decision_id: str,
    feedback_type: str = Query(...),
    explanation: str = Query(""),
    impact_score: int = Query(50),
):
    feedback_map = {
        "override": FeedbackType.DECISION_OVERRIDE,
        "correction": FeedbackType.CORRECTION,
        "validation_pass": FeedbackType.VALIDATION_PASS,
        "edge_case": FeedbackType.EDGE_CASE,
    }
    ftype = feedback_map.get(feedback_type)
    if not ftype:
        raise HTTPException(
            status_code=400, detail=f"Invalid feedback_type: {feedback_type}")
    feedback_engine.submit_feedback(
        decision_id=decision_id,
        feedback_type=ftype,
        explanation=explanation,
        impact_score=impact_score,
    )
    return {"status": "submitted", "decision_id": decision_id, "feedback_type": feedback_type}


@router.get("/manifest")
async def learning_manifest():
    try:
        health = feedback_engine.get_pipeline_health_report()
        pct = min(100, (health["pipeline_accuracy"] / 98.0 * 100))
        perfection_map: Dict[str, Any] = {
            "overall_accuracy": {"current": health["pipeline_accuracy"], "target": 98.0, "progress_percent": pct},
            "agents": {},
            "timeline": {"current_phase": "Learning & Optimization", "phase_progress_percent": pct},
        }
        for name, summary in health["agents"].items():
            perfection_map["agents"][name] = {
                "current_accuracy": summary["accuracy"],
                "target_accuracy": 95.0,
                "decisions_made": summary["total_decisions"],
                "improvements_needed": len(summary["improvement_areas"]),
            }
        return {
            "timestamp": health["timestamp"],
            "perfection_map": perfection_map,
            "bottlenecks": health["bottlenecks"],
            "recommendations": health["recommendations"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ImprovementArea",
    "QualityAuditRecord",
    "LearningMetric",
    "CycleResult",
    "LearningSystem",
    "LearningOptimizerEngine",
    "router",
]
