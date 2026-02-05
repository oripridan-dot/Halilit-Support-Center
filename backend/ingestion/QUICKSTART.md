# INGESTION PIPELINE - QUICK START GUIDE v6.0

## 30-Second Overview

The new ingestion pipeline has **4 engines** that work together:

```
Taxonomy Manager  ← Classifies products into categories
Pricing Engine    ← Handles pricing tiers and rules
Display Engine    ← Prepares visual presentation
Orchestrator      ← Runs the 6-phase pipeline
```

All connected through a **single unified data model**: `IngestionProductDraft`

---

## Installation & Setup

### 1. Import what you need

```python
from backend.ingestion import (
    get_ingestion_orchestrator,
    get_taxonomy_manager,
    get_pricing_engine,
    get_display_engine,
)
```

### 2. Get the singleton instances

```python
orchestrator = get_ingestion_orchestrator()
taxonomy = get_taxonomy_manager()
pricing = get_pricing_engine()
display = get_display_engine()
```

---

## The 6-Phase Pipeline

```python
# Phase 1: HARVEST
raw_data = {
    "name": "Nord Lead A1",
    "price_il": 14500,
    "price_eilat": 12325,
}

# Phase 2-6: Let the orchestrator handle it
report = orchestrator.ingest_batch(
    brand="Nord",
    raw_products=[raw_data],
)

# Results
for product in report.approved_products:
    print(f"✓ {product.product_name}")
    print(f"  Category: {product.taxonomy.canonical_category}")
    print(f"  Tier: {product.pricing.tier.value}")
    print(f"  Display: {product.display.display_role.value}")
```

---

## Common Tasks

### Task 1: Classify a Product by Name

```python
taxonomy = get_taxonomy_manager()

category, subcategory, confidence = taxonomy.classify_product(
    product_name="Moog Sub 37",
    brand="Moog",
    description="Three-oscillator analog synth",
)

print(f"✓ {category} > {subcategory} ({confidence:.0%})")
# Output: Keyboards & Synthesizers > Moog Synthesizer (98%)
```

### Task 2: Determine Pricing Tier

```python
pricing = get_pricing_engine()

# From a price
tier = pricing.determine_tier_by_price(2500)
# Returns: PricingTier.PRO

# Get tier label
label = pricing.get_tier_label(tier)
# Returns: "Professional"

# Get tier color
color = pricing.get_tier_color(tier)
# Returns: "bg-purple-100"
```

### Task 3: Validate Pricing

```python
pricing = get_pricing_engine()

pricing_data = PricingData(
    price_il=10000,
    price_eilat=8500,
)

is_valid, errors = pricing.validate_pricing(pricing_data)

if is_valid:
    print("✓ Pricing is valid")
else:
    for error in errors:
        print(f"✗ {error}")
```

### Task 4: Determine Display Role

```python
display = get_display_engine()

role = display.determine_display_role(
    product_name="Nord Grand",
    pricing_tier=PricingTier.PRO,
    data_completeness=0.85,
    is_official_spec=True,
    is_flagship_product=False,
)

print(f"Display as: {role.value}")
# Output: "cornerstone"
```

### Task 5: Get All Categories

```python
taxonomy = get_taxonomy_manager()

# Get all main categories
categories = taxonomy.get_all_categories()
# Returns: ["Keyboards & Synthesizers", "Drums & Percussion", ...]

# Get subcategories
subcats = taxonomy.get_subcategories("Keyboards & Synthesizers")
# Returns: ["Synthesizer", "Digital Keyboard", "Digital Piano", ...]
```

---

## Data Model: `IngestionProductDraft`

This is THE object that flows through the entire pipeline.

```python
from backend.ingestion import IngestionProductDraft

product = IngestionProductDraft(
    # Identity (Required)
    halilit_id="nord_001",
    product_name="Nord Lead A1",
    brand="Nord",

    # Taxonomy (Set by Phase 2)
    taxonomy=TaxonomyMapping(
        canonical_category="Keyboards & Synthesizers",
        canonical_subcategory="Nord Keyboard",
    ),

    # Pricing (Set by Phase 3)
    pricing=PricingData(
        price_il=14500,
        price_eilat=12325,
        tier=PricingTier.PRO,
    ),

    # Display (Set by Phase 4)
    display=DisplayProperties(
        display_role=DisplayRole.CORNERSTONE,
        display_tier_level=4,
        hero_image="https://...",
    ),

    # Other fields populated as needed
)
```

---

## Enums Reference

### PricingTier

```python
PricingTier.ENTRY      # < 500 NIS
PricingTier.MID        # 500-1,500 NIS
PricingTier.PRO        # 1,500-4,000 NIS
PricingTier.FLAGSHIP   # > 4,000 NIS
PricingTier.LEGACY     # Discontinued
```

### DisplayRole

```python
DisplayRole.HERO         # ⭐ Flagship/signature
DisplayRole.CORNERSTONE  # 💎 Key product in tier
DisplayRole.SPECIALIST   # 🎯 Niche product
DisplayRole.ENTRY        # 🎁 Gateway product
DisplayRole.HIDDEN       # 🚫 Internal/archived
```

### IngestionStatus

```python
IngestionStatus.HARVESTED       # Raw data extracted
IngestionStatus.ENRICHED        # Taxonomy applied
IngestionStatus.VALIDATED       # Passed validation
IngestionStatus.APPROVED        # Ready for display
IngestionStatus.REJECTED        # Failed validation
IngestionStatus.ARCHIVED        # Historical
```

### DataSourceConfidence

