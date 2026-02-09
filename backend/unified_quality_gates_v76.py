"""
UNIFIED QUALITY GATES SYSTEM - v7.5
===================================

Consolidates four quality systems into one unified module:
1. Audit System - Operation tracking & compliance logging
2. Security Gates - Multi-stage verification & validation
3. Feedback Engine - Learning signal collection
4. Agent Memory - Long-term learning & improvement

This is the "nervous system" of quality assurance for the Trinity Swarm.
Provides traceability, security, feedback loops, and learning capabilities.
"""

import json
import logging
import os
import re
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
from collections import deque

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Google Genai client for memory operations
try:
    genai_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception:
    genai_client = None

# ============================================================================
# SECTION 0.5: RATE LIMITING & SOURCE TRACEABILITY (NEW v7.6)
# ============================================================================


@dataclass
class SourceReference:
    """Tracks the source of a verification or data enrichment"""
    source_type: str  # "url", "api", "manufacturer_data", "internal_db"
    source_url: Optional[str] = None  # URL if applicable
    # Relevant text/data snippet (max 500 chars)
    source_snippet: Optional[str] = None
    extraction_method: str = "scrape"  # How the data was extracted
    timestamp: str = ""  # When it was extracted
    confidence: float = 1.0  # 0.0-1.0, confidence in this source

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.source_snippet and len(self.source_snippet) > 500:
            self.source_snippet = self.source_snippet[:497] + "..."


@dataclass
class VerificationTrace:
    """Complete traceability for a verification decision"""
    verification_id: str
    product_id: str
    verified_field: str  # E.g., "official_price", "manufacturer_name"
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
        """Register a source for this verification"""
        self.sources.append(source)

    def source_summary(self) -> Dict[str, Any]:
        """Summary of all sources used in this verification"""
        return {
            "total_sources": len(self.sources),
            "primary_source": self.sources[0].source_type if self.sources else None,
            "sources": [
                {
                    "type": s.source_type,
                    "url": s.source_url,
                    "confidence": s.confidence,
                    "timestamp": s.timestamp
                }
                for s in self.sources
            ]
        }


class RateLimiter:
    """
    Production-grade rate limiter for Gemini API calls.

    Implements:
    - Token bucket algorithm for request rate limiting
    - Exponential backoff on API errors
    - Per-agent request tracking
    - Quota monitoring

    Usage:
        limiter = RateLimiter(max_requests_per_minute=60)
        limiter.wait_if_needed('CommercialScout')
        # Make API call
        limiter.record_success('CommercialScout')
        # OR on failure:
        limiter.record_failure('CommercialScout', error_code=429)
    """

    def __init__(self, max_requests_per_minute: int = 60,
                 max_requests_per_day: int = 10000):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: RPM quota (Gemini 2.0 Flash default)
            max_requests_per_day: Daily quota
        """
        self.max_rpm = max_requests_per_minute
        self.max_daily = max_requests_per_day
        self.request_times = deque()  # Track all requests
        self.agent_backoff = {}  # Per-agent backoff timers
        self.agent_request_count = {}  # Per-agent request count
        self.last_reset_time = datetime.now()
        self.lock = threading.Lock()

        logger.info(f"🚦 RateLimiter initialized: {max_requests_per_minute} RPM, "
                    f"{max_requests_per_day} daily")

    def wait_if_needed(self, agent_name: str) -> float:
        """
        Check if we need to wait before making a request.
        Returns the wait time in seconds (0 if no wait needed).

        Implements exponential backoff on consecutive failures.
        """
        with self.lock:
            # Check agent-specific backoff
            if agent_name in self.agent_backoff:
                backoff_until = self.agent_backoff[agent_name]
                wait_time = (backoff_until - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.warning(f"⏱️  [{agent_name}] Backoff active. "
                                   f"Waiting {wait_time:.1f}s")
                    return wait_time
                else:
                    # Backoff expired, remove it
                    del self.agent_backoff[agent_name]

            # Check global rate limit (token bucket)
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)

            # Remove requests older than 1 minute
            while self.request_times and self.request_times[0] < minute_ago:
                self.request_times.popleft()

            # If we're at the limit, calculate wait time
            if len(self.request_times) >= self.max_rpm:
                oldest_request = self.request_times[0]
                reset_time = oldest_request + timedelta(minutes=1)
                wait_seconds = (reset_time - now).total_seconds()

                logger.info(f"🚦 Rate limit reached ({self.max_rpm} RPM). "
                            f"Waiting {wait_seconds:.1f}s")
                return wait_seconds

            return 0.0

    def record_request(self, agent_name: str) -> None:
        """Record that a request was made"""
        with self.lock:
            self.request_times.append(datetime.now())
            self.agent_request_count[agent_name] = \
                self.agent_request_count.get(agent_name, 0) + 1

    def record_success(self, agent_name: str) -> None:
        """Record successful API call. Resets backoff timer."""
        with self.lock:
            # Clear backoff on success
            if agent_name in self.agent_backoff:
                del self.agent_backoff[agent_name]
                logger.info(f"✅ [{agent_name}] Backoff cleared (success)")

    def record_failure(self, agent_name: str, error_code: Optional[int] = None,
                       retry_after: Optional[float] = None) -> None:
        """
        Record API failure and apply exponential backoff.

        Args:
            agent_name: Which agent failed
            error_code: HTTP error code (429 = rate limit, 503 = service unavailable)
            retry_after: Server-suggested retry delay (seconds)
        """
        with self.lock:
            # Get current backoff level
            current_backoff = self.agent_backoff.get(agent_name)

            if current_backoff:
                # Already backing off, increase delay
                backoff_seconds = min(
                    300, (current_backoff - datetime.now()).total_seconds() * 2)
            else:
                # First failure
                if error_code == 429:
                    # Rate limit hit - use server's retry_after or default to 60s
                    backoff_seconds = retry_after or 60.0
                elif error_code == 503:
                    # Service unavailable - exponential backoff
                    backoff_seconds = retry_after or 30.0
                else:
                    # Generic error - short backoff
                    backoff_seconds = 5.0

            # Cap backoff at 5 minutes
            backoff_seconds = min(300, backoff_seconds)
            backoff_until = datetime.now() + timedelta(seconds=backoff_seconds)
            self.agent_backoff[agent_name] = backoff_until

            logger.warning(f"⚠️  [{agent_name}] API failure (code {error_code}). "
                           f"Backoff: {backoff_seconds:.1f}s")

    def get_status(self) -> Dict[str, Any]:
        """Get current limiter status"""
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            requests_in_window = len(
                [t for t in self.request_times if t > minute_ago])

            return {
                "current_rpm": requests_in_window,
                "max_rpm": self.max_rpm,
                "capacity_remaining": max(0, self.max_rpm - requests_in_window),
                "agents_with_backoff": list(self.agent_backoff.keys()),
                "agent_request_counts": dict(self.agent_request_count),
                "timestamp": now.isoformat()
            }


class SourceTracedVerification:
    """
    Enhanced verification that tracks sources for all data points.

    Replaces basic verification with auditable, traceable verification.
    """

    def __init__(self, log_dir: str = "/workspaces/Halilit-Support-Center/backend/logs/verification"):
        self.log_dir = log_dir
        self.traces: Dict[str, VerificationTrace] = {}
        os.makedirs(log_dir, exist_ok=True)
        self.traces_file = os.path.join(log_dir, "verification_traces.jsonl")

    def verify_with_source(self, product_id: str, field: str, value: Any,
                           source: SourceReference, agent_name: str = "",
                           confidence: float = 1.0) -> VerificationTrace:
        """
        Record a verification with full source traceability.

        Args:
            product_id: Which product is being verified
            field: Which field (e.g., "official_price")
            value: The verified value
            source: SourceReference with URL, snippet, etc.
            agent_name: Which agent performed verification
            confidence: 0.0-1.0 confidence in this verification

        Returns:
            VerificationTrace with full audit trail
        """
        trace_id = f"trace_{product_id}_{field}_{datetime.now().isoformat()}"

        trace = VerificationTrace(
            verification_id=trace_id,
            product_id=product_id,
            verified_field=field,
            verified_value=value,
            auditor_agent=agent_name,
            confidence_score=confidence,
            is_approved=True  # Default to approved
        )

        trace.add_source(source)
        self.traces[trace_id] = trace
        self._save_trace(trace)

        logger.info(f"📋 Verification traced: {product_id}.{field} "
                    f"from {source.source_type}")

        return trace

    def add_verification_source(self, trace_id: str, source: SourceReference) -> None:
        """Add an additional source to an existing verification"""
        if trace_id in self.traces:
            self.traces[trace_id].add_source(source)
            self._save_trace(self.traces[trace_id])
            logger.info(f"📋 Added source to {trace_id}: {source.source_type}")

    def get_verification_audit(self, product_id: str) -> Dict[str, Any]:
        """Get complete audit trail for a product's verifications"""
        product_traces = [t for t in self.traces.values()
                          if t.product_id == product_id]

        return {
            "product_id": product_id,
            "total_verifications": len(product_traces),
            "verified_fields": [t.verified_field for t in product_traces],
            "verifications": [
                {
                    "field": t.verified_field,
                    "value": str(t.verified_value)[:100],
                    "confidence": t.confidence_score,
                    "auditor": t.auditor_agent,
                    "sources": t.source_summary()
                }
                for t in product_traces
            ],
            "audit_timestamp": datetime.now().isoformat()
        }

    def _save_trace(self, trace: VerificationTrace) -> None:
        """Persist verification trace to disk"""
        trace_dict = asdict(trace)
        trace_dict['sources'] = [asdict(s) for s in trace.sources]
        with open(self.traces_file, 'a') as f:
            f.write(json.dumps(trace_dict, default=str) + '\n')

