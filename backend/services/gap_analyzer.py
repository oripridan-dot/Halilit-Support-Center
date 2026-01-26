# backend/services/gap_analyzer.py
import json
import os
from typing import List, Dict, Set, Any
from datetime import datetime

class GapAnalyzer:
    def __init__(self, radar_dir="data/radar", blueprint_dir="data/blueprints"):
        self.radar_dir = radar_dir
        self.blueprint_dir = blueprint_dir
        self.report_dir = "data/reports/opportunities"
        os.makedirs(self.report_dir, exist_ok=True)

    def _load_json(self, path: str) -> List[Dict]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Handle wrapped data vs direct list
                # Some blueprints wrap products in "products" key, others might not
                result = data.get('products', data) if isinstance(data, dict) else data
                # Ensure result is a list
                if not isinstance(result, list):
                     result = []
                return result
        except FileNotFoundError:
            return []

    def _normalize_name(self, name: str) -> str:
        """
        Strip spaces, dashes, and lowercase for fuzzy comparison.
        e.g., "Fantom-06" -> "fantom06"
        """
        if not name: return ""
        return name.lower().replace("-", "").replace(" ", "").replace("_", "")

    def run_analysis(self, brand: str) -> Dict[str, Any]:
        print(f"🕵️‍♂️ Analyzing Gaps for {brand}...")

        # 1. Load The "Global Truth" (Radar Data)
        radar_path = os.path.join(self.radar_dir, f"{brand}_global.json")
        global_catalog = self._load_json(radar_path)
        
        if not global_catalog:
            print(f"⚠️ No Global Radar data found for {brand}. Run GlobalRadar first.")
            # Return empty report structure rather than None to be safe
            return {
                "brand": brand,
                "generated_at": datetime.now().isoformat(),
                "error": "No radar data found",
                "missing_count": 0,
                "opportunities": []
            }

        # 2. Load "Our Inventory" (Blueprints)
        blueprint_path = os.path.join(self.blueprint_dir, f"{brand}_blueprint.json")
        our_inventory = self._load_json(blueprint_path)

        # 3. Create Comparison Sets
        # Helper to safely get model/name
        def get_identifier(item):
            return item.get('model', item.get('name', ''))

        our_model_codes = {self._normalize_name(get_identifier(p)) for p in our_inventory}
        
        missing_goodies = []
        
        for item in global_catalog:
            raw_model_name = get_identifier(item)
            norm_name = self._normalize_name(raw_model_name)
            
            # If we don't have it, and it's not a generic accessory/cable check
            if norm_name and norm_name not in our_model_codes:
                missing_goodies.append({
                    "model": raw_model_name,
                    "category": item.get('category', 'Unknown'),
                    "url": item.get('url'),
                    "image": item.get('image'),
                    "status": "OPPORTUNITY" # Flag for the UI
                })

        # 4. Generate Report
        report = {
            "brand": brand,
            "generated_at": datetime.now().isoformat(),
            "total_global_models": len(global_catalog),
            "our_models": len(our_inventory),
            "missing_count": len(missing_goodies),
            "opportunities": missing_goodies
        }

        # 5. Save Report
        save_path = os.path.join(self.report_dir, f"{brand}_opportunities.json")
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Found {len(missing_goodies)} missing products! Report saved to {save_path}")
        return report
