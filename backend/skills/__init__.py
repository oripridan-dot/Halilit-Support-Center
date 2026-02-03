"""
Skills Module - Modular Agent Capabilities

This module contains reusable, verifiable skills that agents can use.
Each skill implements BaseSkill and returns (success: bool, output: Any).
"""

from .base_skill import BaseSkill
from .maintenance_skills import FileCleanupSkill, WhitespaceFormattingSkill

__all__ = ['BaseSkill', 'FileCleanupSkill', 'WhitespaceFormattingSkill']