# ============================================================================
# SECTION 1: ENUMS & DATA MODELS
# ============================================================================

# --- Audit System Enums ---


class AuditLevel(Enum):
    """Severity/importance levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditCategory(Enum):
    """Categories of auditable events"""
    AGENT_ACTION = "agent_action"
    DATA_VALIDATION = "data_validation"
    SECURITY_CHECK = "security_check"
    VERIFICATION_GATE = "verification_gate"
    APPROVAL_DECISION = "approval_decision"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE = "performance"


@dataclass
class AuditEvent:
    """A single auditable event in the system"""
    event_id: str
    timestamp: str
    category: AuditCategory
    level: AuditLevel
    agent_name: Optional[str]
    action: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    status: str  # "success", "failure", "partial"
    error_message: Optional[str]
    execution_time_ms: float
    verification_passed: bool


# --- Security Gates Enums ---

class GateStatus(Enum):
    """Gate check result"""
    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class GateCheckResult:
    """Result of a gate verification"""
    gate_name: str
    status: GateStatus
    checks_passed: int
    checks_total: int
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]

    def is_critical_failure(self) -> bool:
        """Check if any critical violations detected"""
        critical_patterns = ["pii_detected",
                             "malicious_code", "structure_invalid"]
        return any(pattern in v.lower() for v in self.violations)


# --- Feedback Engine Enums & Models ---

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


# --- Agent Memory Models ---

class LearningRecord(BaseModel):
    """Single learning instance from an agent action"""
    id: str
    timestamp: str
    agent_name: str
    action_type: str  # analyze|fix|validate|improve|scan
    input_summary: str
    output_summary: str
    success: bool
    confidence: int
    outcome_quality: Optional[int] = None  # 0-100, validated later
    patterns_learned: List[str] = Field(default_factory=list)
    mistakes_avoided: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentInsight(BaseModel):
    """Distilled insight from multiple learning records"""
    pattern: str
    frequency: int
    success_rate: float
    contexts: List[str]
    recommended_approach: str
    anti_patterns: List[str]


class MemoryQuery(BaseModel):
    """Query to retrieve relevant past learning"""
    agent_name: str
    action_type: Optional[str] = None
    context: Optional[str] = None
    limit: int = 10


# ============================================================================
# SECTION 2: AUDIT LOGGER
# ============================================================================

class AuditLogger:
    """
    Comprehensive audit logging system for all pipeline operations.

    Features:
    - Complete operation traceability
    - Security event logging
    - Performance metrics
    - Error tracking with resolution status
    """

    def __init__(self, log_dir: str = "/workspaces/Halilit-Support-Center/backend/logs/audit"):
        self.log_dir = log_dir
        self.events: List[AuditEvent] = []
        self.event_index: Dict[str, AuditEvent] = {}
        os.makedirs(log_dir, exist_ok=True)

        # Setup file logging FIRST (before loading historical events)
        self.log_file = os.path.join(
            log_dir, f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.json_log_file = os.path.join(log_dir, "events.jsonl")

        # Now load historical events
        self._load_historical_events()

    def log_event(
        self,
        category: AuditCategory,
        level: AuditLevel,
        action: str,
        agent_name: Optional[str] = None,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        execution_time_ms: float = 0.0,
        verification_passed: bool = True,
    ) -> str:
        """Log a single audit event"""
        event_id = f"{category.value}_{datetime.now().isoformat()}"

        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            category=category,
            level=level,
            agent_name=agent_name,
            action=action,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            verification_passed=verification_passed,
        )

        self.events.append(event)
        self.event_index[event_id] = event
        self._save_event(event)

        # Log to standard logging
        log_msg = f"[{category.value.upper()}] {action} - Status: {status}"
        if agent_name:
            log_msg += f" (Agent: {agent_name})"

        if level == AuditLevel.CRITICAL or level == AuditLevel.SECURITY:
            logger.critical(log_msg)
        elif level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif level == AuditLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return event_id

    def log_agent_action(
        self,
        agent_name: str,
        action: str,
        input_data: Dict,
        output_data: Dict,
        success: bool = True,
        execution_time_ms: float = 0.0,
    ) -> str:
        """Convenience method: Log an agent's action"""
        return self.log_event(
            category=AuditCategory.AGENT_ACTION,
            level=AuditLevel.INFO if success else AuditLevel.WARNING,
            action=action,
            agent_name=agent_name,
            input_data=input_data,
            output_data=output_data,
            status="success" if success else "failure",
            execution_time_ms=execution_time_ms,
        )

    def log_verification(
        self,
        agent_name: str,
        item_type: str,
        item_id: str,
        passed: bool,
        violations: Optional[List[str]] = None,
        risk_score: int = 0,
    ) -> str:
        """Log a verification/validation gate result"""
        return self.log_event(
            category=AuditCategory.VERIFICATION_GATE,
            level=AuditLevel.WARNING if not passed else AuditLevel.INFO,
            action=f"Verified {item_type}: {item_id}",
            agent_name=agent_name,
            input_data={"item_type": item_type, "item_id": item_id},
            output_data={
                "passed": passed,
                "violations": violations or [],
                "risk_score": risk_score,
            },
            status="success" if passed else "failure",
            verification_passed=passed,
        )

    def log_security_event(
        self,
        event_type: str,
        description: str,
        threat_level: str = "medium",  # low, medium, high, critical
        details: Optional[Dict] = None,
    ) -> str:
        """Log security-relevant events"""
        level_map = {
            "low": AuditLevel.WARNING,
            "medium": AuditLevel.WARNING,
            "high": AuditLevel.CRITICAL,
            "critical": AuditLevel.CRITICAL,
        }

        return self.log_event(
            category=AuditCategory.SECURITY_CHECK,
            level=level_map.get(threat_level, AuditLevel.WARNING),
            action=f"Security: {event_type}",
            output_data={"threat_level": threat_level,
                         "details": details, "description": description},
            status="flagged",
        )

    def log_approval_decision(
        self,
        agent_name: str,
        decision_type: str,
        item_id: str,
        approved: bool,
        confidence: float,
        rationale: str,
    ) -> str:
        """Log approval/rejection decisions"""
        return self.log_event(
            category=AuditCategory.APPROVAL_DECISION,
            level=AuditLevel.INFO,
            action=f"{agent_name} {'APPROVED' if approved else 'REJECTED'}: {decision_type}",
            agent_name=agent_name,
            input_data={"item_id": item_id, "decision_type": decision_type},
            output_data={
                "approved": approved,
                "confidence": confidence,
                "rationale": rationale,
            },
            status="success",
        )

    def log_error_recovery(
        self,
        agent_name: str,
        error_type: str,
        original_error: str,
        recovery_action: str,
        recovery_successful: bool,
    ) -> str:
        """Log error recovery attempts"""
        return self.log_event(
            category=AuditCategory.ERROR_RECOVERY,
            level=AuditLevel.WARNING if recovery_successful else AuditLevel.ERROR,
            action=f"Error recovery attempt: {error_type}",
            agent_name=agent_name,
            input_data={"error_type": error_type,
                        "original_error": original_error},
            output_data={
                "recovery_action": recovery_action,
                "recovered": recovery_successful,
            },
            status="success" if recovery_successful else "failure",
        )

    def audit_flow(self, category: AuditCategory, agent_name: Optional[str] = None):
        """
        Decorator to automatically audit function calls.

        Usage:
            @audit_logger.audit_flow(AuditCategory.AGENT_ACTION, agent_name="CommercialScout")
            def my_function():
                pass
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                start = time.time()

                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start) * 1000

                    self.log_event(
                        category=category,
                        level=AuditLevel.INFO,
                        action=f"Executed {func.__name__}",
                        agent_name=agent_name,
                        output_data={"result_type": type(result).__name__},
                        execution_time_ms=duration_ms,
                        status="success",
                    )
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start) * 1000
                    self.log_event(
                        category=category,
                        level=AuditLevel.ERROR,
                        action=f"Failed: {func.__name__}",
                        agent_name=agent_name,
                        error_message=str(e),
                        execution_time_ms=duration_ms,
                        status="failure",
                    )
                    raise
            return wrapper
        return decorator

    def get_audit_trail(
        self,
        agent_name: Optional[str] = None,
        category: Optional[AuditCategory] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Retrieve audit trail filtered by criteria"""
        events = self.events

        if agent_name:
            events = [e for e in events if e.agent_name == agent_name]

        if category:
            events = [e for e in events if e.category == category]

        # Return most recent first
        return [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp,
                "category": e.category.value,
                "level": e.level.value,
                "agent": e.agent_name,
                "action": e.action,
                "status": e.status,
                "execution_time_ms": e.execution_time_ms,
            }
            for e in sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]
        ]

    def get_security_audit(self) -> Dict:
        """Get comprehensive security audit"""
        security_events = [
            e for e in self.events if e.category == AuditCategory.SECURITY_CHECK]

        critical = len(
            [e for e in security_events if e.level == AuditLevel.CRITICAL])
        high = len([e for e in security_events if e.level in [
                   AuditLevel.ERROR, AuditLevel.CRITICAL]])

        return {
            "timestamp": datetime.now().isoformat(),
            "total_security_events": len(security_events),
            "critical_events": critical,
            "high_severity_events": high,
            "recent_events": self.get_audit_trail(category=AuditCategory.SECURITY_CHECK, limit=20),
        }

    def get_performance_report(self) -> Dict:
        """Get performance metrics from audit log"""
        agent_names = set(e.agent_name for e in self.events if e.agent_name)

        performance = {}
        for agent in agent_names:
            agent_events = [e for e in self.events if e.agent_name == agent]
            successful = len(
                [e for e in agent_events if e.status == "success"])
            failed = len([e for e in agent_events if e.status == "failure"])
            total_time_ms = sum(e.execution_time_ms for e in agent_events)
            avg_time_ms = total_time_ms / \
                len(agent_events) if agent_events else 0

            performance[agent] = {
                "total_actions": len(agent_events),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(agent_events) * 100) if agent_events else 0, 2),
                "avg_execution_time_ms": round(avg_time_ms, 2),
                "total_execution_time_ms": round(total_time_ms, 2),
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "by_agent": performance,
        }

    def _save_event(self, event: AuditEvent) -> None:
        """Save event to disk in JSONL format"""
        with open(self.json_log_file, "a") as f:
            f.write(json.dumps(asdict(event), default=str) + "\n")

    def _load_historical_events(self) -> None:
        """Load historical events from disk"""
        if not os.path.exists(self.json_log_file):
            return

        try:
            with open(self.json_log_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # Convert category and level back to enums
                        data["category"] = AuditCategory[data["category"].upper().replace(
                            "_", "_")]
                        data["level"] = AuditLevel[data["level"].upper()]
                        event = AuditEvent(**data)
                        self.events.append(event)
                        self.event_index[event.event_id] = event
                    except Exception as e:
                        logger.warning(f"Failed to parse audit event: {e}")
        except FileNotFoundError:
            pass


# ============================================================================
# SECTION 3: SECURITY GATES
# ============================================================================

class InputValidationGate:
    """
    Sanitizes and validates inputs before processing.
    Prevents bad data from entering the pipeline.
    """

    @staticmethod
    def validate_product(product: Dict[str, Any]) -> GateCheckResult:
        """Validate product structure and basic sanity."""
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 6

        # Check 1: Is dict
        if not isinstance(product, dict):
            violations.append(
                f"Product is not a dictionary (got {type(product).__name__})")
        else:
            checks_passed += 1

        # Check 2: Has required fields
        required_fields = ['product_name', 'brand', 'price_il', 'halilit_id']
        for field in required_fields:
            if field not in product or not product[field]:
                violations.append(f"Missing required field: {field}")
            else:
                checks_passed += 1

        # Check 3: Price is valid
        try:
            price = float(product.get('price_il', 0))
            if price < 0:
                violations.append("Price is negative")
            elif price == 0:
                warnings.append("Price is zero (might be TBD)")
            else:
                checks_passed += 1
        except (ValueError, TypeError):
            violations.append(
                f"Price is not a number (got {type(product.get('price_il')).__name__})")

        # Check 4: Product name is reasonable length
        name = product.get('product_name', '')
        if len(name) < 3:
            violations.append("Product name too short (< 3 chars)")
        elif len(name) > 500:
            violations.append("Product name too long (> 500 chars)")
        else:
            checks_passed += 1

        return GateCheckResult(
            gate_name="InputValidation",
            status=GateStatus.BLOCKED if violations else GateStatus.PASSED,
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Add missing fields",
                             "Verify price information"] if violations else [],
        )


