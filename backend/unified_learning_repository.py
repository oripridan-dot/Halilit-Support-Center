"""
Learning Pattern Repository — Stores and retrieves patterns from agent learning.
Stub implementation; patterns are held in-memory for the current session.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LearningPattern:
    pattern_id: str
    brand: str
    category: str
    insight: str
    confidence: float = 0.9
    created_at: str = ""
    source: str = ""


class LearningPatternRepository:
    """In-memory repository for learning patterns (ephemeral)."""

    def __init__(self):
        self._patterns: Dict[str, LearningPattern] = {}
        logger.debug("LearningPatternRepository initialised (in-memory)")

    def save_pattern(self, pattern: LearningPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern
        logger.debug(
            f"Saved pattern {pattern.pattern_id}: {pattern.insight[:60]}")

    def get_pattern(self, pattern_id: str) -> Optional[LearningPattern]:
        return self._patterns.get(pattern_id)

    def get_patterns_for_brand(self, brand: str) -> List[LearningPattern]:
        return [p for p in self._patterns.values() if p.brand.lower() == brand.lower()]

    def get_all_patterns(self) -> List[LearningPattern]:
        return list(self._patterns.values())

    def get_most_recent_insight(self) -> Optional[str]:
        if not self._patterns:
            return None
        latest = max(self._patterns.values(), key=lambda p: p.created_at or "")
        return latest.insight