```python
DataSourceConfidence.OFFICIAL    # 1.0 - Manufacturer
DataSourceConfidence.TRUSTED     # 0.95 - Verified third party
DataSourceConfidence.COMMERCIAL  # 0.9 - Retailer (Halilit)
DataSourceConfidence.USER        # 0.7 - Community/reviews
DataSourceConfidence.INFERRED    # 0.6 - Computed
```

---

## Integration with Trinity Agents

```python
# In your agent workflow:
from backend.ingestion import get_ingestion_orchestrator

orchestrator = get_ingestion_orchestrator()

# CommercialScout harvests raw data
raw_products = commercial_scout.harvest(brand="Nord")

# Send to ingestion pipeline
report = orchestrator.ingest_batch("Nord", raw_products)

# Check results
approved_count = report.approved_count
for product in report.approved_products:
    # Use approved products downstream
    print(product.halilit_id, product.product_name, product.pricing.tier)

# Log any issues
for product, errors in report.rejected_products:
    print(f"Rejected: {product.product_name}")
    for error in errors:
        print(f"  - {error}")
```

---

## Common Configurations

### Custom Tier Boundaries

In `pricing_engine.py`:

```python
self.tier_boundaries = {
    PricingTier.ENTRY: (0, 500),
    PricingTier.MID: (500, 1500),
    PricingTier.PRO: (1500, 4000),
    PricingTier.FLAGSHIP: (4000, float('inf')),
}
```

### Custom Eilat Discount

In `pricing_engine.py`:

```python
self.eilat_discount_expected_percent = 15.0  # Default 15%
self.eilat_discount_tolerance_percent = 5.0  # +/- 5%
self.eilat_discount_min = 10.0
self.eilat_discount_max = 25.0
```

### Add Brand Mapping

In `taxonomy_manager.py`:

```python
self.brand_taxonomy_mappings = {
    'YourBrand': {
        'Product Name A': 'Keyboards & Synthesizers > Synthesizer',
        'Product Name B': 'Keyboards & Synthesizers > Digital Piano',
    },
}
```

### Add New Category

In `taxonomy_manager.py`, add to `universal_taxonomy`:

```python
"Your Category": {
    "Your Subcategory": TaxonomyNode(
        category="Your Category",
        subcategory="Your Subcategory",
        keywords=["keyword1", "keyword2"],
        aliases=["Alias 1", "Alias 2"],
        description="Description here",
        display_order=10,
    ),
},
```

---

## Error Handling

```python
report = orchestrator.ingest_batch("Nord", raw_products)

# Check for critical errors
if report.rejected_count > 0:
    print(f"⚠ {report.rejected_count} products rejected:")
    for product, errors in report.rejected_products:
        print(f"\n{product.product_name}:")
        for error in errors:
            if error.startswith("❌"):
                print(f"  CRITICAL: {error}")
            else:
                print(f"  WARNING: {error}")

# Check recommendations
if report.recommendations:
    print("\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")
```

---

## Validation Rules

### Critical Errors (Block Approval)

- ❌ Missing ID
- ❌ Missing name
- ❌ Missing brand
- ❌ Eilat price > IL price
- ❌ Invalid category/subcategory combo
- ❌ Data completeness < 40%

### Warnings (Don't Block)

- ⚠ Eilat discount outside 10%-25% range
- ⚠ Price seems unusual for category
- ⚠ Data completeness < 60%
- ⚠ Missing official specs

---

## Testing

```python
def test_nord_ingestion():
    from backend.ingestion import get_ingestion_orchestrator

    orchestrator = get_ingestion_orchestrator()

    raw_products = [{
        "name": "Nord Lead A1",
        "price_il": 14500,
        "price_eilat": 12325,
    }]

    report = orchestrator.ingest_batch("Nord", raw_products)

    assert report.approved_count == 1
    product = report.approved_products[0]
    assert product.taxonomy.canonical_category == "Keyboards & Synthesizers"
    assert product.pricing.tier.value == "pro"
    assert product.display.display_role.value == "cornerstone"
    print("✅ Test passed!")
```

---

## Performance Tips

1. **Batch Processing**: Ingest multiple products at once (better throughput)
2. **Caching**: Manager singletons are cached (reuse instances)
3. **Lazy Loading**: Managers initialize on first use
4. **No DB Calls**: Current implementation is in-memory (add caching layer as needed)

---

## FAQ

**Q: How do I add a new category?**
A: Edit `taxonomy_manager.py` → `_build_universal_taxonomy()` → add to dict

**Q: How do I change tier boundaries?**
A: Edit `pricing_engine.py` → `__init__` → `tier_boundaries` dict

**Q: Can I customize the pipeline?**
A: Yes, subclass `IngestionOrchestrator` and override `_phase_*` methods

**Q: What's the minimum data to ingest?**
A: id, name, brand, price_il, price_eilat (others optional)

**Q: How do I validate before ingesting?**
A: Call respective engine validation methods first (e.g., `pricing.validate_pricing()`)

**Q: Can I use the legacy ProductDraft format?**
A: Yes, orchestrator has `ingest_legacy_products()` method

---

## Resources

- 📚 Full Architecture: `backend/ingestion/ARCHITECTURE.md`
- 🔍 Data Models: `backend/ingestion/data_models.py`
- 📊 Taxonomy: `backend/ingestion/taxonomy_manager.py`
- 💰 Pricing: `backend/ingestion/pricing_engine.py`
- 🎨 Display: `backend/ingestion/display_engine.py`
- 🎭 Orchestrator: `backend/ingestion/orchestrator.py`