class SecurityGate:
    """
    Checks for security threats:
    - Personal Identifiable Information (PII)
    - Malicious code/markup
    - Suspicious patterns
    - Data integrity
    """

    # PII patterns to detect
    PII_PATTERNS = {
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ip_address": r"\b(?:192\.168|10\.|172\.1[6-9]|172\.2[0-9]|172\.3[01])\.\d{1,3}\.\d{1,3}\b",
        "internal_id": r"(?i)(internal_id|ref_id|employee_id|account_\w+)[:=\s]+[\w\d-]+",
    }

    # Malicious code patterns
    MALICIOUS_PATTERNS = {
        "script": r"<script[^>]*>.*?</script>",
        "javascript": r"javascript:",
        "onclick": r"on\w+\s*=",
        "sql_injection": r"(union|select|insert|delete|drop)[\s\n]+(from|into|where|table)",
        "xss": r"<(iframe|object|embed|img)[^>]*on\w+",
    }

    @staticmethod
    def check_pii(text: str) -> Tuple[bool, List[str]]:
        """Scan text for PII. Returns (has_pii, detected_patterns)"""
        if not isinstance(text, str):
            return False, []

        detected = []
        for pattern_name, pattern in SecurityGate.PII_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"PII_detected: {pattern_name}")

        return len(detected) > 0, detected

    @staticmethod
    def check_malicious(text: str) -> Tuple[bool, List[str]]:
        """Scan for malicious code patterns. Returns (is_malicious, detected_patterns)"""
        if not isinstance(text, str):
            return False, []

        detected = []
        for pattern_name, pattern in SecurityGate.MALICIOUS_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                detected.append(f"malicious_{pattern_name}")

        return len(detected) > 0, detected

    @staticmethod
    def check_product_security(product: Dict[str, Any]) -> GateCheckResult:
        """Full security check on a product."""
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 5

        # Convert entire product to string for scanning
        product_text = str(product).lower()

        # Check 1: No PII
        has_pii, pii_patterns = SecurityGate.check_pii(product_text)
        if has_pii:
            violations.append(f"PII detected: {', '.join(pii_patterns)}")
        else:
            checks_passed += 1

        # Check 2: No malicious code
        is_malicious, mal_patterns = SecurityGate.check_malicious(product_text)
        if is_malicious:
            violations.append(
                f"Malicious code detected: {', '.join(mal_patterns)}")
        else:
            checks_passed += 1

        # Check 3: No obvious credential exposure
        if re.search(r"(?i)(password|api_?key|secret|token)[\s:=]+\S+", product_text):
            violations.append("Potential credential exposure detected")
        else:
            checks_passed += 1

        # Check 4: Brand is reasonable
        brand = product.get('brand', '')
        if not brand or len(brand) < 2 or len(brand) > 100:
            warnings.append("Brand name suspicious or missing")
        else:
            checks_passed += 1

        # Check 5: Price is reasonable (not obviously fake)
        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 10 or price > 1000000:
                warnings.append(
                    "Price seems unrealistic (very low or very high)")
            else:
                checks_passed += 1

        return GateCheckResult(
            gate_name="Security",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Remove PII before storage", "Verify brand legitimacy",
                             "Check price reasonableness"] if violations else [],
        )


