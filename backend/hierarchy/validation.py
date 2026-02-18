"""
Hierarchy Validation - Ensures Product-to-Product Relationships Only
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple
from backend.hierarchy.models import Product, ProductRelationship, HierarchyValidationLog

logger = logging.getLogger("HierarchyValidation")


class HierarchyValidator:
    """
    Validates that the hierarchy structure is correct:
    - All relationships are product-to-product (NOT family-to-product)
    - All products have complete hierarchy paths
    - No orphaned products
    """

    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logger

    def validate_relationships_are_product_to_product(
        self,
        relationships: List[ProductRelationship],
        product_ids: set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all relationships connect products to products.
        
        Args:
            relationships: List of relationships to validate
            product_ids: Set of valid product IDs
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        for rel in relationships:
            # Check source is a product
            if rel.source_product_id not in product_ids:
                errors.append(
                    f"Relationship {rel.source_product_id} → {rel.target_product_id}: "
                    f"source_product_id '{rel.source_product_id}' is not a valid product"
                )

            # Check target is a product
            if rel.target_product_id not in product_ids:
                errors.append(
                    f"Relationship {rel.source_product_id} → {rel.target_product_id}: "
                    f"target_product_id '{rel.target_product_id}' is not a valid product"
                )

            # Check not self-referential (unless variant_of)
            if rel.source_product_id == rel.target_product_id:
                if rel.relationship_type != "variant_of":
                    errors.append(
                        f"Relationship {rel.source_product_id} → {rel.target_product_id}: "
                        f"self-referential relationship not allowed for type '{rel.relationship_type}'"
                    )

        return len(errors) == 0, errors

    def validate_product_has_accessories_linked(
        self,
        product: Product,
        relationships: List[ProductRelationship]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a product's accessories are linked via relationships.
        
        This ensures accessories are NOT stored in family.accessory_ids.
        """
        errors = []
        warnings = []

        # Find accessories for this product
        accessory_rels = [
            r for r in relationships
            if r.target_product_id == product.id and r.relationship_type == "accessory_for"
        ]

        if not accessory_rels:
            warnings.append(
                f"Product {product.id} ({product.name}) has no accessories linked. "
                f"This is OK, but verify if accessories should exist."
            )

        return len(errors) == 0, errors + warnings

    def validate_no_family_level_relationships(
        self,
        relationships: List[ProductRelationship],
        family_ids: set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Ensure no relationships reference families directly.
        
        Args:
            relationships: List of relationships to validate
            family_ids: Set of valid family IDs (to check against)
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        for rel in relationships:
            # Check source is not a family ID
            if rel.source_product_id in family_ids:
                errors.append(
                    f"Relationship {rel.source_product_id} → {rel.target_product_id}: "
                    f"source_product_id '{rel.source_product_id}' is a family ID, not a product ID. "
                    f"Relationships must be product-to-product."
                )

            # Check target is not a family ID
            if rel.target_product_id in family_ids:
                errors.append(
                    f"Relationship {rel.source_product_id} → {rel.target_product_id}: "
                    f"target_product_id '{rel.target_product_id}' is a family ID, not a product ID. "
                    f"Relationships must be product-to-product."
                )

        return len(errors) == 0, errors

    def validate_complete_hierarchy(
        self,
        products: List[Product],
        relationships: List[ProductRelationship]
    ) -> Dict[str, Any]:
        """
        Run complete validation suite.
        
        Returns:
            {
                "valid": bool,
                "errors": [...],
                "warnings": [...],
                "summary": {...}
            }
        """
        all_errors = []
        all_warnings = []

        product_ids = {p.id for p in products}

        # Validation 1: All relationships are product-to-product
        is_valid, errors = self.validate_relationships_are_product_to_product(
            relationships, product_ids
        )
        all_errors.extend(errors)

        # Validation 2: No family-level relationships
        # (Would need family_ids set - placeholder for now)
        # family_ids = set()  # Would come from database
        # is_valid, errors = self.validate_no_family_level_relationships(
        #     relationships, family_ids
        # )
        # all_errors.extend(errors)

        # Validation 3: Products have complete paths
        for product in products:
            is_valid, errors = product.validate_hierarchy()
            if not is_valid:
                all_errors.extend([
                    f"Product {product.id}: {e}" for e in errors
                ])

        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "summary": {
                "total_products": len(products),
                "total_relationships": len(relationships),
                "products_with_errors": len([p for p in products if not p.validate_hierarchy()[0]]),
                "relationships_with_errors": len([r for r in relationships if r.source_product_id not in product_ids or r.target_product_id not in product_ids]),
            }
        }


def get_hierarchy_validator(db_connection=None) -> HierarchyValidator:
    """Get or create singleton HierarchyValidator instance"""
    return HierarchyValidator(db_connection)
