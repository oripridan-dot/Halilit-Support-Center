"""
FEEDBACK ENGINE - v7.2 LEARNING LOOP SYSTEM
============================================

Captures agent decisions, outcomes, and feedback to enable continuous learning.
This is the "nervous system" that closes the loop between actions and improvements.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback the system can capture"""
    DECISION_OVERRIDE = "override"  # Human overrode agent decision
    CORRECTION = "correction"  # Agent made a mistake
    VALIDATION_PASS = "validation_pass"  # Agent's work passed review
    EDGE_CASE = "edge_case"  # Unexpected scenario encountered
    PERFORMANCE = "performance"  # Speed/efficiency metrics
    USER_SATISFACTION = "user_satisfaction"  # User feedback
    CONSISTENCY = "consistency"  # Pattern consistency tracking


@dataclass
class AgentDecision:
    """A single decision made by an agent"""
    decision_id: str
    agent_name: str
    decision_type: str  # e.g., "categorize", "enrich", "validate"
    input_data: Dict[str, Any]
    decision_output: Dict[str, Any]
    confidence: float  # 0-100
    reasoning: str
    timestamp: str
    status: str  # "pending_review", "approved", "rejected"


@dataclass
class FeedbackRecord:
    """Feedback about an agent's decision"""
    feedback_id: str
    decision_id: str
    agent_name: str
    feedback_type: FeedbackType
    correction: Optional[Dict[str, Any]] = None
    explanation: str = ""
    impact_score: int = 0  # How significant this feedback is (0-100)
    timestamp: str = ""