class DataIntegrityGate:
    """
    Verifies data structure and completeness.
    Ensures data can be properly stored and served.
    """

    @staticmethod
    def check_integrity(product: Dict[str, Any], required_fields: List[str] = None) -> GateCheckResult:
        """Check data integrity and structure."""
        if required_fields is None:
            required_fields = {
                'product_name', 'brand', 'price_il', 'halilit_id',
                'display', 'pricing', 'taxonomy'
            }

        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 6

        # Check 1: Essential fields present
        missing = [f for f in required_fields if f not in product]
        if missing:
            violations.append(f"Missing fields: {', '.join(missing)}")
        else:
            checks_passed += 1

        # Check 2: Images accessible
        images = product.get('official_images', [])
        if isinstance(images, list):
            if len(images) == 0:
                warnings.append("No official images available")
            else:
                checks_passed += 1
        else:
            violations.append(
                f"Images field is not a list (got {type(images).__name__})")

        # Check 3: Taxonomy valid
        taxonomy = product.get('taxonomy') or {}
        if isinstance(taxonomy, dict):
            required_taxonomy = ['canonical_category', 'canonical_subcategory']
            # Only strictly require these if taxonomy is NOT empty
            if taxonomy:
                missing_tax = [
                    f for f in required_taxonomy if f not in taxonomy]
                if missing_tax:
                    warnings.append(
                        f"Missing taxonomy fields: {', '.join(missing_tax)}")
                else:
                    checks_passed += 1
            else:
                # Taxonomy is empty/None but was a dict or None
                # If it's the raw draft, this is expected in early phases.
                # If it's final, this is a warning.
                # We count it as passed check (structure ok) but maybe warn if we are strict.
                checks_passed += 1
        else:
            violations.append(
                f"Taxonomy is not a dict (got {type(taxonomy).__name__})")

        # Check 4: Display data valid
        display = product.get('display', {})
        if isinstance(display, dict):
            checks_passed += 1
        else:
            violations.append(
                f"Display is not a dict (got {type(display).__name__})")

        # Check 5: Pricing valid
        pricing = product.get('pricing', {})
        if isinstance(pricing, dict):
            if 'price_il' not in pricing:
                warnings.append("Pricing missing price_il field")
            else:
                checks_passed += 1
        else:
            violations.append(
                f"Pricing is not a dict (got {type(pricing).__name__})")

        # Check 6: Data consistency
        name1 = product.get('product_name', '')
        name2 = product.get('display', {}).get('display_name', '')
        if name1 and name2 and name1.lower() == name2.lower():
            checks_passed += 1
        elif name1:
            checks_passed += 1

        return GateCheckResult(
            gate_name="DataIntegrity",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Normalize data structure",
                             "Add missing fields"] if violations else [],
        )


