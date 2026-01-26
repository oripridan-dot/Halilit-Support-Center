# backend/analyze_gaps.py
import json
import os
from typing import List, Dict, Set
import difflib

class GapAnalyzer:
    def __init__(self, brand: str):
        self.brand = brand
        self.radar_path = f"backend/data/radar/{brand.lower()}_global.json"
        self.blueprint_path = f"backend/data/blueprints/{brand.lower()}_blueprint.json"
        self.output_path = f"backend/data/radar/{brand.lower()}_gap_report.json"

    def load_json(self, path: str) -> List[Dict]:
        if not os.path.exists(path):
            print(f"⚠️ Warning: File not found: {path}")
            return []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle different structures
            if isinstance(data, dict) and "products" in data:
                return data["products"]
            return data

    def normalize_name(self, name: str) -> str:
        """Normalize product name for comparison"""
        return name.lower().replace("-", "").replace(" ", "").replace("_", "")

    def analyze(self):
        print(f"🔍 Analyzing Gaps for {self.brand}...")
        
        # 1. Load Data
        global_products = self.load_json(self.radar_path)
        local_products = self.load_json(self.blueprint_path)
        
        print(f"   Global Scope: {len(global_products)} products")
        print(f"   Local Inventory: {len(local_products)} products")

        # 2. Build Lookup Sets
        local_normalized = set()
        for p in local_products:
            # Try 'model', 'name', or 'id'
            name = p.get('model') or p.get('name') or p.get('id', '')
            if name:
                local_normalized.add(self.normalize_name(name))

        # 3. Identify Missing
        missing_products = []
        for gp in global_products:
            g_name = gp.get('model') or gp.get('name', 'Unknown')
            g_norm = self.normalize_name(g_name)
            
            if g_norm not in local_normalized:
                # Fuzzy match check (to avoid false positives like "Fantom 8" vs "Fantom-8")
                # If we are really paranoid, we can use difflib
                missing_products.append(gp)

        # 4. Generate Report
        report = {
            "brand": self.brand,
            "total_global": len(global_products),
            "total_local": len(local_products),
            "missing_count": len(missing_products),
            "missing_products": missing_products
        }

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Gap Analysis Complete!")
        print(f"   Found {len(missing_products)} products missing from Halilit inventory.")
        print(f"   Report saved to: {self.output_path}")
        
        return report

if __name__ == "__main__":
    # Example usage
    import sys
    brand = sys.argv[1] if len(sys.argv) > 1 else "Roland"
    analyzer = GapAnalyzer(brand)
    analyzer.analyze()
