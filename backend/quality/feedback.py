"""
Feedback Engine — Learning signal collection for Trinity Swarm.
Split from unified_quality_gates.py Section 4.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import asdict

from backend.quality.models import (
    FeedbackType, AgentDecision, FeedbackRecord,
)

logger = logging.getLogger(__name__)


class FeedbackEngine:
    """
    Manages feedback collection and learning signals for agents.
    Records decisions, captures feedback, identifies patterns.
    """

    def __init__(self):
        self.decisions: Dict[str, AgentDecision] = {}
        self.feedback: List[FeedbackRecord] = []
        self.agent_metrics: Dict[str, Dict] = {}
        self.feedback_log_path = str(
            Path(__file__).resolve().parent.parent / "logs" / "feedback")
        os.makedirs(self.feedback_log_path, exist_ok=True)
        self._load_feedback_history()

    def record_decision(self, agent_name: str, decision_type: str,
                        input_data: Dict, decision_output: Dict,
                        confidence: float, reasoning: str) -> str:
        decision_id = f"{agent_name}_{decision_type}_{datetime.now().isoformat()}"
        decision = AgentDecision(
            decision_id=decision_id, agent_name=agent_name,
            decision_type=decision_type, input_data=input_data,
            decision_output=decision_output, confidence=confidence,
            reasoning=reasoning, timestamp=datetime.now().isoformat(),
            status="pending_review",
        )
        self.decisions[decision_id] = decision
        self._save_decision(decision)
        logger.info(
            f"Recorded decision: {decision_id} (confidence: {confidence}%)")
        return decision_id

    def submit_feedback(self, decision_id: str, feedback_type: FeedbackType,
                        correction: Optional[Dict] = None,
                        explanation: str = "", impact_score: int = 50) -> None:
        if decision_id not in self.decisions:
            logger.warning(f"Decision not found: {decision_id}")
            return

        decision = self.decisions[decision_id]
        feedback_id = f"fb_{decision_id}_{datetime.now().isoformat()}"
        feedback = FeedbackRecord(
            feedback_id=feedback_id, decision_id=decision_id,
            agent_name=decision.agent_name, feedback_type=feedback_type,
            correction=correction, explanation=explanation,
            impact_score=impact_score, timestamp=datetime.now().isoformat(),
        )
        self.feedback.append(feedback)

        if feedback_type == FeedbackType.VALIDATION_PASS:
            decision.status = "approved"
        elif feedback_type in (FeedbackType.CORRECTION, FeedbackType.DECISION_OVERRIDE):
            decision.status = "rejected"

        self._save_feedback(feedback)
        self._update_agent_metrics(feedback)
        logger.info(
            f"Feedback: {feedback_id} ({feedback_type.value}, impact: {impact_score})")

    def get_agent_learning_summary(self, agent_name: str) -> Dict:
        agent_decisions = [
            d for d in self.decisions.values() if d.agent_name == agent_name]
        agent_feedback = [
            f for f in self.feedback if f.agent_name == agent_name]

        if not agent_decisions:
            return {"agent": agent_name, "summary": "No decisions recorded yet"}

        total = len(agent_decisions)
        approved = len([d for d in agent_decisions if d.status == "approved"])
        rejected = len([d for d in agent_decisions if d.status == "rejected"])
        pending = len(
            [d for d in agent_decisions if d.status == "pending_review"])
        accuracy = (approved / total * 100) if total > 0 else 0

        corrections = [
            f for f in agent_feedback if f.feedback_type == FeedbackType.CORRECTION]
        common_errors = {}
        for c in corrections:
            error_type = c.explanation.split(
                ":")[0] if c.explanation else "unknown"
            common_errors[error_type] = common_errors.get(error_type, 0) + 1

        high_conf_correct = len(
            [d for d in agent_decisions if d.confidence >= 80 and d.status == "approved"])

        return {
            "agent": agent_name, "total_decisions": total,
            "accuracy": round(accuracy, 2),
            "approved": approved, "rejected": rejected,
            "pending_review": pending,
            "confidence_score": round(
                sum(d.confidence for d in agent_decisions) / total, 2),
            "high_confidence_correct": high_conf_correct,
            "common_errors": common_errors,
            "improvement_areas": self._identify_improvement_areas(agent_name),
            "timestamp": datetime.now().isoformat(),
        }

    def get_pipeline_health_report(self) -> Dict:
        agent_names = set(d.agent_name for d in self.decisions.values())
        summaries = {a: self.get_agent_learning_summary(
            a) for a in agent_names}

        total = len(self.decisions)
        approved = len([d for d in self.decisions.values()
                       if d.status == "approved"])
        accuracy = (approved / total * 100) if total > 0 else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "pipeline_accuracy": round(accuracy, 2),
            "total_decisions": total,
            "total_feedback_received": len(self.feedback),
            "agents": summaries,
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations(summaries),
        }

    def get_edge_cases(self, agent_name: Optional[str] = None) -> List[Dict]:
        cases = [f for f in self.feedback if f.feedback_type ==
                 FeedbackType.EDGE_CASE]
        if agent_name:
            cases = [f for f in cases if f.agent_name == agent_name]
        return [{"agent": f.agent_name, "case": f.explanation,
                 "correction": f.correction, "timestamp": f.timestamp}
                for f in cases]

    # ── Private ──────────────────────────────────────────────────────────

    def _identify_improvement_areas(self, agent_name: str) -> List[str]:
        agent_feedback = [
            f for f in self.feedback if f.agent_name == agent_name]
        areas = []
        high_impact = [f for f in agent_feedback if f.impact_score >= 70]
        if high_impact:
            areas.append(f"Fix high-impact issues ({len(high_impact)} cases)")

        agent_decisions = [
            d for d in self.decisions.values() if d.agent_name == agent_name]
        low_conf_rejected = len([
            d for d in agent_decisions if d.status == "rejected" and d.confidence < 60])
        if low_conf_rejected:
            areas.append(
                f"Improve confidence calibration ({low_conf_rejected} cases)")

        edge_cases = [
            f for f in agent_feedback if f.feedback_type == FeedbackType.EDGE_CASE]
        if edge_cases:
            areas.append(f"Handle edge cases ({len(edge_cases)} identified)")
        return areas

    def _identify_bottlenecks(self) -> List[str]:
        bottlenecks = []
        for agent_name in set(d.agent_name for d in self.decisions.values()):
            summary = self.get_agent_learning_summary(agent_name)
            if summary.get("accuracy", 0) < 70:
                bottlenecks.append(
                    f"{agent_name} has low accuracy ({summary['accuracy']}%)")
        return bottlenecks

    def _generate_recommendations(self, summaries: Dict) -> List[str]:
        recs = []
        for agent, summary in summaries.items():
            for area in summary.get("improvement_areas", []):
                recs.append(f"[{agent}] {area}")
        return recs

    def _save_decision(self, decision: AgentDecision) -> None:
        path = os.path.join(self.feedback_log_path,
                            f"decision_{decision.decision_id}.json")
        with open(path, "w") as f:
            json.dump(asdict(decision), f, indent=2)

    def _save_feedback(self, feedback: FeedbackRecord) -> None:
        path = os.path.join(self.feedback_log_path,
                            f"feedback_{feedback.feedback_id}.json")
        with open(path, "w") as f:
            json.dump(asdict(feedback), f, indent=2, default=str)

    def _load_feedback_history(self) -> None:
        if not os.path.exists(self.feedback_log_path):
            return
        for filename in os.listdir(self.feedback_log_path):
            if filename.startswith("decision_"):
                try:
                    with open(os.path.join(self.feedback_log_path, filename), "r") as f:
                        data = json.load(f)
                        decision = AgentDecision(**data)
                        self.decisions[decision.decision_id] = decision
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")

    def _update_agent_metrics(self, feedback: FeedbackRecord) -> None:
        agent = feedback.agent_name
        if agent not in self.agent_metrics:
            self.agent_metrics[agent] = {
                "total_feedback": 0, "positive": 0,
                "negative": 0, "impact_weighted_score": 0,
            }
        self.agent_metrics[agent]["total_feedback"] += 1
        if feedback.feedback_type == FeedbackType.VALIDATION_PASS:
            self.agent_metrics[agent]["positive"] += 1
        elif feedback.feedback_type in (FeedbackType.CORRECTION, FeedbackType.DECISION_OVERRIDE):
            self.agent_metrics[agent]["negative"] += 1
        self.agent_metrics[agent]["impact_weighted_score"] += feedback.impact_score