class ComplianceGate:
    """Checks compliance with business rules and policies."""

    @staticmethod
    def check_compliance(product: Dict[str, Any]) -> GateCheckResult:
        """Check business rule compliance."""
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 4

        # Check 1: Price in valid range (for Israel market)
        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 50:  # Minimum reasonable price
                violations.append("Price below acceptable minimum (< 50 NIS)")
            elif price > 500000:  # Maximum reasonable price
                violations.append(
                    "Price exceeds acceptable maximum (> 500,000 NIS)")
            else:
                checks_passed += 1

        # Check 2: Brand validation
        brand = product.get('brand', '').lower()
        known_brands = ['roland', 'nord', 'yamaha', 'boss',
                        'korg', 'universal audio', 'rode', 'shure']
        if brand in known_brands or len(brand) > 2:
            checks_passed += 1
        else:
            warnings.append("Brand not in known list or too short")

        # Check 3: Category consistency
        category = product.get('taxonomy', {}).get('canonical_category', '')
        valid_categories = [
            'Amplifiers & Effects', 'Audio Interfaces & Mixers',
            'Drums & Percussion', 'Headphones & Earphones',
            'Keyboards & Synthesizers', 'Microphones & Recording',
            'Studio Monitors & Speakers', 'Other'
        ]
        if category in valid_categories:
            checks_passed += 1
        else:
            warnings.append(f"Category '{category}' not in approved list")

        # Check 4: Minimum data quality
        name = product.get('product_name', '')
        has_images = len(product.get('official_images', [])) > 0
        has_specs = bool(product.get('official_specs'))
        quality_score = sum([bool(name), has_images, has_specs]) / 3

        if quality_score >= 0.6:
            checks_passed += 1
        else:
            warnings.append(f"Data quality too low ({quality_score*100:.0f}%)")

        return GateCheckResult(
            gate_name="Compliance",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=[
                "Verify prices", "Validate category assignment"] if violations else [],
        )


class QualityGate:
    """Verifies product meets quality standards."""

    @staticmethod
    def check_quality(product: Dict[str, Any], target_score: float = 80.0) -> GateCheckResult:
        """Check if product meets quality threshold."""
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 3

        # Import here to avoid circular imports
        from backend.agents.perfection_map import PerfectionMap

        # Check 1: Completeness
        completeness = PerfectionMap.calculate_completeness_score(product)
        if completeness >= target_score:
            checks_passed += 1
        else:
            warnings.append(
                f"Completeness score too low ({completeness:.0f}% < {target_score}%)")

        # Check 2: Security
        security = PerfectionMap.calculate_security_score(product)
        if security >= 90.0:
            checks_passed += 1
        else:
            violations.append(
                f"Security score too low ({security:.0f}% < 90%)")

        # Check 3: Overall tier
        tier = PerfectionMap.get_quality_tier(completeness)
        if tier in ['GOLD', 'SILVER']:
            checks_passed += 1
        else:
            warnings.append(
                f"Product is tier '{tier}' (target: GOLD or SILVER)")

        return GateCheckResult(
            gate_name="Quality",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Improve data completeness",
                             "Add official images/specs"] if violations else [],
        )


