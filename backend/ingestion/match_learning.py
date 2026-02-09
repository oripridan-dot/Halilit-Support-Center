import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any

class MatchLearningSystem:
    """
    Persists and retrieves confirmed product matches to avoid re-running expense AI checks.
    """
    def __init__(self, data_path: Path):
        self.file_path = data_path / "learned_matches.json"
        self.matches: Dict[str, Any] = {}
        self.logger = logging.getLogger("MatchLearning")
        self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.matches = json.load(f)
                self.logger.info(f"Loaded {len(self.matches)} learned matches.")
            except Exception as e:
                self.logger.warning(f"Failed to load matches: {e}")
                self.matches = {}

    def _save(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.matches, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save matches: {e}")

    def get_match(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored match for a Halilit product ID."""
        return self.matches.get(product_id)

    def register_match(self, product_id: str, candidate: Dict[str, Any], confidence: float):
        """Register a confirmed match."""
        self.matches[product_id] = {
            "candidate": candidate,
            "confidence": confidence,
            "timestamp": "iso_timestamp_here" # Add datetime logic if needed
        }
        self._save()

# Singleton instance setup handled by consumer or we can export a factory
