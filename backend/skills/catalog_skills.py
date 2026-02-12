"""
Catalog Skills — Validation & Resolution

Two skills that plug into the SkillRegistry:
  - CatalogValidateSkill: Score products + catalog health
  - CatalogResolveSkill: Auto-fix missing data

These bridge the catalog_validator into the skill pipeline.
"""

import logging
from typing import Dict, Any, Tuple, List

from backend.skills.base_skill import BaseSkill
from backend.catalog_validator import (
    validate_product,
    validate_catalog,
    resolve_product,
    resolve_catalog,
)


class CatalogValidateSkill(BaseSkill):
    """
    Validate a single product or entire catalog.

    Context options:
      - {"product": dict}                → validate one product
      - {"products": [dict, ...]}        → validate full catalog
      - {"product": dict, "fix": True}   → validate + resolve one product
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        try:
            # Single product validation
            if "product" in context:
                product = context["product"]
                result = validate_product(product)

                # Optionally resolve
                if context.get("fix"):
                    catalog = context.get("catalog_products", [])
                    resolved, changes = resolve_product(product, catalog)
                    result["resolved"] = resolved
                    result["changes"] = changes
                    result["new_score"] = validate_product(resolved)["score"]

                self.log_execution(
                    True, "CatalogValidate",
                    f"{product.get('name', '?')} → {result['score']}/100 ({result['status']})"
                )
                return True, result

            # Full catalog validation
            if "products" in context:
                products = context["products"]
                health = validate_catalog(products)

                self.log_execution(
                    True, "CatalogValidate",
                    f"Catalog: {health['health_score']}/100 ({health['total_products']} products)"
                )
                return True, health

            return False, "Context must include 'product' or 'products'"

        except Exception as e:
            error_msg = f"Catalog validation failed: {str(e)}"
            self.log_execution(False, "CatalogValidate", error_msg)
            return False, error_msg


class CatalogResolveSkill(BaseSkill):
    """
    Resolve missing data across catalog using smart heuristics.

    Context:
      - {"products": [dict, ...]}   → resolve all products
      - {"product": dict, "catalog_products": [...]}  → resolve one with peer data
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        try:
            # Full catalog resolution
            if "products" in context:
                products = context["products"]
                resolved, summary = resolve_catalog(products)

                # Validate after resolution
                health_before = validate_catalog(products)
                health_after = validate_catalog(resolved)

                result = {
                    "resolved_products": resolved,
                    "summary": summary,
                    "health_before": health_before["health_score"],
                    "health_after": health_after["health_score"],
                    "improvement": health_after["health_score"] - health_before["health_score"],
                }

                self.log_execution(
                    True, "CatalogResolve",
                    f"Resolved {summary['products_improved']} products: "
                    f"{result['health_before']} → {result['health_after']}/100"
                )
                return True, result

            # Single product resolution
            if "product" in context:
                product = context["product"]
                catalog = context.get("catalog_products", [])
                resolved, changes = resolve_product(product, catalog)
                before = validate_product(product)["score"]
                after = validate_product(resolved)["score"]

                result = {
                    "resolved": resolved,
                    "changes": changes,
                    "score_before": before,
                    "score_after": after,
                    "improvement": after - before,
                }

                self.log_execution(
                    True, "CatalogResolve",
                    f"{product.get('name', '?')}: {before} → {after}/100 ({len(changes)} changes)"
                )
                return True, result

            return False, "Context must include 'product' or 'products'"

        except Exception as e:
            error_msg = f"Catalog resolution failed: {str(e)}"
            self.log_execution(False, "CatalogResolve", error_msg)
            return False, error_msg
