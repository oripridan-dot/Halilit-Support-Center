"""
Skills Module - Modular Agent Capabilities

This module contains reusable, verifiable skills that agents can use.
Each skill implements BaseSkill and returns (success: bool, output: Any).

Ingestion Skills:
- HarvestSkill: Extract and normalize raw products
- EnrichSkill: Add taxonomy and official data
- TierSkill: Calculate pricing tier
- PrepareSkill: Set display properties
- ValidateSkill: Audit products
- ApproveSkill: Final decision and recording

Frontend Skills:
- ReactComponentBuilder: Safe component building with verification
"""

from .base_skill import BaseSkill
from .frontend_builder import ReactComponentBuilder
from .ingestion_skills import (
    HarvestSkill, EnrichSkill, TierSkill, PrepareSkill, ValidateSkill, ApproveSkill
)
from .skill_registry import SkillRegistry, SkillPipeline

__all__ = [
    'BaseSkill',
    'ReactComponentBuilder',
    'HarvestSkill',
    'EnrichSkill',
    'TierSkill',
    'PrepareSkill',
    'ValidateSkill',
    'ApproveSkill',
    'SkillRegistry',
    'SkillPipeline'
]
