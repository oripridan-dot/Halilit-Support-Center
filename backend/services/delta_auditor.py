# backend/services/delta_auditor.py
import json
import os
from datetime import datetime
from typing import Dict, List, Set, Any

class DeltaAuditor:
    def __init__(self, report_dir="backend/data/reports/audit"):
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Define what constitutes a "Perfect" product
        self.required_fields = {
            "commercial": ["price", "sku", "stock_status"],
            "knowledge": ["manual_url", "description", "main_image"],
            "specs": ["weight", "dimensions"]
        }

    def audit_product(self, raw_data: Dict, blueprint: Dict) -> Dict:
        """
        Compares Raw Input vs. Processed Output to find gaps.
        """
        report = {
            "sku": blueprint.get("sku", "UNKNOWN"),
            "model": blueprint.get("model", "UNKNOWN"),
            "health_score": 100,
            "missing_critical": [],
            "extra_unmapped_data": []
        }

        # 1. Detect MISSING Data (Deficit)
        # Check top-level required fields
        # Note: Depending on the pipeline stage, data might be nested or not.
        # Assuming the 'Commercial Quarantine' structure is applied, we check inside 'official_knowledge'.
        # If not yet applied (processed blueprint might be flat), we check root.
        
        official = blueprint.get("official_knowledge", {})
        # If official_knowledge key doesn't exist, maybe it IS the flat blueprint.
        # Let's support both for robustness or check if blueprint structure has changed.
        # The prompt implies we ARE changing the structure.
        
        if not official and "name" in blueprint:
             # Fallback for flat structure if auditor runs before quarantine or on old data
             official = blueprint 
        
        if not official.get("manuals"):
            report["missing_critical"].append("No PDF Manuals")
            report["health_score"] -= 10
        
        if not official.get("images"):
            report["missing_critical"].append("No Images")
            report["health_score"] -= 20

        # Check deep specs
        specs = official.get("specs", {})
        if not specs:
             report["missing_critical"].append("No Technical Specs")
             report["health_score"] -= 15

        # 2. Detect EXTRA Data (Surplus)
        # Flatten raw keys to see what we ignored
        raw_keys = self._get_all_keys(raw_data)
        
        # This is a simplified check: If raw has "360" or "audio_sample"
        # and we didn't use it, flag it.
        interesting_keywords = ["360", "audio", "sample", "firmware", "driver", "cad", "drawing"]
        
        for key in raw_keys:
            if any(keyword in key.lower() for keyword in interesting_keywords):
                # Check if this data made it into the blueprint
                if not self._is_in_blueprint(key, blueprint):
                    report["extra_unmapped_data"].append(key)

        return report

    def _get_all_keys(self, d: Dict, parent_key: str = '') -> Set[str]:
        keys = set()
        for k, v in d.items():
            if isinstance(v, (list, tuple)):
                 # Skip iterating lists for keys unless lists contains dicts? 
                 # For simplicity, just add the key list name.
                 new_key = f"{parent_key}.{k}" if parent_key else k
                 keys.add(new_key)
            else:
                new_key = f"{parent_key}.{k}" if parent_key else k
                keys.add(new_key)
                if isinstance(v, dict):
                    keys.update(self._get_all_keys(v, new_key))
        return keys

    def _is_in_blueprint(self, key_term: str, blueprint: Dict) -> bool:
        # Simple heuristic: is this key string present in the blueprint values?
        # A real implementation would map specific raw keys to blueprint keys.
        # We search if the key term (e.g. "360_view") appears in stringified blueprint or if values match?
        # The prompt example: "extra_unmapped_data" contains keys.
        # The prompt logic: "Check if this data made it into the blueprint".
        # If I have a raw key "360_view", and I mapped it to "virtual_tour", "360_view" won't be in blueprint keys.
        # But maybe the value is?
        # Let's stick to the prompt's provided heuristic (check if key exists in stringified blueprint is a bit loose but that's what was asked).
        
        blueprint_str = json.dumps(blueprint).lower()
        # Clean the key term to just the last part for better matching?
        # e.g. "downloads.dxf_file". If blueprint has "dxf_file" key or value?
        # The prompt says: "return key_term.lower() in blueprint_str"
        return key_term.lower() in blueprint_str

    def save_brand_report(self, brand: str, audit_results: List[Dict]):
        path = os.path.join(self.report_dir, f"{brand}_audit_report.json")
        
        summary = {
            "brand": brand,
            "timestamp": datetime.now().isoformat(),
            "products_audited": len(audit_results),
            "perfect_products": sum(1 for r in audit_results if r['health_score'] == 100),
            "average_health": sum(r['health_score'] for r in audit_results) / len(audit_results) if audit_results else 0,
            "details": audit_results
        }
        
        with open(path, 'w') as f:
            json.dump(summary, f, indent=2)
        return path
