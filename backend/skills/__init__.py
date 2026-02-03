"""
Skills Module - Modular Agent Capabilities

This module contains reusable, verifiable skills that agents can use.
Each skill implements BaseSkill and returns (success: bool, output: Any).
"""

from .base_skill import BaseSkill

__all__ = ['BaseSkill']