class ContentQualityGate:
    """
    Ensures content quality:
    - No placeholder text (lorem ipsum, TBD)
    - No empty or null string values where clear text is expected
    - No excessive repetition
    """

    PLACEHOLDERS = [
        "lorem ipsum", "tbd", "pending", "coming soon",
        "no description", "n/a", "undefined", "null", "[insert"
    ]

    @staticmethod
    def check_content(product: Dict[str, Any]) -> GateCheckResult:
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 4

        # Helper to check text quality
        def is_placeholder(text: str) -> bool:
            if not text:
                return False
            t = text.lower()
            return any(p in t for p in ContentQualityGate.PLACEHOLDERS)

        # Check 1: Product Name Quality
        name = product.get('product_name', '')
        if is_placeholder(name):
            violations.append(
                f"Product name contains placeholder text: {name}")
        elif name.lower() in ["unknown", "product", "test"]:
            violations.append(f"Product name is generic: {name}")
        else:
            checks_passed += 1

        # Check 2: Description Quality (if present)
        desc = product.get('description_long') or product.get(
            'description_short') or ""
        if desc and is_placeholder(desc):
            violations.append("Description contains placeholder text")
        else:
            checks_passed += 1

        # Check 3: Repetition (Name == Description)
        if desc and name and desc.lower().strip() == name.lower().strip():
            warnings.append("Description is identical to product name")
        else:
            checks_passed += 1

        # Check 4: Empty "Official" fields
        # If we have official specs but they are empty dict, warn
        if 'official_specs' in product and isinstance(product['official_specs'], dict) and not product['official_specs']:
            warnings.append("Official specs present but empty")
        else:
            checks_passed += 1

        return GateCheckResult(
            gate_name="ContentQuality",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Remove placeholder text", "Enrich description",
                             "Populate official specs"] if violations else [],
        )


class GateProcessor:
    """
    Runs all gates against a product.
    Provides comprehensive security and quality verification.
    """

    @staticmethod
    def process_all_gates(product: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
        """Run all gates and return comprehensive report."""
        results = {
            "product_id": product.get('halilit_id', 'unknown'),
            "timestamp": None,
            "overall_status": GateStatus.PASSED,
            "gates": {},
        }

        # Run all gates
        gates = [
            InputValidationGate.validate_product(product),
            SecurityGate.check_product_security(product),
            DataIntegrityGate.check_integrity(product),
            ComplianceGate.check_compliance(product),
            QualityGate.check_quality(product),
            ContentQualityGate.check_content(
                product),  # Added ContentQualityGate
        ]

        total_violations = 0
        total_warnings = 0

        for gate_result in gates:
            results["gates"][gate_result.gate_name] = {
                "status": gate_result.status.value,
                "checks_passed": gate_result.checks_passed,
                "checks_total": gate_result.checks_total,
                "violations": gate_result.violations,
                "warnings": gate_result.warnings,
                "recommendations": gate_result.recommendations,
            }

            # Update overall status
            if gate_result.status == GateStatus.BLOCKED:
                results["overall_status"] = GateStatus.BLOCKED
                total_violations += len(gate_result.violations)
            elif gate_result.status == GateStatus.WARNING and strict_mode:
                results["overall_status"] = GateStatus.WARNING
                total_warnings += len(gate_result.warnings)
            elif gate_result.status == GateStatus.WARNING and results["overall_status"] == GateStatus.PASSED:
                results["overall_status"] = GateStatus.WARNING
                total_warnings += len(gate_result.warnings)

        results["total_violations"] = total_violations
        results["total_warnings"] = total_warnings
        results["passed_all_gates"] = results["overall_status"] == GateStatus.PASSED

        logger.info(
            f"[GateProcessor] {product.get('product_name')}: Status={results['overall_status'].value}, "
            f"Violations={total_violations}, Warnings={total_warnings}"
        )

        return results


# ============================================================================
# SECTION 4: FEEDBACK ENGINE
# ============================================================================

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
        """Record a decision made by an agent. Returns the decision_id for later feedback reference."""
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
        """Submit feedback about a decision the agent made. This closes the loop and enables learning."""
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
            f"✅ Feedback submitted: {feedback_id} ({feedback_type.value}, impact: {impact_score})")

    def get_agent_learning_summary(self, agent_name: str) -> Dict:
        """Generate a learning summary for an agent to improve its decision-making."""
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
            "confidence_score": round(sum(d.confidence for d in agent_decisions) / total_decisions, 2),
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
        """Generate a health report for the entire pipeline."""
        agent_names = set(d.agent_name for d in self.decisions.values())

        agent_summaries = {agent: self.get_agent_learning_summary(
            agent) for agent in agent_names}

        # Pipeline-wide metrics
        total_decisions = len(self.decisions)
        total_feedback = len(self.feedback)
        approved_decisions = len(
            [d for d in self.decisions.values() if d.status == "approved"])

        pipeline_accuracy = (
            approved_decisions / total_decisions * 100) if total_decisions > 0 else 0

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

        for agent_name in set(d.agent_name for d in self.decisions.values()):
            summary = self.get_agent_learning_summary(agent_name)
            if summary.get("accuracy", 0) < 70:
                bottlenecks.append(
                    f"{agent_name} has low accuracy ({summary['accuracy']}%)")

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
        """Retrieve all edge cases encountered."""
        edge_case_feedback = [
            f for f in self.feedback if f.feedback_type == FeedbackType.EDGE_CASE]

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


# ============================================================================
# SECTION 5: AGENT MEMORY SYSTEM
# ============================================================================

