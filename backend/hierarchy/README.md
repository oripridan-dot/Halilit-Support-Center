# Perfect Hierarchy Module

## Overview

This module implements the complete hierarchical product structure:

```
Category → Sub Category → Product Type → Brand → Family/Series → Products
                                                                    ↓
                                              Product Relationships (Product-to-Product)
                                              ├─ Accessories → Products
                                              └─ Related Products → Products
```

## Critical Design Decision

**Accessories and Related Products connect DIRECTLY to individual Products, NOT to Families/Series.**

### Example

```
Family: "Nord Stage 4"
  ├─ Product: "Nord Stage 4 88"
  │  ├─ Accessory: "Soft Case for Stage 4 88" (via product_relationships)
  │  └─ Related: "Nord Stage 3 88" (via product_relationships)
  ├─ Product: "Nord Stage 4 73"
  │  └─ Accessory: "Soft Case for Stage 4 73" (via product_relationships)
  └─ Product: "Nord Stage 4 Compact"
     └─ Accessory: "Soft Case for Stage 4 Compact" (via product_relationships)
```

**Why Product-to-Product?**
- Each product variant may have different accessories (e.g., 88-key vs 73-key cases)
- More precise matching
- Better user experience (shows exact compatible accessories)
- Easier to maintain and validate

## Database Schema

### Products Table
- Each product has a complete hierarchy path
- Products belong to a family (optional)
- Products have relationships via `product_relationships` table

### Product Relationships Table
- **source_product_id**: The accessory/related product
- **target_product_id**: The main product
- **relationship_type**: 'accessory_for', 'related_to', 'variant_of', etc.
- **relationship_level**: 'direct' (same family) or 'indirect' (different family/brand)

### Product Families Table
- **NO accessory_ids field** - accessories are NOT stored here
- Families only contain variant_ids (the products in the family)
- Accessories are linked via product_relationships table

## Usage

### Get Accessories for a Product

```python
from backend.hierarchy.service import get_hierarchy_service

service = get_hierarchy_service()

# Get all accessories for a specific product
product_id = "nord-stage-4-88"
accessories = service.get_accessories_for_product(product_id)
```

### Create Product Relationship

```python
from backend.hierarchy.models import ProductRelationship

# Link an accessory to a product
relationship = ProductRelationship(
    source_product_id="soft-case-stage-4-88",
    target_product_id="nord-stage-4-88",
    relationship_type="accessory_for",
    relationship_level="direct",
    confidence=0.95,
    manually_curated=True
)
```

## Migration Notes

When migrating existing data:
1. **Remove family-level accessory references** - if any exist
2. **Create product-to-product relationships** for all accessories
3. **Validate** that no relationships reference families
4. **Update queries** to use product_relationships table instead of family.accessory_ids

## Validation

The validation system ensures:
- ✅ All relationships are product-to-product
- ✅ No relationships reference families directly
- ✅ All source and target products exist
- ✅ Relationships are properly classified
