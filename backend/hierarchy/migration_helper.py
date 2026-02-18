"""
Hierarchy Migration Helper

Scripts to help migrate existing products to the new perfect hierarchy structure.
"""

from __future__ import annotations

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

from backend.hierarchy.service import HierarchyService
from backend.hierarchy.models import Product, ProductType
from backend.ingestion.taxonomy_manager import get_taxonomy_manager

logger = logging.getLogger("HierarchyMigration")


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug. Reuses HierarchyService logic."""
    if not text:
        return ""
    import re
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "other"


class HierarchyMigrationHelper:
    """
    Helper class for migrating existing products to the new hierarchy structure.
    """

    def __init__(self):
        self.hierarchy_service = HierarchyService()
        self.taxonomy_manager = get_taxonomy_manager()
        self.logger = logger

    def extract_categories_from_existing_products(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract all unique categories and subcategories from existing products.
        
        Returns:
            {
                "category_name": {
                    "subcategories": ["subcat1", "subcat2", ...],
                    "product_count": 10
                }
            }
        """
        categories = defaultdict(lambda: {"subcategories": set(), "product_count": 0})

        for product in products:
            taxonomy = product.get("taxonomy", {})
            category = taxonomy.get("canonical_category", "Uncategorized")
            subcategory = taxonomy.get("canonical_subcategory", "")

            categories[category]["subcategories"].add(subcategory)
            categories[category]["product_count"] += 1

        # Convert sets to lists
        result = {}
        for cat, data in categories.items():
            result[cat] = {
                "subcategories": sorted(list(data["subcategories"])),
                "product_count": data["product_count"]
            }

        return result

    def classify_all_products(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Classify all products into product types.
        
        Returns:
            {
                "product_id": {
                    "category": "...",
                    "sub_category": "...",
                    "product_type": "...",
                    "confidence": 0.95
                }
            }
        """
        classifications = {}

        for product in products:
            product_id = product.get("id") or product.get("halilit_id", "")
            product_name = product.get("product_name") or product.get("name", "")
            brand = product.get("brand", "")
            
            taxonomy = product.get("taxonomy", {})
            category = taxonomy.get("canonical_category", "Uncategorized")
            subcategory = taxonomy.get("canonical_subcategory", "")

            pricing = product.get("pricing", {})
            price = pricing.get("price_il", 0)

            # Classify product type
            product_type_id, confidence = self.hierarchy_service.classify_product_type(
                product_name=product_name,
                brand=brand,
                sub_category=subcategory,
                price=price,
                features=product.get("specifications", {})
            )

            classifications[product_id] = {
                "category": category,
                "sub_category": subcategory,
                "product_type": product_type_id,
                "confidence": confidence,
                "product_name": product_name,
                "brand": brand
            }

        return classifications

    def group_products_by_hierarchy(
        self,
        products: List[Dict[str, Any]],
        classifications: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Group products by their hierarchy path.
        
        Returns:
            {
                "category/subcategory/product_type/brand": {
                    "category": "...",
                    "sub_category": "...",
                    "product_type": "...",
                    "brand": "...",
                    "products": [...],
                    "families": {...}
                }
            }
        """
        groups = defaultdict(lambda: {
            "category": "",
            "sub_category": "",
            "product_type": "",
            "brand": "",
            "products": [],
            "families": defaultdict(list)
        })

        for product in products:
            product_id = product.get("id") or product.get("halilit_id", "")
            classification = classifications.get(product_id, {})

            if not classification:
                self.logger.warning(f"No classification for product {product_id}")
                continue

            category = classification["category"]
            sub_category = classification["sub_category"]
            product_type = classification["product_type"]
            brand = classification["brand"]

            # Create hierarchy key
            key = f"{category}/{sub_category}/{product_type}/{brand}"

            groups[key]["category"] = category
            groups[key]["sub_category"] = sub_category
            groups[key]["product_type"] = product_type
            groups[key]["brand"] = brand
            groups[key]["products"].append(product)

            # Group by family
            family_id = product.get("family_id")
            if family_id:
                groups[key]["families"][family_id].append(product)

        return dict(groups)

    def generate_migration_report(
        self,
        products: List[Dict[str, Any]],
        output_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive migration report.
        
        Returns:
            {
                "total_products": 1000,
                "categories_found": 10,
                "subcategories_found": 50,
                "product_types_needed": 30,
                "products_classified": 950,
                "products_unclassified": 50,
                "validation_errors": [...]
            }
        """
        # Extract categories
        categories_data = self.extract_categories_from_existing_products(products)

        # Classify products
        classifications = self.classify_all_products(products)

        # Count statistics
        total_products = len(products)
        products_classified = len(classifications)
        products_unclassified = total_products - products_classified

        # Count unique product types
        product_types = set()
        for classification in classifications.values():
            product_types.add(classification["product_type"])

        # Group by hierarchy
        groups = self.group_products_by_hierarchy(products, classifications)

        report = {
            "total_products": total_products,
            "categories_found": len(categories_data),
            "subcategories_found": sum(len(data["subcategories"]) for data in categories_data.values()),
            "product_types_needed": len(product_types),
            "products_classified": products_classified,
            "products_unclassified": products_unclassified,
            "classification_rate": products_classified / total_products if total_products > 0 else 0,
            "hierarchy_groups": len(groups),
            "categories": categories_data,
            "product_types": sorted(list(product_types)),
            "hierarchy_groups_sample": dict(list(groups.items())[:5]),  # Sample
        }

        # Save to file if requested
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Migration report saved to {output_file}")

        return report

    def validate_migration(
        self,
        migrated_products: List[Product]
    ) -> Dict[str, Any]:
        """
        Validate migrated products for completeness and correctness.
        
        Returns:
            {
                "total_validated": 1000,
                "valid": 950,
                "invalid": 50,
                "errors": [...]
            }
        """
        valid_count = 0
        invalid_count = 0
        errors = []

        for product in migrated_products:
            is_valid, product_errors = self.hierarchy_service.validate_product_hierarchy(product)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                errors.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "errors": product_errors
                })

        return {
            "total_validated": len(migrated_products),
            "valid": valid_count,
            "invalid": invalid_count,
            "error_rate": invalid_count / len(migrated_products) if migrated_products else 0,
            "errors": errors[:100]  # Limit to first 100 errors
        }


def main():
    """Example usage"""
    helper = HierarchyMigrationHelper()

    # Load existing products (example)
    # products = load_all_products()

    # Generate report
    # report = helper.generate_migration_report(products, Path("migration_report.json"))
    # print(json.dumps(report, indent=2))

    print("Hierarchy Migration Helper initialized")
    print("Use this module to help migrate existing products to the new hierarchy structure")


if __name__ == "__main__":
    main()
