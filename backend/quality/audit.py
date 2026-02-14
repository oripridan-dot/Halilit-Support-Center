"""
Audit Logger — Comprehensive operation traceability.
Split from unified_quality_gates.py Section 2.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import asdict
from functools import wraps

from backend.quality.models import (
    AuditLevel, AuditCategory, AuditEvent,
    SourceReference, VerificationTrace,
)

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logging for all pipeline operations.
    Tracks agent actions, security events, and performance.
    """

    def __init__(self, log_dir: str = ""):
        if not log_dir:
            log_dir = str(Path(__file__).resolve(
            ).parent.parent / "logs" / "audit")
        self.log_dir = log_dir
        self.events: List[AuditEvent] = []
        self.event_index: Dict[str, AuditEvent] = {}
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(
            log_dir, f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.json_log_file = os.path.join(log_dir, "events.jsonl")
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

        log_msg = f"[{category.value.upper()}] {action} - Status: {status}"
        if agent_name:
            log_msg += f" (Agent: {agent_name})"

        if level in (AuditLevel.CRITICAL, AuditLevel.SECURITY):
            logger.critical(log_msg)
        elif level == AuditLevel.ERROR:
            logger.error(log_msg)
        elif level == AuditLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return event_id

    def log_agent_action(self, agent_name: str, action: str,
                         input_data: Dict, output_data: Dict,
                         success: bool = True,
                         execution_time_ms: float = 0.0) -> str:
        return self.log_event(
            category=AuditCategory.AGENT_ACTION,
            level=AuditLevel.INFO if success else AuditLevel.WARNING,
            action=action, agent_name=agent_name,
            input_data=input_data, output_data=output_data,
            status="success" if success else "failure",
            execution_time_ms=execution_time_ms,
        )

    def log_verification(self, agent_name: str, item_type: str,
                         item_id: str, passed: bool,
                         violations: Optional[List[str]] = None,
                         risk_score: int = 0) -> str:
        return self.log_event(
            category=AuditCategory.VERIFICATION_GATE,
            level=AuditLevel.WARNING if not passed else AuditLevel.INFO,
            action=f"Verified {item_type}: {item_id}",
            agent_name=agent_name,
            input_data={"item_type": item_type, "item_id": item_id},
            output_data={"passed": passed, "violations": violations or [],
                         "risk_score": risk_score},
            status="success" if passed else "failure",
            verification_passed=passed,
        )

    def log_security_event(self, event_type: str, description: str,
                           threat_level: str = "medium",
                           details: Optional[Dict] = None) -> str:
        level_map = {
            "low": AuditLevel.WARNING, "medium": AuditLevel.WARNING,
            "high": AuditLevel.CRITICAL, "critical": AuditLevel.CRITICAL,
        }
        return self.log_event(
            category=AuditCategory.SECURITY_CHECK,
            level=level_map.get(threat_level, AuditLevel.WARNING),
            action=f"Security: {event_type}",
            output_data={"threat_level": threat_level,
                         "details": details, "description": description},
            status="flagged",
        )

    def log_approval_decision(self, agent_name: str, decision_type: str,
                              item_id: str, approved: bool,
                              confidence: float, rationale: str) -> str:
        return self.log_event(
            category=AuditCategory.APPROVAL_DECISION,
            level=AuditLevel.INFO,
            action=f"{agent_name} {'APPROVED' if approved else 'REJECTED'}: {decision_type}",
            agent_name=agent_name,
            input_data={"item_id": item_id, "decision_type": decision_type},
            output_data={"approved": approved, "confidence": confidence,
                         "rationale": rationale},
            status="success",
        )

    def log_error_recovery(self, agent_name: str, error_type: str,
                           original_error: str, recovery_action: str,
                           recovery_successful: bool) -> str:
        return self.log_event(
            category=AuditCategory.ERROR_RECOVERY,
            level=AuditLevel.WARNING if recovery_successful else AuditLevel.ERROR,
            action=f"Error recovery attempt: {error_type}",
            agent_name=agent_name,
            input_data={"error_type": error_type,
                        "original_error": original_error},
            output_data={"recovery_action": recovery_action,
                         "recovered": recovery_successful},
            status="success" if recovery_successful else "failure",
        )

    def audit_flow(self, category: AuditCategory,
                   agent_name: Optional[str] = None):
        """Decorator to automatically audit function calls."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start) * 1000
                    self.log_event(
                        category=category, level=AuditLevel.INFO,
                        action=f"Executed {func.__name__}",
                        agent_name=agent_name,
                        output_data={"result_type": type(result).__name__},
                        execution_time_ms=duration_ms, status="success",
                    )
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start) * 1000
                    self.log_event(
                        category=category, level=AuditLevel.ERROR,
                        action=f"Failed: {func.__name__}",
                        agent_name=agent_name, error_message=str(e),
                        execution_time_ms=duration_ms, status="failure",
                    )
                    raise
            return wrapper
        return decorator

    def get_audit_trail(self, agent_name: Optional[str] = None,
                        category: Optional[AuditCategory] = None,
                        limit: int = 100) -> List[Dict]:
        events = self.events
        if agent_name:
            events = [e for e in events if e.agent_name == agent_name]
        if category:
            events = [e for e in events if e.category == category]
        return [
            {"event_id": e.event_id, "timestamp": e.timestamp,
             "category": e.category.value, "level": e.level.value,
             "agent": e.agent_name, "action": e.action,
             "status": e.status, "execution_time_ms": e.execution_time_ms}
            for e in sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]
        ]

    def get_security_audit(self) -> Dict:
        security_events = [
            e for e in self.events if e.category == AuditCategory.SECURITY_CHECK]
        critical = len(
            [e for e in security_events if e.level == AuditLevel.CRITICAL])
        high = len([e for e in security_events
                    if e.level in [AuditLevel.ERROR, AuditLevel.CRITICAL]])
        return {
            "timestamp": datetime.now().isoformat(),
            "total_security_events": len(security_events),
            "critical_events": critical,
            "high_severity_events": high,
            "recent_events": self.get_audit_trail(
                category=AuditCategory.SECURITY_CHECK, limit=20),
        }

    def get_performance_report(self) -> Dict:
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
                "successful": successful, "failed": failed,
                "success_rate": round(
                    (successful / len(agent_events) * 100) if agent_events else 0, 2),
                "avg_execution_time_ms": round(avg_time_ms, 2),
                "total_execution_time_ms": round(total_time_ms, 2),
            }
        return {"timestamp": datetime.now().isoformat(), "by_agent": performance}

    def _save_event(self, event: AuditEvent) -> None:
        with open(self.json_log_file, "a") as f:
            f.write(json.dumps(asdict(event), default=str) + "\n")

    def _load_historical_events(self) -> None:
        if not os.path.exists(self.json_log_file):
            return
        try:
            with open(self.json_log_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        cat_str = data.get("category", "").upper()
                        if "." in cat_str:
                            cat_str = cat_str.split(".")[-1]
                        level_str = data.get("level", "").upper()
                        if "." in level_str:
                            level_str = level_str.split(".")[-1]
                        data["category"] = AuditCategory[cat_str]
                        data["level"] = AuditLevel[level_str]
                        event = AuditEvent(**data)
                        self.events.append(event)
                        self.event_index[event.event_id] = event
                    except Exception as exc:
                        logger.debug("Skipping malformed audit event: %s", exc)
        except FileNotFoundError:
            pass


class SourceTracedVerification:
    """Enhanced verification that tracks sources for all data points."""

    def __init__(self, log_dir: str = ""):
        if not log_dir:
            log_dir = str(Path(__file__).resolve(
            ).parent.parent / "logs" / "verification")
        self.log_dir = log_dir
        self.traces: Dict[str, VerificationTrace] = {}
        os.makedirs(log_dir, exist_ok=True)
        self.traces_file = os.path.join(log_dir, "verification_traces.jsonl")

    def verify_with_source(self, product_id: str, field: str, value: Any,
                           source: SourceReference, agent_name: str = "",
                           confidence: float = 1.0) -> VerificationTrace:
        from datetime import datetime
        trace_id = f"trace_{product_id}_{field}_{datetime.now().isoformat()}"
        trace = VerificationTrace(
            verification_id=trace_id, product_id=product_id,
            verified_field=field, verified_value=value,
            auditor_agent=agent_name, confidence_score=confidence,
            is_approved=True,
        )
        trace.add_source(source)
        self.traces[trace_id] = trace
        self._save_trace(trace)
        logger.info(
            f"Verification traced: {product_id}.{field} from {source.source_type}")
        return trace

    def add_verification_source(self, trace_id: str, source: SourceReference) -> None:
        if trace_id in self.traces:
            self.traces[trace_id].add_source(source)
            self._save_trace(self.traces[trace_id])

    def get_verification_audit(self, product_id: str) -> Dict:
        from datetime import datetime
        product_traces = [
            t for t in self.traces.values() if t.product_id == product_id]
        return {
            "product_id": product_id,
            "total_verifications": len(product_traces),
            "verified_fields": [t.verified_field for t in product_traces],
            "verifications": [
                {"field": t.verified_field, "value": str(t.verified_value)[:100],
                 "confidence": t.confidence_score, "auditor": t.auditor_agent,
                 "sources": t.source_summary()}
                for t in product_traces
            ],
            "audit_timestamp": datetime.now().isoformat(),
        }

    def _save_trace(self, trace: VerificationTrace) -> None:
        trace_dict = asdict(trace)
        trace_dict['sources'] = [asdict(s) for s in trace.sources]
        with open(self.traces_file, 'a') as f:
            f.write(json.dumps(trace_dict, default=str) + '\n')
