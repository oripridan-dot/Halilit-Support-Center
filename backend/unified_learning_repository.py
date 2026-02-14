"""
Learning Pattern Repository — Stores and retrieves patterns from agent learning.
Persists patterns to disk (JSONL) so they survive restarts.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

_PERSIST_PATH = Path(__file__).resolve().parent / \
    "data" / "learning_patterns.jsonl"


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
    """File-backed repository for learning patterns."""

    def __init__(self, path: Optional[Path] = None):
        self._path = path or _PERSIST_PATH
        self._patterns: Dict[str, LearningPattern] = {}
        self._load()

    # ── Persistence ────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text().splitlines():
                if not line.strip():
                    continue
                d = json.loads(line)
                p = LearningPattern(**d)
                self._patterns[p.pattern_id] = p
            logger.debug(
                f"Loaded {len(self._patterns)} learning patterns from {self._path.name}")
        except Exception as e:
            logger.warning(f"Failed to load learning patterns: {e}")

    def _append(self, pattern: LearningPattern) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a") as f:
                f.write(json.dumps(asdict(pattern)) + "\n")
        except Exception as e:
            logger.warning(f"Failed to persist learning pattern: {e}")

    # ── CRUD ───────────────────────────────────────────────────────────

    def save_pattern(self, pattern: LearningPattern) -> None:
        self._patterns[pattern.pattern_id] = pattern
        self._append(pattern)
        logger.debug(
            f"Saved pattern {pattern.pattern_id}: {pattern.insight[:60]}")

    def get_pattern(self, pattern_id: str) -> Optional[LearningPattern]:
        return self._patterns.get(pattern_id)

    def get_patterns_for_brand(self, brand: str) -> List[LearningPattern]:
        return [p for p in self._patterns.values() if p.brand.lower() == brand.lower()]

    def get_brand_insights(self, brand: str) -> List[str]:
        """Return insight strings for a brand (used by agents and learning system)."""
        return [p.insight for p in self.get_patterns_for_brand(brand)]

    def get_all_patterns(self) -> List[LearningPattern]:
        return list(self._patterns.values())

    def get_most_recent_insight(self) -> Optional[Dict]:
        """Return the most recent pattern as a dict (used by SSE streams)."""
        if not self._patterns:
            return None
        latest = max(self._patterns.values(), key=lambda p: p.created_at or "")
        return asdict(latest)