class AgentMemory:
    """Functional memory system for agent learning and improvement"""

    def __init__(self, memory_dir: str = ".agent_memory"):
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, "learning_history.jsonl")
        self.insights_file = os.path.join(memory_dir, "insights.json")
        self.client = genai_client

        # Ensure directory exists
        os.makedirs(memory_dir, exist_ok=True)

        # Initialize insights cache
        self.insights_cache: Dict[str, List[AgentInsight]] = {}
        self._load_insights()

    def _load_insights(self):
        """Load existing insights from disk"""
        if os.path.exists(self.insights_file):
            with open(self.insights_file, 'r') as f:
                data = json.load(f)
                for agent, insights in data.items():
                    self.insights_cache[agent] = [
                        AgentInsight(**i) for i in insights]

    def _save_insights(self):
        """Save insights to disk"""
        data = {
            agent: [i.model_dump() for i in insights]
            for agent, insights in self.insights_cache.items()
        }
        with open(self.insights_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_action(self, record: LearningRecord) -> None:
        """Record an agent action for learning"""
        with open(self.memory_file, 'a') as f:
            f.write(record.model_dump_json() + '\n')

        print(
            f"📚 [Memory] Recorded {record.agent_name} action: {record.action_type}")

    def recall_relevant(self, query: MemoryQuery) -> List[LearningRecord]:
        """Retrieve relevant past learning records"""
        if not os.path.exists(self.memory_file):
            return []

        records = []
        with open(self.memory_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = LearningRecord(**json.loads(line))

                    # Filter by agent and action type
                    if record.agent_name == query.agent_name:
                        if query.action_type is None or record.action_type == query.action_type:
                            records.append(record)

        # Return most recent
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:query.limit]

    def analyze_patterns(self, agent_name: str, min_frequency: int = 3) -> List[AgentInsight]:
        """Analyze learning records to extract patterns using AI"""
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=100))

        if len(records) < 3 or not self.client:
            return []

        # Prepare data for AI analysis
        records_summary = []
        for r in records:
            records_summary.append({
                "action": r.action_type,
                "success": r.success,
                "confidence": r.confidence,
                "input": r.input_summary[:200],
                "output": r.output_summary[:200],
                "patterns": r.patterns_learned
            })

        # Use AI to extract insights
        prompt = f"""Analyze these {len(records)} agent actions and extract patterns:

{json.dumps(records_summary, indent=2)}

Identify:
1. Common successful patterns (things that work well)
2. Anti-patterns (approaches that fail)
3. Context-specific recommendations
4. Areas for improvement

Return JSON array of insights with this structure:
[
  {{
    "pattern": "Descriptive pattern name",
    "frequency": number_of_occurrences,
    "success_rate": 0.0_to_1.0,
    "contexts": ["context1", "context2"],
    "recommended_approach": "What to do",
    "anti_patterns": ["What to avoid"]
  }}
]

Focus on patterns that appear at least {min_frequency} times."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Parse AI response
            insights_data = json.loads(response.text.strip())
            insights = [AgentInsight(**i) for i in insights_data]

            # Cache insights
            self.insights_cache[agent_name] = insights
            self._save_insights()

            print(
                f"🧠 [Memory] Extracted {len(insights)} patterns for {agent_name}")
            return insights

        except Exception as e:
            print(f"⚠️ [Memory] Pattern analysis failed: {e}")
            return []

    def get_contextual_advice(self, agent_name: str, current_task: str) -> str:
        """Get AI-powered advice based on past learning"""
        # Get recent records
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=20))

        # Get insights
        insights = self.insights_cache.get(agent_name, [])

        if not records and not insights:
            return "No prior learning available. Proceed with best judgment."

        if not self.client:
            return "AI client not available. Use cached insights."

        # Build context for AI
        context_data = {
            "recent_successes": [r.output_summary for r in records if r.success][:5],
            "recent_failures": [r.output_summary for r in records if not r.success][:3],
            "learned_patterns": [i.pattern for i in insights][:5],
            "anti_patterns": [ap for i in insights for ap in i.anti_patterns][:5]
        }

        prompt = f"""Based on this agent's learning history, provide advice for the current task.

Agent: {agent_name}
Current Task: {current_task}

Learning Context:
{json.dumps(context_data, indent=2)}

Provide specific, actionable advice in 2-3 sentences that:
1. References successful past patterns
2. Warns against known mistakes
3. Suggests optimal approach for this task"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            advice = response.text.strip()
            print(f"💡 [Memory] Generated contextual advice for {agent_name}")
            return advice

        except Exception as e:
            print(f"⚠️ [Memory] Advice generation failed: {e}")
            return "Proceed with caution. No specific advice available."

    def suggest_improvements(self, agent_name: str) -> List[str]:
        """Suggest improvements based on learning patterns"""
        insights = self.insights_cache.get(agent_name, [])

        if not insights:
            # Trigger pattern analysis
            insights = self.analyze_patterns(agent_name)

        if not insights:
            return ["Continue gathering learning data for meaningful insights"]

        # Find patterns with low success rate
        improvements = []
        for insight in insights:
            if insight.success_rate < 0.8:
                improvements.append(
                    f"Improve {insight.pattern} (current success: {insight.success_rate:.0%}) - {insight.recommended_approach}"
                )

        # Add general improvements
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=50))

        if records:
            avg_confidence = sum(r.confidence for r in records) / len(records)
            if avg_confidence < 85:
                improvements.append(
                    f"Increase decision confidence (current avg: {avg_confidence:.0f}%) - Gather more context before acting"
                )

        return improvements[:5]  # Top 5 improvements

    def validate_outcome(self, record_id: str, quality: int) -> None:
        """Validate the quality of a past action's outcome"""
        # Read all records
        records = []
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = LearningRecord(**json.loads(line))
                        if record.id == record_id:
                            record.outcome_quality = quality
                        records.append(record)

        # Rewrite file with updated record
        with open(self.memory_file, 'w') as f:
            for record in records:
                f.write(record.model_dump_json() + '\n')

        print(f"✅ [Memory] Validated outcome for {record_id}: {quality}/100")

    def get_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get learning statistics for an agent"""
        records = self.recall_relevant(
            MemoryQuery(agent_name=agent_name, limit=1000))

        if not records:
            return {
                "total_actions": 0,
                "success_rate": 0,
                "avg_confidence": 0,
                "insights_count": 0
            }

        successes = sum(1 for r in records if r.success)
        avg_confidence = sum(r.confidence for r in records) / len(records)
        insights = self.insights_cache.get(agent_name, [])

        return {
            "total_actions": len(records),
            "success_rate": successes / len(records),
            "avg_confidence": avg_confidence,
            "insights_count": len(insights),
            "recent_patterns": [i.pattern for i in insights][:3]
        }


class MemoryAwareMixin:
    """Mixin to add memory capabilities to any agent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = AgentMemory()
        self.agent_name = getattr(self, 'name', self.__class__.__name__)

    def learn_from_action(self,
                          action_type: str,
                          input_data: Any,
                          output_data: Any,
                          success: bool,
                          confidence: int,
                          patterns: List[str] = None) -> None:
        """Record learning from an action"""
        record = LearningRecord(
            id=f"{self.agent_name}_{datetime.now().isoformat()}",
            timestamp=datetime.now().isoformat(),
            agent_name=self.agent_name,
            action_type=action_type,
            input_summary=str(input_data)[:500],
            output_summary=str(output_data)[:500],
            success=success,
            confidence=confidence,
            patterns_learned=patterns or []
        )
        self.memory.record_action(record)

    def get_advice_for(self, task: str) -> str:
        """Get contextual advice for a task"""
        return self.memory.get_contextual_advice(self.agent_name, task)

    def analyze_my_patterns(self) -> List[AgentInsight]:
        """Analyze my own learning patterns"""
        return self.memory.analyze_patterns(self.agent_name)

    def my_improvement_suggestions(self) -> List[str]:
        """Get improvement suggestions for myself"""
        return self.memory.suggest_improvements(self.agent_name)

    def my_stats(self) -> Dict[str, Any]:
        """Get my learning statistics"""
        return self.memory.get_stats(self.agent_name)


