from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LearningPattern:
    """
    Represents a specific learned insight about a brand or category.
    Used to inject knowledge into future agent runs.
    """
    pattern_id: str
    brand: str
    category: str
    insight: str  # e.g., "Brand X often uses accessory photos for main listings"
    confidence: float
    created_at: str
    # visual_validator, manual_review, etc.
    source: str = "conflict_resolution"

# ============================================================================
# LEARNING REPOSITORY
# ============================================================================


class LearningPatternRepository:
    """
    Manages the persistence and retrieval of learned patterns.
    Acts as the 'Long Term Memory' for agent strategy.
    """

    def __init__(self, memory_dir: str = ".agent_memory"):
        self.memory_dir = Path(memory_dir)
        self.patterns_file = self.memory_dir / "learning_patterns.json"
        self._ensure_storage()

    def _ensure_storage(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        if not self.patterns_file.exists():
            with open(self.patterns_file, "w") as f:
                json.dump([], f)

    def save_pattern(self, pattern: LearningPattern):
        patterns = self._load_patterns()
        # Check for duplicates based on insight text and brand
        if any(p['insight'] == pattern.insight and p['brand'] == pattern.brand for p in patterns):
            return  # Skip duplicate

        patterns.append(asdict(pattern))
        with open(self.patterns_file, "w") as f:
            json.dump(patterns, f, indent=2)
        logger.info(
            f"🧠 Learned new pattern for {pattern.brand}: {pattern.insight}")

    def get_brand_insights(self, brand: str) -> List[str]:
        """Retrieve all insights valid for a specific brand."""
        patterns = self._load_patterns()
        # Filter for this brand or 'ALL'
        return [p['insight'] for p in patterns if p['brand'].lower() == brand.lower() or p['brand'] == "ALL"]

    def get_most_recent_insight(self) -> Optional[Dict]:
        """Retrieve the single most recent insight added to the system."""
        patterns = self._load_patterns()
        if not patterns:
            return None
        return patterns[-1]

    def _load_patterns(self) -> List[dict]:
        try:
            with open(self.patterns_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
