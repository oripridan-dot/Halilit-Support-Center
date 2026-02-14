"""
UNIFIED QUALITY GATES SYSTEM — v8.5 Backward-Compatibility Facade
══════════════════════════════════════════════════════════════════

The actual code now lives in focused modules:

  backend/quality/models.py   — All data models, enums, dataclasses
  backend/quality/audit.py    — AuditLogger + SourceTracedVerification
  backend/quality/gates.py    — All Gate classes + GateProcessor
  backend/quality/feedback.py — FeedbackEngine
  backend/quality/memory.py   — AgentMemory + MemoryAwareMixin
  backend/llm.py              — LLM gateway (replaces call_gemini_with_rate_limit)

This file re-exports EVERYTHING so existing imports keep working:
  from backend.unified_quality_gates import MemoryAwareMixin  # still works
  from backend.unified_quality_gates import call_gemini_with_rate_limit  # still works
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ── Re-export: Models ──────────────────────────────────────────────────────
from backend.quality.models import (  # noqa: F401
    AuditLevel, AuditCategory, AuditEvent,
    GateStatus, GateCheckResult,
    FeedbackType, AgentDecision, FeedbackRecord,
    SourceReference, VerificationTrace,
    LearningRecord, AgentInsight, MemoryQuery,
)

# ── Re-export: Audit ──────────────────────────────────────────────────────
from backend.quality.audit import AuditLogger, SourceTracedVerification  # noqa: F401

# ── Re-export: Gates ──────────────────────────────────────────────────────
from backend.quality.gates import (  # noqa: F401
    InputValidationGate, SecurityGate, DataIntegrityGate,
    ComplianceGate, SourceRulesGate, QualityGate,
    ContentQualityGate, GateProcessor,
)

# ── Re-export: Feedback ───────────────────────────────────────────────────
from backend.quality.feedback import FeedbackEngine  # noqa: F401

# ── Re-export: Memory ─────────────────────────────────────────────────────
from backend.quality.memory import AgentMemory, MemoryAwareMixin  # noqa: F401

# ── Global singletons (preserved for backward compat) ─────────────────────
audit_logger = AuditLogger()
feedback_engine = FeedbackEngine()
source_verification = SourceTracedVerification()

# Rate limiter is now inside backend.llm — expose a compat reference
try:
    from backend.llm import get_llm as _get_llm
    rate_limiter = _get_llm().rate_limiter
except Exception:
    rate_limiter = None  # type: ignore


# ── Backward-compat wrapper ───────────────────────────────────────────────
def call_gemini_with_rate_limit(
    agent_name: str,
    prompt: str,
    model: str = "gemini-2.0-flash",
    system_instruction: Optional[str] = None,
) -> Tuple[str, bool]:
    """
    Backward-compatible wrapper → delegates to backend.llm.LLMGateway.

    New code should use:
        from backend.llm import get_llm
        llm = get_llm()
        text, ok = llm.call(agent, prompt, system=system)
    """
    from backend.llm import get_llm
    llm = get_llm()
    return llm.call(
        agent_name, prompt,
        system=system_instruction,
        model=model,
    )
