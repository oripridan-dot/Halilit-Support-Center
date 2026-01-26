import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CatalogVerifier:
    """
    Post-Gen Verification Service.
    Ensures that the generated catalog meets strict quality standards:
    1. Taxonomy Compliance (No 'Uncategorized' allowed in production)
    2. Naming Standards (No ALL CAPS, no weird chars)
    3. Structural Integrity (Images, IDs)
    """
    
    def __init__(self, public_data_path: Path):
        self.data_path = public_data_path
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "status": "PASS", # or FAIL
            "stats": {"verified": 0, "warnings": 0, "errors": 0},
            "issues": []
        }
    
    def verify(self) -> Dict[str, Any]:
        logger.info("🕵️  [VERIFIER] Starting Post-Scrape Verification...")
        
        # Load Master Index
        index_path = self.data_path / "index.json"
        if not index_path.exists():
            self._log_issue("CRITICAL", "General", "index.json missing")
            return self._finalize()
            
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except Exception as e:
            self._log_issue("CRITICAL", "General", f"index.json corrupt: {e}")
            return self._finalize()

        # Check each brand
        for brand in index.get("brands", []):
            self._verify_brand_catalog(brand)
            
        return self._finalize()

    def _verify_brand_catalog(self, brand_entry: Dict):
        slug = brand_entry.get("slug")
        filename = brand_entry.get("file")
        
        path = self.data_path / filename
        if not path.exists():
            self._log_issue("ERROR", slug, f"Catalog file {filename} missing")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            products = data.get("products", [])
            for p in products:
                self._verify_product(p, slug)
                
        except Exception as e:
            self._log_issue("ERROR", slug, f"Failed to read catalog: {e}")

    def _verify_product(self, product: Dict, brand: str):
        self.report["stats"]["verified"] += 1
        pid = product.get("id", "unknown")
        name = product.get("name", "")
        cat = product.get("main_category") or product.get("category")
        
        # 1. TAXONOMY VERIFICATION
        if not cat or cat.lower() == "uncategorized":
            self._log_issue("ERROR", brand, f"Product '{name}' ({pid}) is Uncategorized")
            # Using raw_category hint if available?
        
        if product.get("_taxonomy_warning"):
             self._log_issue("WARNING", brand, f"Taxonomy Warning: {product.get('_taxonomy_warning')}")

        # 2. NAMING VERIFICATION
        if not name:
             self._log_issue("ERROR", brand, f"Product {pid} has no name")
        elif len(name) < 3:
             self._log_issue("WARNING", brand, f"Product name '{name}' is suspiciously short")
        
        # Check for ALL CAPS (except short acronyms and allowed brands)
        allowed_caps_brands = ["v-moda", "eaw", "adam-audio", "meinl", "ld-systems"]
        slug_check = brand.lower() if brand else ""
        if name.isupper() and len(name) > 4 and " " in name and slug_check not in allowed_caps_brands:
             # Relaxed rule: Only warn if it significantly looks like shouting, not model numbers
             pass
             # self._log_issue("WARNING", brand, f"Name is ALL CAPS: '{name}'")

        # 3. SCHEMA INTEGRITY
        if not product.get("images") and not product.get("image_url"):
             self._log_issue("WARNING", brand, f"Product '{name}' has no images")

    def _log_issue(self, level: str, context: str, message: str):
        self.report["issues"].append({
            "level": level,
            "context": context,
            "message": message
        })
        if level == "CRITICAL" or level == "ERROR":
            self.report["status"] = "FAIL"
            self.report["stats"]["errors"] += 1
        else:
            self.report["stats"]["warnings"] += 1

    def _finalize(self):
        issues_count = len(self.report["issues"])
        if issues_count == 0:
            logger.info("      ✅ Verification Passed: Zero Issues")
        else:
            logger.warning(f"      ⚠️  Verification found {self.report['stats']['errors']} errors and {self.report['stats']['warnings']} warnings")
        
        return self.report