# ============================================================================
# SECTION 6: GLOBAL INSTANCES
# ============================================================================

# Initialize global instances for easy access
audit_logger = AuditLogger()
feedback_engine = FeedbackEngine()
rate_limiter = RateLimiter(max_requests_per_minute=60,
                           max_requests_per_day=10000)
source_verification = SourceTracedVerification()


# ============================================================================
# SECTION 7: ENHANCED API CALL WRAPPER (NEW v7.6)
# ============================================================================

def call_gemini_with_rate_limit(agent_name: str, prompt: str,
                                model: str = "gemini-2.0-flash",
                                system_instruction: Optional[str] = None) -> Tuple[str, bool]:
    """
    Make a Gemini API call with automatic rate limiting and backoff.

    Args:
        agent_name: Name of calling agent (for rate limit tracking)
        prompt: The prompt to send
        model: Model to use
        system_instruction: Optional system instruction

    Returns:
        (response_text, success: bool)

    Example:
        response, success = call_gemini_with_rate_limit(
            'CommercialScout',
            'Find all Roland products on Halilit.com',
            system_instruction='You are a product harvester...'
        )
        if success:
            print(response)
        else:
            logger.error(f"API call failed: {response}")
    """
    if not genai_client:
        return "Error: Genai client not initialized", False

    # Check rate limit and wait if needed
    wait_time = rate_limiter.wait_if_needed(agent_name)
    if wait_time > 0:
        logger.info(f"⏱️  Waiting {wait_time:.1f}s due to rate limit...")
        time.sleep(wait_time)

    try:
        # Make API call
        rate_limiter.record_request(agent_name)

        response = genai_client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": system_instruction} if system_instruction else {}
        )

        response_text = response.text if hasattr(
            response, 'text') else str(response)

        # Record success
        rate_limiter.record_success(agent_name)
        audit_logger.log_event(
            category=AuditCategory.AGENT_ACTION,
            level=AuditLevel.INFO,
            action=f"API call succeeded: {agent_name}",
            agent_name=agent_name,
            output_data={"response_length": len(response_text)}
        )

        return response_text, True

    except Exception as e:
        error_code = None
        error_msg = str(e)

        # Extract HTTP error code if available
        if "429" in error_msg:
            error_code = 429
        elif "503" in error_msg:
            error_code = 503
        elif "QuotaExceededError" in error_msg:
            error_code = 429

        # Record failure with backoff
        rate_limiter.record_failure(agent_name, error_code=error_code)

        audit_logger.log_event(
            category=AuditCategory.ERROR_RECOVERY,
            level=AuditLevel.ERROR,
            action=f"API call failed: {agent_name}",
            agent_name=agent_name,
            error_message=error_msg,
            status="failure"
        )

        return f"API Error: {error_msg}", False


# ============================================================================
# TEST & UTILITIES
# ============================================================================

def test_agent_memory():
    """Test the memory system"""
    memory = AgentMemory()

    # Simulate some learning records
    for i in range(5):
        record = LearningRecord(
            id=f"test_{i}",
            timestamp=datetime.now().isoformat(),
            agent_name="DevAgent",
            action_type="fix",
            input_summary=f"Error: React hook violation {i}",
            output_summary=f"Fixed by moving hooks before return {i}",
            success=i < 4,  # 80% success rate
            confidence=85 + i * 2,
            patterns_learned=["hooks-before-return", "proper-dependency-array"]
        )
        memory.record_action(record)

    # Test retrieval
    records = memory.recall_relevant(MemoryQuery(
        agent_name="DevAgent",
        action_type="fix",
        limit=5
    ))

    print(f"\n✅ Retrieved {len(records)} records")

    # Test stats
    stats = memory.get_stats("DevAgent")
    print(f"\n📊 Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    test_agent_memory()

    # Test Rate Limiter
    print("\n" + "="*60)
    print("TESTING RATE LIMITER")
    print("="*60)

    limiter = RateLimiter(max_requests_per_minute=5)

    # Simulate 6 rapid requests (5th should trigger rate limit)
    for i in range(6):
        wait = limiter.wait_if_needed("TestAgent")
        if wait > 0:
            print(f"Request {i+1}: Rate limited! Wait {wait:.2f}s")
        else:
            print(f"Request {i+1}: OK")
        limiter.record_request("TestAgent")

    print(f"\n📊 Limiter status: {json.dumps(limiter.get_status(), indent=2)}")

    # Test Source Traceability
    print("\n" + "="*60)
    print("TESTING SOURCE TRACEABILITY")
    print("="*60)

    tracer = SourceTracedVerification()

    # Simulate verification with multiple sources
    source1 = SourceReference(
        source_type="url",
        source_url="https://halilit.com/product/roland-rd88",
        source_snippet="Roland RD-88 - ₪45,990",
        extraction_method="scrape",
        confidence=0.95
    )

    source2 = SourceReference(
        source_type="manufacturer_data",
        source_url="https://roland.com/specs/rd88",
        source_snippet="Professional 88-key stage keyboard",
        extraction_method="api",
        confidence=1.0
    )

    # Record verification with first source
    trace = tracer.verify_with_source(
        product_id="halilit_roland_rd88",
        field="official_price",
        value=45990,
        source=source1,
        agent_name="OfficialVerifier",
        confidence=0.95
    )

    # Add second source to the same verification
    tracer.add_verification_source(trace.verification_id, source2)

    # Get complete audit trail
    audit = tracer.get_verification_audit("halilit_roland_rd88")
    print(f"\n📋 Verification Audit:\n{json.dumps(audit, indent=2)}")
