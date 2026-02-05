# INGESTION PIPELINE ARCHITECTURE v6.0

## 🎯 Executive Summary

This document describes the **complete refactored scraping and ingestion phase** for the Halilit Support Center. It replaces ad-hoc data handling with a **unified, taxonomy-aware, pricing-conscious, display-optimized pipeline**.

### Problem Statement

Previous system had:

- ❌ Scattered taxonomy logic (buried in DataRefinery)
- ❌ Basic pricing (just two prices, no tiers)
- ❌ Display logic mixed with data processing
- ❌ No single data model (different models in different places)
- ❌ Difficult to test and maintain
- ❌ No clear separation of concerns

### Solution: 4-Engine Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           INGESTION ORCHESTRATOR (Master Conductor)          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PHASE 1: HARVEST  → ENRICH  → TIER  → PREPARE  → VALIDATE  │
│                      │          │       │           │         │
│                      v          v       v           v         │
│               ┌──────────┬────────────┬──────────┬──────────┐ │
│               │Taxonomy  │ Pricing    │ Display  │ Validation│ │
│               │Manager   │Engine      │Engine    │Logic      │ │
│               └──────────┴────────────┴──────────┴──────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────┐
    │ UNIFIED DATA MODEL                 │
    │ (IngestionProductDraft)            │
    ├────────────────────────────────────┤
    │ • Identity & Naming                │
    │ • Taxonomy & Classification        │
    │ • Pricing & Value                  │
    │ • Description & Content            │
    │ • Specifications                   │
    │ • Display & Presentation           │
    │ • Source & Provenance              │
    │ • Quality & Validation             │
    └────────────────────────────────────┘
```

---

## 📊 Architecture Overview

### The 4 Core Engines

#### 1. **Taxonomy Manager** (`taxonomy_manager.py`)

Manages product categorization with:

- **Universal Taxonomy**: Single source of truth with categories and subcategories
- **Brand Mappings**: How each brand's products map to universal taxonomy
- **Keyword Index**: Fast lookup any term → canonical category
- **Validation**: Check if category/subcategory combo is valid

```python
taxonomy_mgr = get_taxonomy_manager()
category, subcategory, confidence = taxonomy_mgr.classify_product(
    product_name="Nord Lead A1",
    brand="Nord",
    description="Professional synthesizer....",
)
# Returns: ("Keyboards & Synthesizers", "Synthesizer", 0.98)
```

**Universal Categories** (expandable):

- Keyboards & Synthesizers
  - Synthesizer, Digital Keyboard, Digital Piano, Nord Keyboard, Moog Synthesizer, Groovebox, Organ
- Drums & Percussion
  - Electronic Drum, Drum Trigger, Drum Pad, Percussion, Drum Kit
- Audio Interfaces & Mixers
  - Audio Interface, Mixer, Preamp
- Microphones & Recording
  - Condenser Mic, Dynamic Mic, Ribbon Mic, Wireless Mic, Microphone, Recording Equipment
- Cables & Connectors
  - Cable, Connector, Jack
- Studio Monitors & Speakers
  - Studio Monitor, Powered Speaker, Speaker
- Headphones & Earphones
  - Headphones, In-Ear Monitors, Earbuds
- Amplifiers & Effects
  - Amplifier, Effects Processor, Pedal

#### 2. **Pricing Strategy Engine** (`pricing_engine.py`)

Handles all pricing logic:

- **Tier Determination**: Map price → tier (Entry/Mid/Pro/Flagship)
- **Price Validation**: Check for inconsistencies and violations
- **Regional Pricing**: Validate IL vs Eilat prices
- **Discount Calculations**: Compute and validate 15% default discount
- **Pricing Rules**: Enforce business logic (min/max prices per tier)
- **Anomaly Detection**: Identify suspicious price changes

```python
pricing_engine = get_pricing_engine()

# Determine tier from price
tier = pricing_engine.determine_tier_by_price(8500)  # Returns: PricingTier.PRO

# Validate pricing
is_valid, errors = pricing_engine.validate_pricing(pricing_data)

