"""
Perfect Hierarchy Service - v1.0

Service layer for managing the complete product hierarchy:
Category → Sub Category → Product Type → Brand → Family → Products
"""

from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from backend.hierarchy.models import (
    Category, SubCategory, ProductType, Brand, ProductFamily,
    Product, ProductHierarchy, HierarchyPath, HierarchyValidationLog
)

logger = logging.getLogger("HierarchyService")


class HierarchyService:
    """
    Manages the complete product hierarchy structure.
    
    Responsibilities:
    - Build and maintain hierarchy levels
    - Validate product paths
    - Classify products into hierarchy
    - Generate hierarchy paths
    """

    def __init__(self, db_connection=None):
        """
        Initialize hierarchy service.
        
        Args:
            db_connection: Database connection (will be injected)
        """
        self.db = db_connection
        self.logger = logger

    # ═══════════════════════════════════════════════════════════════════════
    # PATH GENERATION
    # ═══════════════════════════════════════════════════════════════════════

    def generate_hierarchy_path(
        self,
        category_id: str,
        sub_category_id: str,
        product_type_id: str,
        brand_id: str,
        family_id: str,
        model_id: Optional[str] = None
    ) -> str:
        """
        Generate hierarchy path string from IDs.
        
        Format: category-slug/subcategory-slug/product-type-slug/brand-slug/family-slug/model-slug
        
        Example: keyboards-synthesizers/digital-keyboard/stage-keyboard/nord/stage/stage-4
        """
        parts = [
            self._slugify(category_id),
            self._slugify(sub_category_id),
            self._slugify(product_type_id),
            self._slugify(brand_id),
            self._slugify(family_id),
        ]
        
        if model_id:
            parts.append(self._slugify(model_id))
        
        return "/".join(parts)

    def parse_hierarchy_path(self, path: str) -> HierarchyPath:
        """Parse hierarchy path string into HierarchyPath object"""
        return HierarchyPath.from_string(path)

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug"""
        if not text:
            return ""
        return text.lower().replace(" ", "-").replace("_", "-")

    # ═══════════════════════════════════════════════════════════════════════
    # PRODUCT TYPE CLASSIFICATION
    # ═══════════════════════════════════════════════════════════════════════

    def classify_product_type(
        self,
        product_name: str,
        brand: str,
        sub_category: str,
        price: Optional[float] = None,
        features: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, float]:
        """
        Classify a product into a product type.
        
        Returns: (product_type_id, confidence)
        """
        if features is None:
            features = {}
        
        product_name_lower = product_name.lower()
        brand_lower = brand.lower()
        sub_category_lower = sub_category.lower()

        # Rule 1: Brand + Series Pattern Matching
        brand_patterns = {
            "nord": {
                "stage": "stage-keyboard",
                "piano": "digital-piano",
                "lead": "synthesizer",
                "electro": "organ-keyboard",
                "grand": "digital-piano",
            },
            "roland": {
                "fantom": "workstation",
                "juno": "synthesizer",
                "jupiter": "synthesizer",
                "fp-": "digital-piano",
                "rd-": "stage-piano",
                "v-drum": "electronic-drum-system",
                "td-": "electronic-drum-system",
            },
            "moog": {
                "minimoog": "analog-synthesizer",
                "sub": "analog-synthesizer",
                "matriarch": "analog-synthesizer",
                "one": "analog-synthesizer",
            },
        }

        if brand_lower in brand_patterns:
            for pattern, product_type in brand_patterns[brand_lower].items():
                if pattern.lower() in product_name_lower:
                    return product_type, 0.95

        # Rule 2: Subcategory + Feature Analysis
        if "piano" in sub_category_lower or "piano" in product_name_lower:
            if features.get("weighted_keys") or "weighted" in product_name_lower:
                return "digital-piano", 0.90
            return "stage-piano", 0.85

        if "synthesizer" in sub_category_lower or "synth" in product_name_lower:
            if features.get("analog") or "analog" in product_name_lower:
                return "analog-synthesizer", 0.90
            return "digital-synthesizer", 0.85

        if "keyboard" in sub_category_lower:
            if "stage" in product_name_lower:
                return "stage-keyboard", 0.90
            if "workstation" in product_name_lower:
                return "workstation", 0.90
            return "portable-keyboard", 0.80

        if "drum" in sub_category_lower:
            if "electronic" in product_name_lower or "e-drum" in product_name_lower:
                return "electronic-drum-system", 0.90
            return "acoustic-drum-kit", 0.85

        # Rule 3: Price Tier Analysis
        if price:
            if price > 5000:
                return "professional", 0.70
            elif price > 2000:
                return "prosumer", 0.70
            elif price > 1000:
                return "standard", 0.70
            else:
                return "entry-level", 0.70

        # Default fallback
        return "general", 0.50

    # ═══════════════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════════════

    def validate_product_hierarchy(self, product: Product) -> Tuple[bool, List[str]]:
        """
        Validate that a product has a complete hierarchy path.
        
        Returns: (is_valid, list_of_errors)
        """
        errors = []

        # Check all required fields
        if not product.category_id:
            errors.append("Missing category_id")
        if not product.sub_category_id:
            errors.append("Missing sub_category_id")
        if not product.product_type_id:
            errors.append("Missing product_type_id")
        if not product.brand_id:
            errors.append("Missing brand_id")
        if not product.family_id:
            errors.append("Missing family_id")
        if not product.model_id:
            errors.append("Missing model_id")
        if not product.hierarchy_path:
            errors.append("Missing hierarchy_path")

        # Validate path matches IDs
        if product.hierarchy_path:
            try:
                parsed_path = self.parse_hierarchy_path(product.hierarchy_path)
                if parsed_path.category.lower() != self._slugify(product.category_id):
                    errors.append(f"Path category mismatch: {parsed_path.category} != {product.category_id}")
                if parsed_path.brand.lower() != self._slugify(product.brand_id):
                    errors.append(f"Path brand mismatch: {parsed_path.brand} != {product.brand_id}")
                if parsed_path.family.lower() != self._slugify(product.family_id):
                    errors.append(f"Path family mismatch: {parsed_path.family} != {product.family_id}")
                if product.model_id and parsed_path.model:
                    if parsed_path.model.lower() != self._slugify(product.model_id):
                        errors.append(f"Path model mismatch: {parsed_path.model} != {product.model_id}")
            except Exception as e:
                errors.append(f"Invalid hierarchy_path format: {e}")

        return len(errors) == 0, errors

    def find_orphaned_products(self) -> List[Product]:
        """Find products that don't fit into the hierarchy"""
        # This would query the database in actual implementation
        # For now, return empty list
        return []

    def find_duplicate_products(self) -> List[Tuple[Product, Product]]:
        """Find duplicate products (same halilit_id or very similar)"""
        # This would query the database in actual implementation
        return []

    # ═══════════════════════════════════════════════════════════════════════
    # HIERARCHY BUILDING
    # ═══════════════════════════════════════════════════════════════════════

    def build_complete_hierarchy(
        self,
        category_id: Optional[str] = None,
        sub_category_id: Optional[str] = None,
        product_type_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build complete hierarchy tree.
        
        Returns nested structure with all levels populated.
        """
        # This would query the database and build the tree
        # For now, return placeholder structure
        return {
            "categories": [],
            "sub_categories": [],
            "product_types": [],
            "brands": [],
            "families": [],
            "products": [],
        }

    def get_products_by_path(
        self,
        category: str,
        sub_category: str,
        product_type: str,
        brand: str,
        family: str,
        model: Optional[str] = None
    ) -> List[Product]:
        """
        Get all products matching a hierarchy path.
        
        Args:
            category: Category slug
            sub_category: Subcategory slug
            product_type: Product type slug
            brand: Brand slug
            family: Family slug (e.g., "stage")
            model: Optional model slug (e.g., "stage-4")
        
        Returns:
            List of products/variants matching the path
        """
        path = HierarchyPath(
            category=category,
            sub_category=sub_category,
            product_type=product_type,
            brand=brand,
            family=family,
            model=model
        )
        
        path_string = path.to_string()
        
        # This would query: SELECT * FROM products WHERE hierarchy_path = path_string
        # For now, return empty list
        return []

    def get_accessories_for_product(self, product_id: str) -> List[Product]:
        """
        Get all accessories for a specific product.
        
        CRITICAL: Accessories link directly to products, NOT families.
        
        Args:
            product_id: The product ID to get accessories for
        
        Returns:
            List of accessory products
        """
        # This would query:
        # SELECT p.* FROM products p
        # JOIN product_relationships pr ON pr.source_product_id = p.id
        # WHERE pr.target_product_id = product_id
        #   AND pr.relationship_type = 'accessory_for'
        # For now, return empty list
        return []

    def get_related_products(self, product_id: str) -> List[Product]:
        """
        Get all related products for a specific product.
        
        CRITICAL: Related products link directly to products, NOT families.
        
        Args:
            product_id: The product ID to get related products for
        
        Returns:
            List of related products
        """
        # This would query:
        # SELECT p.* FROM products p
        # JOIN product_relationships pr ON (
        #   (pr.source_product_id = p.id AND pr.target_product_id = product_id) OR
        #   (pr.target_product_id = p.id AND pr.source_product_id = product_id)
        # )
        # WHERE pr.relationship_type IN ('related_to', 'successor_of', 'alternative_to', 'bundle_with')
        # For now, return empty list
        return []

    # ═══════════════════════════════════════════════════════════════════════
    # MIGRATION HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    def migrate_product_to_hierarchy(
        self,
        existing_product: Dict[str, Any],
        category_id: str,
        sub_category_id: str,
        product_type_id: str,
        brand_id: str,
        family_id: str,
        model_id: str
    ) -> Product:
        """
        Migrate an existing product to the new hierarchy structure.
        
        Args:
            existing_product: Existing product dict (from old structure)
            category_id: Category ID
            sub_category_id: Subcategory ID
            product_type_id: Product type ID
            brand_id: Brand ID
            family_id: Family ID (e.g., "stage")
            model_id: Model ID (e.g., "stage-4")
        
        Returns:
            New Product object with complete hierarchy
        """
        # Generate hierarchy path
        hierarchy_path = self.generate_hierarchy_path(
            category_id=category_id,
            sub_category_id=sub_category_id,
            product_type_id=product_type_id,
            brand_id=brand_id,
            family_id=family_id,
            model_id=model_id
        )

        # Build new product
        product = Product(
            id=existing_product.get("id") or existing_product.get("halilit_id", ""),
            model_id=model_id,
            family_id=family_id,  # Denormalized for fast queries
            product_type_id=product_type_id,
            brand_id=brand_id,
            sub_category_id=sub_category_id,
            category_id=category_id,
            name=existing_product.get("name") or existing_product.get("product_name", ""),
            sku=existing_product.get("sku"),
            halilit_id=existing_product.get("halilit_id"),
            variant_key=existing_product.get("variant_key"),
            product_data=existing_product,  # Preserve all existing data
            hierarchy_path=hierarchy_path,
            hierarchy_validated=False,
            validation_errors=[],
        )

        # Validate
        is_valid, errors = self.validate_product_hierarchy(product)
        if not is_valid:
            product.validation_errors = errors
            product.hierarchy_validated = False
        else:
            product.hierarchy_validated = True

        return product


# Singleton instance
_hierarchy_service = None


def get_hierarchy_service(db_connection=None) -> HierarchyService:
    """Get or create singleton HierarchyService instance"""
    global _hierarchy_service
    if _hierarchy_service is None:
        _hierarchy_service = HierarchyService(db_connection)
    return _hierarchy_service
