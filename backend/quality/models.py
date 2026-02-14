"""
Quality Gate Models — Shared data models for the quality system.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ── Audit System ────────────────────────────────────────────────────────────

class AuditLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditCategory(Enum):
    AGENT_ACTION = "agent_action"
    DATA_VALIDATION = "data_validation"
    SECURITY_CHECK = "security_check"
    VERIFICATION_GATE = "verification_gate"
    APPROVAL_DECISION = "approval_decision"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE = "performance"


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    category: AuditCategory
    level: AuditLevel
    agent_name: Optional[str]
    action: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    execution_time_ms: float
    verification_passed: bool


# ── Gate System ─────────────────────────────────────────────────────────────

class GateStatus(Enum):
    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class GateCheckResult:
    gate_name: str
    status: GateStatus
    checks_passed: int
    checks_total: int
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]

    def is_critical_failure(self) -> bool:
        critical_patterns = ["pii_detected",
                             "malicious_code", "structure_invalid"]
        return any(pattern in v.lower() for v in self.violations
                   for pattern in critical_patterns)


# ── Feedback System ─────────────────────────────────────────────────────────

class FeedbackType(Enum):
    DECISION_OVERRIDE = "override"
    CORRECTION = "correction"
    VALIDATION_PASS = "validation_pass"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    USER_SATISFACTION = "user_satisfaction"
    CONSISTENCY = "consistency"


@dataclass
class AgentDecision:
    decision_id: str
    agent_name: str
    decision_type: str
    input_data: Dict[str, Any]
    decision_output: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: str
    status: str


@dataclass
class FeedbackRecord:
    feedback_id: str
    decision_id: str
    agent_name: str
    feedback_type: FeedbackType
    correction: Optional[Dict[str, Any]] = None
    explanation: str = ""
    impact_score: int = 0
    timestamp: str = ""


# ── Source Tracing ──────────────────────────────────────────────────────────

@dataclass
class SourceReference:
    source_type: str
    source_url: Optional[str] = None
    source_snippet: Optional[str] = None
    extraction_method: str = "scrape"
    timestamp: str = ""
    confidence: float = 1.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.source_snippet and len(self.source_snippet) > 500:
            self.source_snippet = self.source_snippet[:497] + "..."


@dataclass
class VerificationTrace:
    verification_id: str
    product_id: str
    verified_field: str
    verified_value: Any
    sources: List[SourceReference] = None
    verification_timestamp: str = ""
    auditor_agent: str = ""
    is_approved: bool = False
    confidence_score: float = 0.0

    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if not self.verification_timestamp:
            self.verification_timestamp = datetime.now().isoformat()

    def add_source(self, source: SourceReference) -> None:
        self.sources.append(source)

    def source_summary(self) -> Dict[str, Any]:
        return {
            "count": len(self.sources),
            "types": list(set(s.source_type for s in self.sources)),
            "avg_confidence": (
                sum(s.confidence for s in self.sources) / len(self.sources)
                if self.sources else 0
            ),
        }


# ── Agent Memory Models ────────────────────────────────────────────────────

class LearningRecord(BaseModel):
    id: str
    timestamp: str
    agent_name: str
    action_type: str
    input_summary: str
    output_summary: str
    success: bool
    confidence: int
    outcome_quality: Optional[int] = None
    patterns_learned: List[str] = Field(default_factory=list)
    mistakes_avoided: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentInsight(BaseModel):
    pattern: str
    frequency: int
    success_rate: float
    contexts: List[str]
    recommended_approach: str
    anti_patterns: List[str]


class MemoryQuery(BaseModel):
    agent_name: str
    action_type: Optional[str] = None
    context: Optional[str] = None
    limit: int = 10