# Suggest Eilat discount
eilat_price = pricing_engine.suggest_eilat_price(price_il=10000)  # Returns: 8500
```

**Pricing Tiers**:

- **Entry**: < 500 NIS (Budget products)
- **Mid**: 500-1,500 NIS (Mid-range)
- **Pro**: 1,500-4,000 NIS (Professional)
- **Flagship**: > 4,000 NIS (Premium)

**Regional Pricing Rules**:

- Default Eilat discount: 15%
- Acceptable range: 10%-25%
- Minimum discount: 10%
- Maximum discount: 25% (flag as suspicious)

#### 3. **Display Preparation Engine** (`display_engine.py`)

Prepares products for UI display:

- **Display Role**: Classify as Hero/Cornerstone/Specialist/Entry/Hidden
- **Media Organization**: Sort and prioritize images/videos/docs
- **Tier Levels**: Set display prominence (1-5)
- **Color Schemes**: Brand colors and tier colors
- **Visual Hints**: Highlights, thumbnails, hero images

```python
display_engine = get_display_engine()

# Determine display role
role = display_engine.determine_display_role(
    product_name="Nord Lead A1",
    pricing_tier=PricingTier.PRO,
    data_completeness=0.85,
    is_official_spec=True,
    is_flagship_product=False,
)  # Returns: DisplayRole.CORNERSTONE

# Build full display properties
display_props = display_engine.build_display_properties(...)
```

**Display Roles**:

- **Hero** (⭐ Tier 5): Flagship/signature products - featured prominently
- **Cornerstone** (💎 Tier 4): Key products in each tier - prominent display
- **Specialist** (🎯 Tier 3): Niche products - normal display
- **Entry** (🎁 Tier 1): Gateway products - lower in list
- **Hidden** (🚫 Tier 0): Internal/archived - not displayed

#### 4. **Ingestion Orchestrator** (`orchestrator.py`)

Master conductor that orchestrates the entire pipeline:

---

## 🔄 The 6-Phase Pipeline

The ingestion process happens in 6 sequential phases:

```
RAW DATA
   ↓
[PHASE 1: HARVEST]
   • Normalize raw scraped data
   • Extract ID, name, prices
   • Create IngestionProductDraft
   ↓
[PHASE 2: ENRICH - TAXONOMY]
   • Classify product into universal taxonomy
   • Apply brand-specific mappings
   • Set category/subcategory with confidence
   ↓
[PHASE 3: TIER - PRICING]
   • Determine pricing tier from price
   • Validate pricing consistency
   • Calculate Eilat discount
   • Apply pricing rules
   ↓
[PHASE 4: PREPARE - DISPLAY]
   • Determine display role
   • Organize media assets
   • Set tier level
   • Assign visual properties
   ↓
[PHASE 5: VALIDATE]
   • Check required fields
   • Validate taxonomy
   • Check data completeness (min 40%)
   • Verify pricing rules
   ↓
[PHASE 6: APPROVE]
   • Mark as APPROVED
   • Generate ingestion report
   ↓
APPROVED PRODUCTS
```

### Example: North Lead A1 Through Pipeline

```
Input: {
    "name": "Nord Lead A1",
    "price_il": 14500,
    "price_eilat": 12325,
    "source": "halilit.com",
    ...
}

Phase 1 (HARVEST):
✓ Created draft with basic data
✓ ID: nord_001, Name: Nord Lead A1, Brand: Nord
✓ Prices: 14500 NIS / 12325 NIS

Phase 2 (ENRICH - TAXONOMY):
✓ Classified: "Keyboards & Synthesizers" > "Nord Keyboard"
✓ Confidence: 0.98 (brand mapping match)

Phase 3 (TIER - PRICING):
✓ Tier: PRO (price 14500 falls in 1500-4000 range)
✓ Eilat discount: 15% (perfect!) ✓
✓ Pricing validated: PASS

Phase 4 (PREPARE - DISPLAY):
✓ Display role: CORNERSTONE (PRO tier + 80% completeness)
✓ Display tier level: 4
✓ Hero image selected: official.jpg

Phase 5 (VALIDATE):
✓ All required fields present
✓ Taxonomy valid
✓ Data completeness: 82%
✓ Pricing rules: PASS
✓ Result: VALID

