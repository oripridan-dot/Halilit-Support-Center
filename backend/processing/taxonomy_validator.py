import json
from pathlib import Path
from typing import Dict, Any, Optional

# Constants
CONFIG_PATH = Path(__file__).resolve().parent.parent / \
    "data" / "refinery" / "0_config" / "taxonomy_rules.json"


class TaxonomyValidator:
    def __init__(self):
        self.rules = self._load_rules()
        self.scoring = self.rules.get("scoring_weights", {})
        self.thresholds = self.rules.get("global_validation_settings", {})

    def _load_rules(self) -> Dict:
        """Loads the adjustable brain from JSON."""
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"❌ Taxonomy Rules missing at: {CONFIG_PATH}")

        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def apply_taxonomy(self, product: Dict) -> Dict:
        """
        The Main Judge Function.
        Input: A merged product object (Official + Commercial + Context).
        Output: The UI Placement and Validation Report.
        """

        # 1. Classification (Where does it go?)
        classification = self._classify_product(product)

        # 2. Validation & Scoring (Does it deserve to be seen?)
        score_report = self._calculate_trust_score(product)

        # 3. Construct the UI Meta Object
        return {
            "ui_view": classification["view"],           # e.g. "TierBar"
            # e.g. "Studio Monitors"
            "primary_category": classification["category"],
            "sub_division": classification["sub_div"],   # e.g. "Nearfield"
            "y_axis_score": score_report["final_score"],  # 0-100
            # ["High Price Variance", "Verified Pro"]
            "validation_flags": score_report["flags"],
            # ["DIAMOND", "GOLD", "SILVER"]
            "badges": score_report["badges"]
        }

    def _classify_product(self, product: Dict) -> Dict:
        """Matches product data against JSON rule sets."""

        # We look at Official Name and Specs primarily (Official is King)
        name = product.get("official_name", "").lower()
        specs = product.get("specs", {})

        # Default Fallback
        result = {
            "view": "Grid",
            "category": "Uncategorized",
            "sub_div": "General"
        }

        # Iterate through defined Categories in JSON
        for category in self.rules["taxonomy_definitions"]:

            # Check Sub-Divisions (e.g. Nearfield vs Main)
            for sub in category["sub_divisions"]:
                rules = sub["rules"]

                # A. Keyword Check (Required)
                if not any(k in name for k in rules["required_keywords"]):
                    continue  # Skip if main keywords missing

                # B. Exclusion Check (Must NOT have)
                if any(k in name for k in rules.get("excluded_keywords", [])):
                    continue  # Skip if excluded keyword found

                # C. Spec Triggers (Deep Logic)
                # e.g. Woofer Size: Min 3.0, Max 8.0
                spec_match = True
                if "spec_triggers" in rules:
                    for spec_key, limits in rules["spec_triggers"].items():
                        # We try to find the spec value in the product's standardized specs
                        val = self._extract_spec_value(specs, spec_key)
                        if val is None:
                            # Policy: If spec is missing but needed for strict categorization,
                            # we might skip. For now, assume if not found, it doesn't disqualify
                            # unless it violates an explicit limit found elsewhere.
                            # BUT, to be "Adjustable", let's follow the prompt's implied logic:
                            # If triggers are present, we probably need a match.
                            # However, without real data, let's just create a "pass" if unknown for now,
                            # or "fail" if strict. The prompt implies logic: "if val < limits['min']".
                            # If val is None, we can't compare.
                            # Let's assume strict compliance: spec must exist.
                            spec_match = False
                            continue

                        if "min" in limits and val < limits["min"]:
                            spec_match = False
                        if "max" in limits and val > limits["max"]:
                            spec_match = False

                if spec_match:
                    return {
                        "view": "TierBar",  # Or read from config if dynamic
                        "category": category["id"],
                        "sub_div": sub["id"]
                    }

        return result

    def _calculate_trust_score(self, product: Dict) -> Dict:
        """Calculates the Y-Axis position based on Truth & Trust."""

        score = 0
        flags = []
        badges = []

        # --- 1. Base Official Data ---
        # "Official is King" - basic presence gives points
        if product.get("official_name"):
            score += self.scoring.get("base_official_data", 40)

        # --- 2. Commercial Logistics ---
        # Can we actually sell it?
        comm = product.get("commercial", {})
        if comm.get("price") and comm.get("price") > 0:
            score += self.scoring.get("has_price", 10)

        # Stock Status Logic
        stock_source = self.thresholds.get(
            "stock_status_priority", "COMMERCIAL")
        is_in_stock = False
        if stock_source == "COMMERCIAL" and comm.get("stock_status") == "IN_STOCK":
            is_in_stock = True

        # --- 3. Contextual Validators ---
        context = product.get("context", {})

        # Trusted Reviews Bonus
        review_count = len(context.get("verified_sources", []))
        if review_count > 0:
            score += (review_count * self.scoring.get("per_trusted_review", 15))
        else:
            # Unverified Penalty (Ghost Town factor)
            score += self.scoring.get("unverified_penalty", -10)
            flags.append("Community Unverified")

        # Recurring Issue Penalty
        issues = context.get("recurring_issues", [])
        if issues:
            penalty = self.scoring.get("recurring_issue_penalty", -25)
            # Ensure we don't double subtract if multiple logic paths exist, but simplest is fine
            score += penalty
            flags.append(f"Recurring Issue: {issues[0]}")

        # Verified Features
        # (This would be where we match "Pro Tip" keywords to specs)

        # --- 4. Final Badge Assignment ---
        final_score = max(0, min(100, score))  # Clamp 0-100

        if final_score >= self.thresholds.get("confidence_threshold_for_diamond", 80) and is_in_stock:
            badges.append("DIAMOND")
        elif final_score > 50:
            badges.append("GOLD")
        else:
            badges.append("SILVER")

        return {
            "final_score": final_score,
            "flags": flags,
            "badges": badges
        }

    def _extract_spec_value(self, specs: Dict, key: str) -> Optional[float]:
        """
        Helper to pull a number from a string spec.
        e.g. 'woofer_size_inch' maps to specs['woofer_size'] = "6.5 inches" -> 6.5
        """
        # Dictionary to map 'config_key' -> 'actual_spec_key'
        # In a real app, this map might be in config too.
        key_map = {
            "woofer_size_inch": "woofer_size_inch",
            "frequency_response_low_hz": "frequency_response_low_hz",
            "power_total_watts": "power_total_watts",
            "analog_inputs": "analog_inputs"
        }

        actual_key = key_map.get(key, key)
        val = specs.get(actual_key)

        # If val is already a number, return it
        if isinstance(val, (int, float)):
            return float(val)

        # If None, return None
        return None


# Usage Example
if __name__ == "__main__":
    validator = TaxonomyValidator()

    # Mock Data to Test
    test_product = {
        "official_name": "Adam Audio A7V Active Monitor",
        "specs": {"woofer_size_inch": 7.0},
        "commercial": {"price": 799, "stock_status": "IN_STOCK"},
        "context": {
            "verified_sources": ["SOS", "TapeOp"],
            "recurring_issues": []
        }
    }

    result = validator.apply_taxonomy(test_product)
    print(json.dumps(result, indent=2))
