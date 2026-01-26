"""
RELATIONSHIP ENGINE v1.0
========================
Discovers and maps product relationships:
- Necessities: Items required for operation (cables, power supplies)
- Accessories: Compatible add-on items (cases, stands, covers)
- Related: Similar products in the same category/tier
"""

import json
import logging
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ProductRelationship:
    """Represents a single relationship between two products."""
    source_sku: str
    related_sku: str
    relationship_type: str  # "necessity" | "accessory" | "related"
    confidence: float  # 0.0-1.0
    reason: str  # Human-readable explanation


class ProductRelationshipEngine:
    """
    Analyzes blueprints to find Accessories, Related Products, and Necessities.
    
    This engine:
    1. Analyzes product categories and specifications
    2. Identifies cross-brand compatible items
    3. Scores relationships by confidence
    4. Filters false positives
    """
    
    # NECESSITY KEYWORDS: Products required for operation
    NECESSITY_KEYWORDS = {
        "power": ["power supply", "adapter", "ac adapter", "power cord", "power cable"],
        "cables": ["cable", "cord", "xlr", "usb", "midi", "rca", "3.5mm", "jack", "connector"],
        "mounting": ["stand", "mount", "bracket", "clip", "holder", "rack", "pedal board"],
        "protection": ["case", "bag", "cover", "gig bag", "soft case", "hard case"],
        "tools": ["tuner", "strap", "picks", "strings", "drum key", "wrench"],
    }
    
    # ACCESSORY KEYWORDS: Optional add-ons
    ACCESSORY_KEYWORDS = {
        "stands": ["stand", "boom", "tripod", "desk stand"],
        "cases": ["case", "bag", "cover", "gig bag"],
        "upgrades": ["pedal", "switch", "mod", "upgrade"],
        "cosmetic": ["strap", "strap locks", "covers"],
    }
    
    # CATEGORY SIMILARITY MAP
    CATEGORY_SIMILARITIES = {
        "studio": ["studio", "recording", "audio", "mixing"],
        "live": ["live", "sound", "pa", "amplification"],
        "dj": ["dj", "production", "mixing"],
        "guitars": ["guitars", "bass", "string"],
        "drums": ["drums", "percussion"],
        "keys": ["keys", "piano", "synthesizer", "keyboards"],
    }
    
    def __init__(self):
        self.relationships: List[ProductRelationship] = []
        self.all_products: Dict[str, Dict] = {}
    
    def analyze_all_blueprints(self, all_products: List[Dict]) -> Dict[str, Dict]:
        """
        Main entry point: Analyzes all products and returns enriched blueprints.
        
        Args:
            all_products: List of product blueprints from all brands
        
        Returns:
            Dict mapping product SKU to enriched product with relationships
        """
        logger.info(f"🔗 Analyzing {len(all_products)} products for relationships...")
        
        # Build lookup index
        self.all_products = {p.get("sku"): p for p in all_products if p.get("sku")}
        
        enriched_products = {}
        
        for product in all_products:
            sku = product.get("sku")
            if not sku:
                continue
            
            # Discover relationships for this product
            relationships = self.discover_relationships(product)
            
            # Enrich product with relationship data
            enriched_product = product.copy()
            enriched_product["necessities"] = relationships["necessities"]
            enriched_product["accessories"] = relationships["accessories"]
            enriched_product["related"] = relationships["related"]
            
            enriched_products[sku] = enriched_product
        
        logger.info(f"✅ Relationship analysis complete. {len(self.relationships)} relationships discovered.")
        return enriched_products
    
    def discover_relationships(self, product: Dict) -> Dict[str, List[Dict]]:
        """
        Discovers all relationships for a single product.
        
        Returns:
            {
                "necessities": [product dicts],
                "accessories": [product dicts],
                "related": [product dicts]
            }
        """
        results = {
            "necessities": [],
            "accessories": [],
            "related": []
        }
        
        sku = product.get("sku")
        category = product.get("category", "").lower()
        name = product.get("name", "").lower()
        specs = product.get("specs", {})
        
        for candidate_sku, candidate in self.all_products.items():
            if candidate_sku == sku:
                continue  # Skip self
            
            # Check if this product is a necessity
            necessity_score = self._score_necessity(product, candidate)
            if necessity_score > 0.6:
                results["necessities"].append(candidate)
                self.relationships.append(ProductRelationship(
                    source_sku=sku,
                    related_sku=candidate_sku,
                    relationship_type="necessity",
                    confidence=necessity_score,
                    reason=f"Required for {product.get('name', 'this product')}"
                ))
                continue
            
            # Check if this product is an accessory
            accessory_score = self._score_accessory(product, candidate)
            if accessory_score > 0.6:
                results["accessories"].append(candidate)
                self.relationships.append(ProductRelationship(
                    source_sku=sku,
                    related_sku=candidate_sku,
                    relationship_type="accessory",
                    confidence=accessory_score,
                    reason=f"Compatible with {product.get('name', 'this product')}"
                ))
                continue
            
            # Check if this is a related product
            related_score = self._score_related(product, candidate)
            if related_score > 0.7:
                results["related"].append(candidate)
                self.relationships.append(ProductRelationship(
                    source_sku=sku,
                    related_sku=candidate_sku,
                    relationship_type="related",
                    confidence=related_score,
                    reason=f"Similar to {product.get('name', 'this product')}"
                ))
        
        # Limit results to top matches
        results["necessities"] = sorted(
            results["necessities"], 
            key=lambda x: x.get("price", 0), 
            reverse=True
        )[:5]
        results["accessories"] = results["accessories"][:8]
        results["related"] = results["related"][:6]
        
        return results
    
    def _score_necessity(self, product: Dict, candidate: Dict) -> float:
        """
        Score how likely candidate is a NECESSITY for the main product.
        
        Necessities are things like:
        - Power supplies for keyboards/pedals
        - Cables for any audio equipment
        - Stands for microphones/monitors
        """
        score = 0.0
        
        product_category = product.get("category", "").lower()
        candidate_name = candidate.get("name", "").lower()
        candidate_category = candidate.get("category", "").lower()
        
        # Rule 1: Product name contains necessity keywords
        for keyword in self.NECESSITY_KEYWORDS.get("power", []):
            if keyword in candidate_name and any(cat in product_category for cat in ["keyboard", "pedal", "synth"]):
                score += 0.7
        
        for keyword in self.NECESSITY_KEYWORDS.get("cables", []):
            if keyword in candidate_name and any(cat in product_category for cat in ["audio", "studio", "live"]):
                score += 0.5
        
        for keyword in self.NECESSITY_KEYWORDS.get("mounting", []):
            if keyword in candidate_name and any(cat in product_category for cat in ["microphone", "monitor", "speaker"]):
                score += 0.6
        
        # Rule 2: Check compatibility hints in specs
        product_specs = str(product.get("specs", {})).lower()
        if "power supply" in product_specs and "power" in candidate_name.lower():
            score += 0.4
        
        # Rule 3: Category-based heuristic
        if candidate_category in ["accessories", "cables", "stands", "covers"]:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_accessory(self, product: Dict, candidate: Dict) -> float:
        """
        Score how likely candidate is an ACCESSORY for the main product.
        
        Accessories are things like:
        - Cases for instruments
        - Stands for equipment
        - Upgrades for synths/pedals
        """
        score = 0.0
        
        product_category = product.get("category", "").lower()
        candidate_name = candidate.get("name", "").lower()
        candidate_category = candidate.get("category", "").lower()
        
        # Rule 1: Explicit accessory keywords
        for keyword in self.ACCESSORY_KEYWORDS.get("cases", []):
            if keyword in candidate_name and any(cat in product_category for cat in ["guitar", "keyboard", "bass"]):
                score += 0.7
        
        for keyword in self.ACCESSORY_KEYWORDS.get("stands", []):
            if keyword in candidate_name and any(cat in product_category for cat in ["drum", "microphone", "amplifier"]):
                score += 0.6
        
        # Rule 2: Same brand, different category = often accessories
        if product.get("brand") == candidate.get("brand"):
            if candidate_category in ["accessories", "cables", "stands"]:
                score += 0.4
        
        # Rule 3: Candidate is explicitly in "accessories" category
        if candidate_category == "accessories":
            score += 0.5
        
        return min(score, 1.0)
    
    def _score_related(self, product: Dict, candidate: Dict) -> float:
        """
        Score how likely candidate is RELATED to the main product.
        
        Related products are things like:
        - Other keyboards in the same series
        - Different microphones in the same tier
        - Competing products in the same category
        """
        score = 0.0
        
        product_category = product.get("category", "").lower()
        candidate_category = candidate.get("category", "").lower()
        product_price = float(product.get("price", 0) or 0)
        candidate_price = float(candidate.get("price", 0) or 0)
        
        # Rule 1: Same category
        if product_category == candidate_category:
            score += 0.5
        
        # Rule 2: Similar price point (within 50%)
        if product_price > 0 and candidate_price > 0:
            price_ratio = min(product_price, candidate_price) / max(product_price, candidate_price)
            if price_ratio > 0.5:
                score += 0.3
        
        # Rule 3: Same category map
        for category_key, category_list in self.CATEGORY_SIMILARITIES.items():
            if any(cat in product_category for cat in category_list) and \
               any(cat in candidate_category for cat in category_list):
                score += 0.4
        
        # Rule 4: Same brand = strong signal for related
        if product.get("brand") == candidate.get("brand"):
            score += 0.4
        
        # Rule 5: Check if model names are similar (same series)
        product_model = product.get("model_name", "").lower()
        candidate_model = candidate.get("model_name", "").lower()
        if product_model and candidate_model:
            # Check for common prefixes (e.g., "Roland TR" = drums)
            words_product = set(product_model.split())
            words_candidate = set(candidate_model.split())
            if len(words_product & words_candidate) > 0:
                score += 0.3
        
        return min(score, 1.0)
    
    def export_relationships_map(self, output_path: str = None) -> Dict:
        """
        Exports the relationship graph as a JSON file for reference.
        """
        map_data = {
            "total_relationships": len(self.relationships),
            "by_type": {
                "necessity": len([r for r in self.relationships if r.relationship_type == "necessity"]),
                "accessory": len([r for r in self.relationships if r.relationship_type == "accessory"]),
                "related": len([r for r in self.relationships if r.relationship_type == "related"]),
            },
            "relationships": [asdict(r) for r in self.relationships]
        }
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(map_data, f, indent=2)
            logger.info(f"📊 Relationship map exported to {output_path}")
        
        return map_data
    
    def validate_relationships(self) -> tuple[int, int]:
        """Validates all relationships for consistency."""
        valid = 0
        invalid = 0
        
        for rel in self.relationships:
            source = self.all_products.get(rel.source_sku)
            related = self.all_products.get(rel.related_sku)
            
            if source and related and rel.confidence > 0.5:
                valid += 1
            else:
                invalid += 1
                logger.warning(f"Invalid relationship: {rel.source_sku} -> {rel.related_sku}")
        
        return valid, invalid