Phase 6 (APPROVE):
✓ Final status: APPROVED
✓ Ready for frontend display

Output: IngestionProductDraft (fully prepared)
```

---

## 📋 Unified Data Model

### IngestionProductDraft

The core data structure that flows through the entire pipeline:

```python
class IngestionProductDraft(BaseModel):
    # Identity
    halilit_id: str                    # Primary unique ID
    product_name: str                  # Display name
    official_name: Optional[str]       # Manufacturer name
    brand: str                         # Brand
    model_number: Optional[str]        # Model number
    sku: Optional[str]                 # SKU

    # Taxonomy & Classification
    taxonomy: TaxonomyMapping          # Category mapping
        ├─ canonical_category: str     # "Keyboards & Synthesizers"
        ├─ canonical_subcategory: str  # "Synthesizer"
        ├─ brand_taxonomy: Optional[str]
        └─ keywords: List[str]

    # Pricing & Value
    pricing: PricingData               # All pricing info
        ├─ price_il: float             # Israel price
        ├─ price_eilat: float          # Eilat price
        ├─ tier: PricingTier            # ENTRY/MID/PRO/FLAGSHIP
        ├─ eilat_discount_percent: float
        └─ suggested_tier: PricingTier

    # Content
    description_short: Optional[str]   # 1-line description
    description_long: Optional[str]    # Full description
    feature_list: List[str]            # Key features

    # Specifications
    specifications: ProductSpecifications
        ├─ specs_dict: Dict
        ├─ specs_source: DataSourceConfidence
        ├─ specs_completeness: float
        └─ specs_markdown: Optional[str]

    # Display & Presentation
    display: DisplayProperties         # All display info
        ├─ display_role: DisplayRole   # HERO/CORNERSTONE/SPECIALIST/ENTRY
        ├─ hero_image: Optional[str]
        ├─ media_assets: List[MediaAsset]
        ├─ display_tier_level: int     # 1-5
        ├─ color_hint: Optional[str]
        └─ should_highlight: bool

    # Source & Lineage
    sources: List[SourceProvenance]    # All sources
    primary_source: SourceProvenance   # Primary source
        ├─ source_name: str
        ├─ confidence: DataSourceConfidence
        ├─ timestamp: datetime
        └─ extraction_method: str

    # Quality & Status
    data_completeness: float           # 0-1, overall completeness
    quality_score: float               # 0-1, overall quality
    validation_status: IngestionStatus # HARVESTED/ENRICHED/VALIDATED/APPROVED
    validation_errors: List[str]
    validation_warnings: List[str]
```

---

## 🚀 Usage Examples

### Basic Ingestion

```python
from backend.ingestion import get_ingestion_orchestrator

orchestrator = get_ingestion_orchestrator()

# Raw products from scraper
raw_products = [
    {
        "name": "Nord Lead A1",
        "price_il": 14500,
        "price_eilat": 12325,
        "source_url": "https://halilit.com/nord-lead",
        # ... other raw fields
    },
]

# Run complete ingestion pipeline
report = orchestrator.ingest_batch(
    brand="Nord",
    raw_products=raw_products,
)

# Check results
print(f"Approved: {report.approved_count}")
print(f"Rejected: {report.rejected_count}")

for product in report.approved_products:
    print(f"  ✓ {product.product_name}")
    print(f"    Category: {product.taxonomy.canonical_category}")
    print(f"    Tier: {product.pricing.tier.value}")
    print(f"    Display Role: {product.display.display_role.value}")

for product, errors in report.rejected_products:
    print(f"  ✗ {product.product_name}")
    for error in errors:
        print(f"    {error}")
```

### Custom Taxonomy Classification

```python
from backend.ingestion import get_taxonomy_manager

taxonomy = get_taxonomy_manager()

# Classify any product
category, subcategory, confidence = taxonomy.classify_product(
    product_name="Moog Sub 37",
    brand="Moog",
    description="Three-oscillator analog synthesizer",
)
print(f"{category} > {subcategory} (confidence: {confidence:.0%})")
# Output: Keyboards & Synthesizers > Moog Synthesizer (confidence: 98%)