class FeedbackEngine:
    """
    Manages feedback collection and learning signals for the Trinity Swarm.

    Responsibilities:
    1. Record all agent decisions with rationale
    2. Capture feedback about those decisions
    3. Identify patterns and edge cases
    4. Generate learning signals for agents
    """

    def __init__(self):
        self.decisions: Dict[str, AgentDecision] = {}
        self.feedback: List[FeedbackRecord] = []
        self.agent_metrics: Dict[str, Dict] = {}
        self.feedback_log_path = "/workspaces/Halilit-Support-Center/backend/logs/feedback"
        os.makedirs(self.feedback_log_path, exist_ok=True)
        self._load_feedback_history()

    def record_decision(
        self,
        agent_name: str,
        decision_type: str,
        input_data: Dict,
        decision_output: Dict,
        confidence: float,
        reasoning: str,
    ) -> str:
        """
        Record a decision made by an agent.
        Returns the decision_id for later feedback reference.
        """
        decision_id = f"{agent_name}_{decision_type}_{datetime.now().isoformat()}"

        decision = AgentDecision(
            decision_id=decision_id,
            agent_name=agent_name,
            decision_type=decision_type,
            input_data=input_data,
            decision_output=decision_output,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat(),
            status="pending_review",
        )

        self.decisions[decision_id] = decision
        self._save_decision(decision)

        logger.info(
            f"📋 Recorded decision: {decision_id} (confidence: {confidence}%)")
        return decision_id

    def submit_feedback(
        self,
        decision_id: str,
        feedback_type: FeedbackType,
        correction: Optional[Dict] = None,
        explanation: str = "",
        impact_score: int = 50,
    ) -> None:
        """
        Submit feedback about a decision the agent made.
        This closes the loop and enables learning.
        """
        if decision_id not in self.decisions:
            logger.warning(f"⚠️ Decision not found: {decision_id}")
            return

        decision = self.decisions[decision_id]
        feedback_id = f"fb_{decision_id}_{datetime.now().isoformat()}"

        feedback = FeedbackRecord(
            feedback_id=feedback_id,
            decision_id=decision_id,
            agent_name=decision.agent_name,
            feedback_type=feedback_type,
            correction=correction,
            explanation=explanation,
            impact_score=impact_score,
            timestamp=datetime.now().isoformat(),
        )

        self.feedback.append(feedback)

        # Update decision status
        if feedback_type == FeedbackType.VALIDATION_PASS:
            decision.status = "approved"
        elif feedback_type in [FeedbackType.CORRECTION, FeedbackType.DECISION_OVERRIDE]:
            decision.status = "rejected"

        self._save_feedback(feedback)
        self._update_agent_metrics(feedback)

        logger.info(
            f"✅ Feedback submitted: {feedback_id} "
            f"({feedback_type.value}, impact: {impact_score})"
        )

    def get_agent_learning_summary(self, agent_name: str) -> Dict:
        """
        Generate a learning summary for an agent to improve its decision-making.
        """
        agent_decisions = [
            d for d in self.decisions.values() if d.agent_name == agent_name]
        agent_feedback = [
            f for f in self.feedback if f.agent_name == agent_name]

        if not agent_decisions:
            return {"agent": agent_name, "summary": "No decisions recorded yet"}

        # Calculate statistics
        total_decisions = len(agent_decisions)
        approved = len([d for d in agent_decisions if d.status == "approved"])
        rejected = len([d for d in agent_decisions if d.status == "rejected"])
        pending = len(
            [d for d in agent_decisions if d.status == "pending_review"])

        accuracy = (approved / total_decisions *
                    100) if total_decisions > 0 else 0

        # Identify common mistakes
        corrections = [
            f for f in agent_feedback if f.feedback_type == FeedbackType.CORRECTION]
        common_errors = {}
        for correction in corrections:
            error_type = correction.explanation.split(
                ":")[0] if correction.explanation else "unknown"
            common_errors[error_type] = common_errors.get(error_type, 0) + 1

        # Identify improving patterns
        high_confidence_correct = len(
            [d for d in agent_decisions if d.confidence >=
                80 and d.status == "approved"]
        )

        return {
            "agent": agent_name,
            "total_decisions": total_decisions,
            "accuracy": round(accuracy, 2),
            "approved": approved,
            "rejected": rejected,
            "pending_review": pending,
            "confidence_score": round(
                sum(d.confidence for d in agent_decisions) / total_decisions, 2
            ),
            "high_confidence_correct": high_confidence_correct,
            "common_errors": common_errors,
            "improvement_areas": self._identify_improvement_areas(agent_name),
            "timestamp": datetime.now().isoformat(),
        }

    def _identify_improvement_areas(self, agent_name: str) -> List[str]:
        """Identify where an agent needs improvement"""
        agent_feedback = [
            f for f in self.feedback if f.agent_name == agent_name]

        areas = []

        # Check for high-impact mistakes
        high_impact_mistakes = [
            f for f in agent_feedback if f.impact_score >= 70]
        if high_impact_mistakes:
            areas.append(
                f"Fix high-impact issues ({len(high_impact_mistakes)} cases)")

        # Check for low confidence on corrections
        agent_decisions = [
            d for d in self.decisions.values() if d.agent_name == agent_name]
        low_conf_rejected = len([
            d for d in agent_decisions
            if d.status == "rejected" and d.confidence < 60
        ])
        if low_conf_rejected > 0:
            areas.append(
                f"Improve confidence calibration ({low_conf_rejected} low-conf rejections)")

        # Check for edge cases
        edge_cases = [
            f for f in agent_feedback if f.feedback_type == FeedbackType.EDGE_CASE]
        if edge_cases:
            areas.append(f"Handle edge cases ({len(edge_cases)} identified)")

        return areas

    def get_pipeline_health_report(self) -> Dict:
        """
        Generate a health report for the entire pipeline.
        Shows which agents are learning well and which need attention.
        """
        agent_names = set(d.agent_name for d in self.decisions.values())

        agent_summaries = {
            agent: self.get_agent_learning_summary(agent)
            for agent in agent_names
        }

        # Pipeline-wide metrics
        total_decisions = len(self.decisions)
        total_feedback = len(self.feedback)
        approved_decisions = len(
            [d for d in self.decisions.values() if d.status == "approved"])

        pipeline_accuracy = (
            (approved_decisions / total_decisions *
             100) if total_decisions > 0 else 0
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "pipeline_accuracy": round(pipeline_accuracy, 2),
            "total_decisions": total_decisions,
            "total_feedback_received": total_feedback,
            "agents": agent_summaries,
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations(agent_summaries),
        }

    def _identify_bottlenecks(self) -> List[str]:
        """Identify where the pipeline is struggling"""
        bottlenecks = []

        # Find agents with low accuracy
        for agent_name in set(d.agent_name for d in self.decisions.values()):
            summary = self.get_agent_learning_summary(agent_name)
            if summary.get("accuracy", 0) < 70:
                bottlenecks.append(
                    f"{agent_name} has low accuracy ({summary['accuracy']}%)"
                )

        return bottlenecks

    def _generate_recommendations(self, agent_summaries: Dict) -> List[str]:
        """Generate actionable recommendations for improvement"""
        recommendations = []

        for agent_name, summary in agent_summaries.items():
            if summary.get("improvement_areas"):
                for area in summary["improvement_areas"]:
                    recommendations.append(f"[{agent_name}] {area}")

        return recommendations

    def get_edge_cases(self, agent_name: Optional[str] = None) -> List[Dict]:
        """
        Retrieve all edge cases encountered.
        Useful for training and identifying blind spots.
        """
        edge_case_feedback = [
            f for f in self.feedback
            if f.feedback_type == FeedbackType.EDGE_CASE
        ]

        if agent_name:
            edge_case_feedback = [
                f for f in edge_case_feedback if f.agent_name == agent_name]

        return [
            {
                "agent": f.agent_name,
                "case": f.explanation,
                "correction": f.correction,
                "timestamp": f.timestamp,
            }
            for f in edge_case_feedback
        ]

    # --- PERSISTENCE ---

    def _save_decision(self, decision: AgentDecision) -> None:
        """Persist decision to disk"""
        filepath = os.path.join(self.feedback_log_path,
                                f"decision_{decision.decision_id}.json")
        with open(filepath, "w") as f:
            json.dump(asdict(decision), f, indent=2)

    def _save_feedback(self, feedback: FeedbackRecord) -> None:
        """Persist feedback to disk"""
        filepath = os.path.join(self.feedback_log_path,
                                f"feedback_{feedback.feedback_id}.json")
        with open(filepath, "w") as f:
            json.dump(asdict(feedback), f, indent=2, default=str)

    def _load_feedback_history(self) -> None:
        """Load historical feedback from disk"""
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
        """Update metrics for the agent based on feedback"""
        agent = feedback.agent_name
        if agent not in self.agent_metrics:
            self.agent_metrics[agent] = {
                "total_feedback": 0,
                "positive": 0,
                "negative": 0,
                "impact_weighted_score": 0,
            }

        self.agent_metrics[agent]["total_feedback"] += 1

        if feedback.feedback_type == FeedbackType.VALIDATION_PASS:
            self.agent_metrics[agent]["positive"] += 1
        elif feedback.feedback_type in [FeedbackType.CORRECTION, FeedbackType.DECISION_OVERRIDE]:
            self.agent_metrics[agent]["negative"] += 1

        self.agent_metrics[agent]["impact_weighted_score"] += feedback.impact_score


# --- GLOBAL FEEDBACK ENGINE ---
feedback_engine = FeedbackEngine()
