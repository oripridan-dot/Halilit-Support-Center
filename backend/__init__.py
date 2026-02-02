"""
Halilit Support Center v5.1 - ADK Backend
=========================================

Agent Development Kit (ADK) powered backend with Trinity Swarm:
- CommercialScout: Data harvester
- OfficialVerifier: Data enricher
- ExternalValidator: Compliance auditor

FastAPI server bridges frontend to agents via /api/copilot/chat
"""

__version__ = "5.1.0"
__adk_enabled__ = True

from backend.agents.trinity_swarm import (
    TrinitySwarm,
    CommercialAgent,
    OfficialAgent,
    ValidatorAgent,
    AgentBase,
    ProductDraft,
    AuditReport,
)

__all__ = [
    "TrinitySwarm",
    "CommercialAgent",
    "OfficialAgent",
    "ValidatorAgent",
    "AgentBase",
    "ProductDraft",
    "AuditReport",
]