# Get all categories
all_categories = taxonomy.get_all_categories()

# Get subcategories for a category
synth_subcats = taxonomy.get_subcategories("Keyboards & Synthesizers")
```

### Custom Pricing Strategy

```python
from backend.ingestion import get_pricing_engine, PricingData, PricingTier

pricing = get_pricing_engine()

# Create pricing data
pricing_data = PricingData(
    price_il=8500,
    price_eilat=7225,
)

# Determine tier
tier = pricing.determine_tier_by_price(pricing_data.price_il)
print(f"Tier: {tier.value}")  # Output: "pro"

# Validate pricing
is_valid, errors = pricing.validate_pricing(pricing_data)
if is_valid:
    print("✓ Pricing is valid")
else:
    for error in errors:
        print(f"  {error}")

# Suggest Eilat price
suggested = pricing.suggest_eilat_price(price_il=10000)
print(f"Suggested Eilat price: {suggested} NIS")
```

### Custom Display Preparation

```python
from backend.ingestion import get_display_engine, MediaAsset, DataSourceConfidence

display = get_display_engine()

# Prepare media assets
media = [
    MediaAsset(
        type="image",
        url="https://example.com/hero.jpg",
        display_purpose="hero",
        resolution="2000x1500",
        source=DataSourceConfidence.OFFICIAL,
        priority=100,
    ),
]

# Build display properties
display_props = display.build_display_properties(
    product_name="Nord Lead A1",
    pricing_tier=PricingTier.PRO,
    brand="Nord",
    data_completeness=0.85,
    media_assets=media,
    is_official=True,
)

print(f"Display role: {display_props.display_role.value}")
print(f"Tier level: {display_props.display_tier_level}")
print(f"Hero image: {display_props.hero_image}")
```

---

## 📈 Quality Metrics

### Data Completeness Score

Measured 0-1 (0% to 100%):

```
• Basic identity (id, name, brand): 30%
  ├─ ID present: +10%
  ├─ Name present: +10%
  └─ Brand present: +10%

• Pricing (required): 20%
  ├─ price_il present: +10%
  └─ price_eilat present: +10%

• Taxonomy (required): 10%
  ├─ category present: +5%
  └─ subcategory present: +5%

• Description (recommended): 10%
  ├─ description_short: +5%
  └─ description_long: +5%

• Specifications (recommended): 5%
• Media/images (recommended): 15%
• Official source (recommended): 5%

MINIMUM THRESHOLD FOR APPROVAL: 40%
RECOMMENDED TARGET: 75%+
```

### Quality Score

Combines:

- Data completeness (above)
- Pricing validity
- Taxonomy confidence
- Media presence

---

## 🔌 Integration Points

### With Trinity Agents

```python
# CommercialScout → Harvest data
raw_products = commercial_agent.harvest(brand="Nord")

# Send to orchestrator
report = orchestrator.ingest_batch("Nord", raw_products)

# OfficialVerifier → Enrich with official specs
for product in report.approved_products:
    official_specs = official_agent.enrich(product)
    # Re-process with official data

# ExternalValidator → Final audit
audit_reports = validator_agent.audit(report.approved_products)
```

### With Spectrum Data Provider

The ingestion pipeline feeds into Spectrum:

```python
from backend.spectrum_data_provider import inject_ingestion_data

# Ingestion produces approved products
approved = report.approved_products

# Organize by price tier
spectrum_tracks = organize_by_price_tracks(approved)

