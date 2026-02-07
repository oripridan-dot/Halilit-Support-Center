"""
LEARNING PIPELINE ENDPOINTS - v7.2
===================================

REST API endpoints for exposing agent learning metrics, audit logs, and health status.
These endpoints allow external systems to monitor agent intelligence growth.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from backend.agents.feedback_engine import feedback_engine
from backend.agents.audit_system import audit_logger, AuditCategory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/health")
async def pipeline_health():
    """
    Get comprehensive pipeline health report.

    Shows:
    - Overall pipeline accuracy
    - Agent learning progress
    - Bottlenecks and recommendations
    """
    try:
        health = feedback_engine.get_pipeline_health_report()
        return {
            "status": "healthy" if health["pipeline_accuracy"] > 70 else "needs_attention",
            "data": health,
        }
    except Exception as e:
        logger.error(f"Failed to get health report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/learning")
async def agent_learning_summary(agent_name: str):
    """
    Get detailed learning summary for a specific agent.

    Shows:
    - Total decisions made
    - Accuracy percentage
    - Common errors
    - Improvement areas
    """
    try:
        summary = feedback_engine.get_agent_learning_summary(agent_name)
        return {
            "agent": agent_name,
            "summary": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get learning summary for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/trail")
async def audit_trail(
    agent_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get audit trail filtered by agent and/or limit.

    Shows:
    - Recent operations
    - Execution times
    - Status (success/failure)
    """
    try:
        trail = audit_logger.get_audit_trail(
            agent_name=agent_name, limit=limit)
        return {
            "count": len(trail),
            "events": trail,
        }
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/security")
async def security_audit():
    """
    Get security audit report.

    Shows:
    - Recent security events
    - Critical findings
    - Threat levels
    """
    try:
        audit = audit_logger.get_security_audit()
        return {
            "status": "secure" if audit["critical_events"] == 0 else "alert",
            "data": audit,
        }
    except Exception as e:
        logger.error(f"Failed to get security audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def performance_metrics():
    """
    Get agent performance metrics.

    Shows:
    - Success rates
    - Execution times
    - Efficiency metrics
    """
    try:
        perf = audit_logger.get_performance_report()
        return {
            "timestamp": perf["timestamp"],
            "metrics": perf["by_agent"],
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edge-cases")
async def edge_cases(agent_name: Optional[str] = Query(None)):
    """
    Get all discovered edge cases.

    Useful for:
    - Understanding system blindspots
    - Training new versions
    - Improving robustness
    """
    try:
        cases = feedback_engine.get_edge_cases(agent_name=agent_name)
        return {
            "count": len(cases),
            "edge_cases": cases,
        }
    except Exception as e:
        logger.error(f"Failed to get edge cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{decision_id}")
async def submit_feedback(
    decision_id: str,
    feedback_type: str = Query(...),
    explanation: str = Query(""),
    impact_score: int = Query(50),
):
    """
    Submit feedback about an agent's decision.

    This closes the learning loop and enables the agents to improve.

    feedback_type options:
    - override: Human overrode the decision
    - correction: Agent made a mistake
    - validation_pass: Decision was correct
    - edge_case: Unexpected scenario
    """
    try:
        from backend.agents.feedback_engine import FeedbackType

        # Map string to FeedbackType
        feedback_map = {
            "override": FeedbackType.DECISION_OVERRIDE,
            "correction": FeedbackType.CORRECTION,
            "validation_pass": FeedbackType.VALIDATION_PASS,
            "edge_case": FeedbackType.EDGE_CASE,
        }

        ftype = feedback_map.get(feedback_type)
        if not ftype:
            raise ValueError(f"Invalid feedback_type: {feedback_type}")

        feedback_engine.submit_feedback(
            decision_id=decision_id,
            feedback_type=ftype,
            explanation=explanation,
            impact_score=impact_score,
        )

        return {
            "status": "submitted",
            "decision_id": decision_id,
            "feedback_type": feedback_type,
        }
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/manifest")
async def learning_manifest():
    """
    Get the complete learning manifest showing the path to perfection.

    Returns:
    - Current state accuracy
    - Target perfection map
    - Progress toward goals
    - Estimated time to goal
    """
    try:
        health = feedback_engine.get_pipeline_health_report()

        # Define perfection map
        perfection_map = {
            "overall_accuracy": {
                "current": health["pipeline_accuracy"],
                "target": 98.0,
                "progress_percent": min(100, (health["pipeline_accuracy"] / 98.0 * 100)),
            },
            "agents": {},
            "timeline": {
                "current_phase": "Learning & Optimization",
                "phase_progress_percent": min(100, (health["pipeline_accuracy"] / 98.0 * 100)),
            },
        }

        for agent_name, summary in health["agents"].items():
            perfection_map["agents"][agent_name] = {
                "current_accuracy": summary["accuracy"],
                "target_accuracy": 95.0,
                "decisions_made": summary["total_decisions"],
                "improvements_needed": len(summary["improvement_areas"]),
                "path_to_perfection": {
                    "phase_1_foundations": "Complete" if summary["accuracy"] > 70 else "In Progress",
                    "phase_2_refinement": "Complete" if summary["accuracy"] > 85 else "Pending",
                    "phase_3_mastery": "Complete" if summary["accuracy"] > 95 else "Pending",
                },
            }

        return {
            "timestamp": health["timestamp"],
            "perfection_map": perfection_map,
            "bottlenecks": health["bottlenecks"],
            "recommendations": health["recommendations"],
        }
    except Exception as e:
        logger.error(f"Failed to get learning manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))
