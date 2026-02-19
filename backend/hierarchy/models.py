"""
Perfect Hierarchy Models - v1.0

Implements the complete hierarchical structure:
Category → Sub Category → Product Type → Brand → Family → Products
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 1: CATEGORY
# ═══════════════════════════════════════════════════════════════════════════

class Category(BaseModel):
    """Top-level product category"""
    id: str = Field(description="Unique category ID (slug)")
    name: str = Field(description="Category name (e.g., 'Keyboards & Synthesizers')")
    description: Optional[str] = None
    display_order: int = Field(default=100)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_slug(self) -> str:
        """Convert name to URL-safe slug"""
        return self.id.lower().replace(" ", "-")


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 2: SUB CATEGORY
# ═══════════════════════════════════════════════════════════════════════════

class SubCategory(BaseModel):
    """Subcategory within a category"""
    id: str = Field(description="Unique subcategory ID (slug)")
    category_id: str = Field(description="Parent category ID")
    name: str = Field(description="Subcategory name (e.g., 'Digital Keyboard')")
    description: Optional[str] = None
    display_order: int = Field(default=100)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_slug(self) -> str:
        """Convert name to URL-safe slug"""
        return self.id.lower().replace(" ", "-")


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 3: PRODUCT TYPE (NEW LEVEL)
# ═══════════════════════════════════════════════════════════════════════════

class ProductType(BaseModel):
    """Product type within a subcategory"""
    id: str = Field(description="Unique product type ID (slug)")
    sub_category_id: str = Field(description="Parent subcategory ID")
    name: str = Field(description="Product type name (e.g., 'Stage Keyboard')")
    description: Optional[str] = None
    display_order: int = Field(default=100)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_slug(self) -> str:
        """Convert name to URL-safe slug"""
        return self.id.lower().replace(" ", "-")


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 4: BRAND
# ═══════════════════════════════════════════════════════════════════════════

class Brand(BaseModel):
    """Product brand"""
    id: str = Field(description="Unique brand ID (slug)")
    name: str = Field(description="Brand name (e.g., 'Nord')")
    slug: str = Field(description="URL-safe slug")
    logo_url: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 5: PRODUCT FAMILY
# ═══════════════════════════════════════════════════════════════════════════

class ProductFamily(BaseModel):
    """
    Product family/series within a brand.
    
    Example: "Stage" is a family/series. Models like "Stage 3", "Stage 4", "Stage 5" belong to this family.
    
    NOTE: Accessories and related products are NOT stored here.
    They are linked directly to individual products via product_relationships table.
    """
    id: str = Field(description="Unique family ID")
    brand_id: str = Field(description="Parent brand ID")
    product_type_id: str = Field(description="Product type ID")
    family_name: str = Field(description="Family/series name (e.g., 'Stage')")
    series: Optional[str] = None  # Same as family_name for compatibility
    generation: Optional[int] = None  # Deprecated - use model_number in ProductModel
    product_line: Optional[str] = None
    official_family_url: Optional[str] = None
    description: Optional[str] = None
    hero_image: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 6: PRODUCT MODEL (NEW LEVEL)
# ═══════════════════════════════════════════════════════════════════════════

class ProductModel(BaseModel):
    """
    Product model/generation within a family.
    
    Example: "Stage 4" is a model within the "Stage" family.
    Variants like "88", "73", "Compact" belong to this model.
    """
    id: str = Field(description="Unique model ID")
    family_id: str = Field(description="Parent family ID")
    model_name: str = Field(description="Model name (e.g., 'Stage 4')")
    model_number: Optional[int] = Field(default=None, description="Model number (e.g., 3, 4, 5)")
    generation: Optional[int] = Field(default=None, description="Same as model_number, for compatibility")
    description: Optional[str] = None
    official_model_url: Optional[str] = None
    hero_image: Optional[str] = None
    release_year: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL 7: PRODUCT/VARIANT (with complete hierarchy path)
# ═══════════════════════════════════════════════════════════════════════════

class ProductHierarchy(BaseModel):
    """Complete hierarchy path for a product variant"""
    category_id: str
    category_name: str
    sub_category_id: str
    sub_category_name: str
    product_type_id: str
    product_type_name: str
    brand_id: str
    brand_name: str
    family_id: str
    family_name: str
    model_id: Optional[str] = None
    model_name: Optional[str] = None
    model_number: Optional[int] = None

    def to_path(self) -> str:
        """Generate hierarchy path string"""
        parts = [
            self.category_id.lower().replace(" ", "-"),
            self.sub_category_id.lower().replace(" ", "-"),
            self.product_type_id.lower().replace(" ", "-"),
            self.brand_id.lower().replace(" ", "-"),
            self.family_id.lower().replace(" ", "-"),
        ]
        if self.model_id:
            parts.append(self.model_id.lower().replace(" ", "-"))
        return "/".join(parts)


class Product(BaseModel):
    """
    Product variant with complete hierarchy.
    
    Example: "Nord Stage 4 88" is a variant:
    - Family: "Stage"
    - Model: "Stage 4"
    - Variant: "88"
    """
    id: str = Field(description="Unique product ID")
    model_id: Optional[str] = Field(default=None, description="Parent model ID")
    family_id: Optional[str] = Field(default=None, description="Parent family ID (denormalized)")
    product_type_id: str = Field(description="Product type ID")
    brand_id: str = Field(description="Brand ID")
    sub_category_id: str = Field(description="Subcategory ID")
    category_id: str = Field(description="Category ID")
    
    # Product Identity
    name: str
    sku: Optional[str] = None
    halilit_id: Optional[str] = None
    variant_key: Optional[str] = Field(default=None, description="Variant key (e.g., '88', '73', 'Compact')")
    
    # Full product data (preserves all existing fields)
    product_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Hierarchy Path (denormalized)
    hierarchy_path: str = Field(description="Complete hierarchy path including model")
    
    # Validation
    hierarchy_validated: bool = Field(default=False)
    validation_errors: List[str] = Field(default_factory=list)
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def get_hierarchy(self) -> ProductHierarchy:
        """Extract hierarchy from product data or IDs"""
        # This would be populated from joins in actual implementation
        return ProductHierarchy(
            category_id=self.category_id,
            category_name=self.product_data.get("category_name", ""),
            sub_category_id=self.sub_category_id,
            sub_category_name=self.product_data.get("sub_category_name", ""),
            product_type_id=self.product_type_id,
            product_type_name=self.product_data.get("product_type_name", ""),
            brand_id=self.brand_id,
            brand_name=self.product_data.get("brand_name", ""),
            family_id=self.family_id or "",
            family_name=self.product_data.get("family_name", ""),
            model_id=self.model_id,
            model_name=self.product_data.get("model_name"),
            model_number=self.product_data.get("model_number"),
        )

    def validate_hierarchy(self) -> tuple[bool, List[str]]:
        """Validate that product has complete hierarchy path"""
        errors = []
        
        if not self.category_id:
            errors.append("Missing category_id")
        if not self.sub_category_id:
            errors.append("Missing sub_category_id")
        if not self.product_type_id:
            errors.append("Missing product_type_id")
        if not self.brand_id:
            errors.append("Missing brand_id")
        if not self.family_id:
            errors.append("Missing family_id")
        if not self.model_id:
            errors.append("Missing model_id")
        if not self.hierarchy_path:
            errors.append("Missing hierarchy_path")
        
        return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════
# RELATIONSHIPS (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════

class RelationshipLevel(str):
    """Relationship level classification"""
    DIRECT = "direct"      # Same family
    INDIRECT = "indirect"  # Different family/brand


class ProductRelationship(BaseModel):
    """
    Product-to-product relationship.
    
    CRITICAL: Relationships connect PRODUCTS to PRODUCTS, not families.
    - Accessories link directly to individual products (e.g., "Soft Case for Nord Stage 4 88")
    - Related products link directly to individual products
    - Variants link to other variants in the same family
    
    Example:
        source_product_id: "soft-case-stage-4-88" (accessory)
        target_product_id: "nord-stage-4-88" (main product)
        relationship_type: "accessory_for"
    """
    source_product_id: str = Field(description="Source product ID (e.g., accessory)")
    target_product_id: str = Field(description="Target product ID (e.g., main product)")
    relationship_type: str = Field(description="'accessory_for', 'related_to', 'variant_of', 'successor_of', 'alternative_to', 'bundle_with'")
    relationship_level: str = Field(default="direct", description="'direct' = same family, 'indirect' = different family/brand")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    ai_discovered: bool = Field(default=True)
    manually_curated: bool = Field(default=False)
    compatibility_notes: Optional[str] = None
    discovered_from: Optional[str] = None
    sources_verified: List[str] = Field(default_factory=list)
    bidirectional: bool = Field(default=False)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

class ValidationSeverity(str):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class HierarchyValidationLog(BaseModel):
    """Validation log entry"""
    id: Optional[str] = None
    product_id: Optional[str] = None
    validation_type: str  # 'missing_path', 'orphan', 'duplicate', 'invalid_level'
    severity: str  # 'error', 'warning', 'info'
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = Field(default=False)
    resolved_at: Optional[str] = None
    created_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETE HIERARCHY VIEW (for API responses)
# ═══════════════════════════════════════════════════════════════════════════

class CompleteHierarchy(BaseModel):
    """Complete hierarchy tree structure"""
    category: Category
    sub_categories: List[SubCategory] = Field(default_factory=list)
    product_types: List[ProductType] = Field(default_factory=list)
    brands: List[Brand] = Field(default_factory=list)
    families: List[ProductFamily] = Field(default_factory=list)
    models: List[ProductModel] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)


class HierarchyPath(BaseModel):
    """Represents a complete path through the hierarchy"""
    category: str
    sub_category: str
    product_type: str
    brand: str
    family: str
    model: Optional[str] = None

    def to_string(self) -> str:
        """Convert to path string"""
        parts = [
            self.category.lower().replace(" ", "-"),
            self.sub_category.lower().replace(" ", "-"),
            self.product_type.lower().replace(" ", "-"),
            self.brand.lower().replace(" ", "-"),
            self.family.lower().replace(" ", "-"),
        ]
        if self.model:
            parts.append(self.model.lower().replace(" ", "-"))
        return "/".join(parts)

    @classmethod
    def from_string(cls, path_string: str) -> "HierarchyPath":
        """Parse path string into HierarchyPath"""
        parts = path_string.split("/")
        if len(parts) < 5:
            raise ValueError(f"Invalid path string: {path_string} (need at least 5 parts)")
        
        return cls(
            category=parts[0].replace("-", " ").title(),
            sub_category=parts[1].replace("-", " ").title(),
            product_type=parts[2].replace("-", " ").title(),
            brand=parts[3].replace("-", " ").title(),
            family=parts[4].replace("-", " ").title(),
            model=parts[5].replace("-", " ").title() if len(parts) > 5 else None,
        )
