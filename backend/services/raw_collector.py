# backend/services/raw_collector.py
import json
import os
from datetime import datetime
from typing import Dict, Any

class RawCollector:
    def __init__(self, base_path="backend/data/raw_landing_zone"):
        self.base_path = base_path

    def save_as_is(self, brand: str, model: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves the exact data scraped from the website, with no changes.
        """
        # Create brand folder
        brand_clean = brand.lower().replace(" ", "-")
        brand_path = os.path.join(self.base_path, brand_clean)
        os.makedirs(brand_path, exist_ok=True)

        # Add metadata about the scrape itself
        wrapper = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "source_url": raw_data.get("source_url", "unknown"),
                "brand": brand,
                "model": model
            },
            "raw_payload": raw_data # The 100% original unadulterated data
        }

        # Save to AS-IS file
        # Sanitize filename (remove newlines, replace spaces with underscores)
        safe_model = "".join(c for c in model if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_model = safe_model.lower().replace(' ', '_').replace('__', '_')
        
        filename = f"{safe_model}_raw.json"
        with open(os.path.join(brand_path, filename), "w", encoding="utf-8") as f:
            json.dump(wrapper, f, indent=2, ensure_ascii=False)
        
        return wrapper
