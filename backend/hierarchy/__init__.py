"""
Perfect Hierarchy Module

Implements the complete hierarchical product structure:
Category → Sub Category → Product Type → Brand → Family → Products
"""

from backend.hierarchy.models import (
    Category,
    SubCategory,
    ProductType,
    Brand,
    ProductFamily,
    ProductModel,
    Product,
    ProductHierarchy,
    HierarchyPath,
    ProductRelationship,
    HierarchyValidationLog,
    CompleteHierarchy,
)

from backend.hierarchy.service import (
    HierarchyService,
    get_hierarchy_service,
)

from backend.hierarchy.migration_helper import (
    HierarchyMigrationHelper,
)

__all__ = [
    # Models
    "Category",
    "SubCategory",
    "ProductType",
    "Brand",
    "ProductFamily",
    "ProductModel",
    "Product",
    "ProductHierarchy",
    "HierarchyPath",
    "ProductRelationship",
    "HierarchyValidationLog",
    "CompleteHierarchy",
    # Services
    "HierarchyService",
    "get_hierarchy_service",
    # Migration
    "HierarchyMigrationHelper",
]