# Inject into Spectrum system
inject_ingestion_data(brand, spectrum_tracks)
```

---

## 🔄 Error Handling & Recovery

### Validation Errors (Blocking)

```
❌ Missing required field: halilit_id
❌ Missing required field: product_name
❌ CRITICAL: Eilat price exceeds Israel price
❌ Invalid price_il (must be positive)
```

### Warnings (Non-blocking)

```
⚠ price_il must be positive
⚠ Eilat discount is suspiciously low (3%)
⚠ Data completeness too low (25%) - minimum 40% required
⚠ Invalid category: Unknown > Unknown
⚠ Price changed +85% from 5000 to 9250 NIS
```

---

## 📚 Configuration & Customization

### Changing Pricing Tiers

```python
# In pricing_engine.py, modify tier_boundaries:
self.tier_boundaries = {
    PricingTier.ENTRY: (0, 300),       # Changed from 500
    PricingTier.MID: (300, 1200),      # Changed
    PricingTier.PRO: (1200, 3500),     # Changed
    PricingTier.FLAGSHIP: (3500, float('inf')),
}
```

### Changing Eilat Discount Rules

```python
# In pricing_engine.py:
self.eilat_discount_expected_percent = 20.0   # Changed from 15%
self.eilat_discount_tolerance_percent = 3.0   # Changed from 5%
self.eilat_discount_min = 12.0  # Changed from 10%
self.eilat_discount_max = 30.0  # Changed from 25%
```

### Adding New Categories

```python
# In taxonomy_manager.py, add to universal_taxonomy:
"Smart Home Audio": {
    "Voice Assistant": TaxonomyNode(...),
    "Smart Speaker": TaxonomyNode(...),
},
```

---

## 🧪 Testing

Example test structure:

```python
def test_harvest_phase():
    """Test Phase 1: Harvest"""
    raw = {"name": "Test", "price_il": 1000}
    draft = orchestrator._phase_harvest(raw, "TestBrand")
    assert draft.product_name == "Test"
    assert draft.pricing.price_il == 1000

def test_taxonomy_enrichment():
    """Test Phase 2: Taxonomy"""
    draft = create_draft("Nord Lead")
    enriched = orchestrator._phase_enrich_taxonomy(draft)
    assert enriched.taxonomy.canonical_category == "Keyboards & Synthesizers"

def test_pricing_tier():
    """Test Phase 3: Pricing"""
    draft = create_draft(price_il=2500)
    tiered = orchestrator._phase_tier_pricing(draft)
    assert tiered.pricing.tier == PricingTier.PRO

def test_display_role():
    """Test Phase 4: Display"""
    draft = create_draft(data_completeness=0.85, tier=PricingTier.PRO)
    prepared = orchestrator._phase_prepare_display(draft)
    assert prepared.display.display_role == DisplayRole.CORNERSTONE
```

---

## 📊 Reporting & Monitoring

### Ingestion Report

```python
report = orchestrator.ingest_batch(brand, products)

print(f"Batch ID: {report.batch_id}")
print(f"Brand: {report.brand}")
print(f"Total: {report.total_products_processed}")
print(f"Approved: {report.approved_count} ({100*report.approved_count/report.total_products_processed:.0f}%)")
print(f"Rejected: {report.rejected_count}")
print(f"Execution time: {report.execution_time_seconds:.2f} seconds")

print("\nRecommendations:")
for rec in report.recommendations:
    print(f"  {rec}")
```

---

## 🎓 Key Principles

1. **Single Responsibility**: Each engine handles one concern
2. **Unified Data Model**: All phases use same IngestionProductDraft
3. **Clear Separation**: Data, Taxonomy, Pricing, Display are distinct services
4. **Stateless Processing**: Each product is independent
5. **Immutable Flow**: Each phase creates new object (no mutation)
6. **Traceable Lineage**: Complete source provenance
7. **Testable Units**: Each engine can be tested independently

---

## 📝 Files & Structure

```
backend/ingestion/
├── __init__.py                 # High-level imports
├── data_models.py              # Unified data models
├── taxonomy_manager.py         # Category system
├── pricing_engine.py           # Pricing logic
├── display_engine.py           # Display preparation
├── orchestrator.py             # Main pipeline orchestrator
└── ARCHITECTURE.md             # This file
```

---

## 🚀 Next Steps

### Short Term

- [x] Implement core 4 engines
- [x] Create unified data model
- [x] Build orchestrator
- [ ] Integrate with Trinity agents
- [ ] Test with real Halilit data
- [ ] Deploy to Spectrum system

### Medium Term

- [ ] Add enrichment from official APIs
- [ ] Parameter tuning from real data
- [ ] Performance optimization
- [ ] Database storage

### Long Term

- [ ] Machine learning tier suggestions
- [ ] Dynamic category suggestions
- [ ] Price prediction
- [ ] Automated data quality improvement
