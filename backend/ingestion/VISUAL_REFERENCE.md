# INGESTION PIPELINE v6.0 - VISUAL REFERENCE

## 🎬 The 6-Phase Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  RAW PRODUCT DATA (from Halilit scraper)                               │
│  ├─ name: "Nord Lead A1"                                              │
│  ├─ price_il: 14500                                                   │
│  ├─ price_eilat: 12325                                                │
│  └─ ...other fields                                                    │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 1: HARVEST (Normalization)                                     │
│  ├─ Extract: id, name, prices, basic fields                          │
│  └─ Create: IngestionProductDraft (basic)                            │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 2: ENRICH (Taxonomy Classification)                           │
│  ├─ Input: product_name, brand, description, specs                  │
│  ├─ Process: TaxonomyManager.classify_product()                     │
│  ├─ Confidence scoring (0-1)                                        │
│  └─ Output: canonical_category, canonical_subcategory              │
│                                                                           │
│       Example: "Nord Lead A1" → "Keyboards & Synthesizers" >        │
│                                  "Nord Keyboard" (0.98 confidence)   │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 3: TIER (Pricing Strategy)                                    │
│  ├─ Input: price_il, price_eilat                                    │
│  ├─ Process: PricingEngine.determine_tier_by_price()               │
│  ├─ Validate: Check pricing consistency                             │
│  ├─ Calculate: Eilat discount (15% ± 5%)                          │
│  └─ Output: tier, eilat_discount%, pricing_valid                  │
│                                                                           │
│       Example: 14500 NIS → PRO tier, 15% discount ✓               │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 4: PREPARE (Display Configuration)                           │
│  ├─ Input: tier, data_completeness, media_assets                   │
│  ├─ Process: DisplayEngine.build_display_properties()              │
│  ├─ Determine: display_role (HERO/CORNERSTONE/etc)                │
│  ├─ Select: hero_image, organize media                             │
│  └─ Output: DisplayProperties (complete)                           │
│                                                                           │
│       Example: PRO + 82% complete → CORNERSTONE role,             │
│                tier_level=4, hero_img selected                   │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 5: VALIDATE (Compliance Check)                               │
│  ├─ Check: Required fields present                                 │
│  ├─ Check: Taxonomy validity                                       │
│  ├─ Check: Data completeness ≥ 40%                                │
│  ├─ Check: Pricing rules passed                                   │
│  └─ Output: is_valid, validation_errors[]                         │
│                                                                           │
│       Example: All checks pass → VALID                             │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  PHASE 6: APPROVE (Final Decision)                                  │
│  ├─ Mark: validation_status = APPROVED                             │
│  └─ Output: IngestionProductDraft (complete & approved)            │
│                                                                           │
│                              ↓                                            │
│                                                                           │
│  APPROVED PRODUCT (ready for Spectrum display)                      │
│  ├─ All fields populated                                           │
│  ├─ Taxonomy assigned                                             │
│  ├─ Pricing tiered                                               │
│  ├─ Display configured                                           │
│  └─ Quality metrics calculated                                   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ The 4 Core Engines

```
┌──────────────────────────────────────────────────────────────────────┐
│                    INGESTION ORCHESTRATOR                           │
│                  (Master Conductor)                                 │
│                                                                      │
│  Orchestrates the 6-phase pipeline                                 │
│  Manages error handling & reporting                                │
│                                                                      │
│        ↓              ↓              ↓              ↓               │
│                                                                      │
│  ┌────────────────┬────────────────┬────────────────┬────────────┐ │
│  │   TAXONOMY     │   PRICING      │   DISPLAY      │ VALIDATION │ │
│  │   MANAGER      │   ENGINE       │   ENGINE       │  LOGIC     │ │
│  ├────────────────┼────────────────┼────────────────┼────────────┤ │
│  │ ✓ Universal    │ ✓ Tier Logic   │ ✓ Display Role │ ✓ Required │ │
│  │   Taxonomy     │ ✓ Price Rules  │ ✓ Media Org    │   Fields   │ │
│  │ ✓ Brand Maps   │ ✓ Validation   │ ✓ Color Scheme │ ✓ Taxonomy │ │
│  │ ✓ Classification  ✓ Anomaly Det.  ✓ Hero Image  │ ✓ Completeness
│  │                │ ✓ Discount     │ ✓ Tier Levels │ ✓ Pricing  │ │
│  │                │   Calculation  │                │            │ │
│  └────────────────┴────────────────┴────────────────┴────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

All 4 engines read/write to:
┌──────────────────────────────────────────────────────────────────────┐
│                 INGESTIONPRODUCTDRAFT                               │
│            (Unified Data Model)                                     │
│                                                                      │
│  Single source of truth flowing through all 6 phases               │
│  Contains all product information from raw data to approved output │
│                                                                      │
│  Fields:                                                           │
│  • Identity: halilit_id, name, brand, model, sku                │
│  • Taxonomy: category, subcategory, confidence                  │
│  • Pricing: price_il, price_eilat, tier, discount%             │
│  • Display: role, hero_image, tier_level, color               │
│  • Content: description, features, specifications              │
│  • Source: provenance, confidence, extraction_method          │
│  • Quality: completeness, score, validation_status           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Taxonomy Hierarchy

```
┌────────────────────────────────────────────────────────────────┐
│                  UNIVERSAL TAXONOMY                            │
│                                                                │
│  Keyboards & Synthesizers (7)                                │
│  ├─ Synthesizer                                              │
│  ├─ Digital Keyboard                                         │
│  ├─ Digital Piano                                            │
│  ├─ Nord Keyboard                                            │
│  ├─ Moog Synthesizer                                         │
│  ├─ Groovebox                                                │
│  └─ Organ                                                     │
│                                                                │
│  Drums & Percussion (5)                                      │
│  ├─ Electronic Drum                                          │
│  ├─ Drum Trigger                                             │
│  ├─ Drum Pad                                                 │
│  ├─ Percussion                                               │
│  └─ Drum Kit                                                 │
│                                                                │
│  Audio Interfaces & Mixers (3)                              │
│  ├─ Audio Interface                                          │
│  ├─ Mixer                                                    │
│  └─ Preamp                                                   │
│                                                                │
│  Microphones & Recording (6)                                │
│  ├─ Condenser Mic                                            │
│  ├─ Dynamic Mic                                              │
│  ├─ Ribbon Mic                                               │
│  ├─ Wireless Mic                                             │
│  ├─ Microphone                                               │
│  └─ Recording Equipment                                      │
│                                                                │
│  Cables & Connectors (3)                                    │
│  ├─ Cable                                                    │
│  ├─ Connector                                                │
│  └─ Jack                                                     │
│                                                                │
│  Studio Monitors & Speakers (3)                             │
│  ├─ Studio Monitor                                           │
│  ├─ Powered Speaker                                          │
│  └─ Speaker                                                  │
│                                                                │
│  Headphones & Earphones (3)                                │
│  ├─ Headphones                                               │
│  ├─ In-Ear Monitors                                          │
│  └─ Earbuds                                                  │
│                                                                │
│  Amplifiers & Effects (3)                                   │
│  ├─ Amplifier                                                │
│  ├─ Effects Processor                                        │
│  └─ Pedal                                                    │
│                                                                │
│  TOTAL: 8 categories, 32 subcategories (expandable)         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 💰 Pricing Tier System

```
PRICE DISTRIBUTION                    DISPLAY PROMINENCE
(Israel Price)
                                     [5] ██████████████ FLAGSHIP
┌─────────────────────────┐
│                         │          ⭐ Hero products
│   > 4000 NIS            │          Featured prominently
│   FLAGSHIP TIER         │
│        └→ 👑            │
│                         │
├─────────────────────────┤
│                         │          [4] ████████████
│   1500-4000 NIS         │          CORNERSTONE
│   PRO TIER              │
│        └→ 💎            │          💎 Key products
│                         │          Prominent display
├─────────────────────────┤
│                         │          [3] ██████████
│   500-1500 NIS          │          SPECIALIST
│   MID TIER              │
│        └→ ⭐            │          🎯 Normal display
│                         │
├─────────────────────────┤
│                         │          [1] ████
│   < 500 NIS             │          ENTRY
│   ENTRY TIER            │
│        └→ 🎯            │          🎁 Lower prominence
│                         │
└─────────────────────────┘

EXAMPLE PRODUCTS BY TIER:

FLAGSHIP (> 4000 NIS):
  • Nord Grand ..................... 15000 NIS  👑
  • Moog One ...................... 10000 NIS  👑

PRO (1500-4000 NIS):
  • Nord Lead A1 .................. 14500 NIS  💎
  • Elektron Analog Rytm ........... 2500 NIS  💎

MID (500-1500 NIS):
  • Korg Volca .................... 1200 NIS  ⭐
  • Yamaha P-125 .................... 800 NIS  ⭐

ENTRY (< 500 NIS):
  • Basic MIDI Controller ........... 200 NIS  🎯
  • 3m Audio Cable ................... 50 NIS  🎯
```

---

## 🎨 Display Roles & Prominence

```
┌──────────────────────────────────────────────────────────────┐
│  DISPLAY ROLE SYSTEM                                         │
│                                                              │
│  HERO (Tier 5) ⭐⭐⭐⭐⭐                                     │
│  ├─ Flagship/signature products                            │
│  ├─ Featured prominently on page                           │
│  ├─ Large hero image                                       │
│  ├─ Highlighted/special styling                           │
│  └─ Conditions: FLAGSHIP tier + high completeness (80%+)  │
│                                                              │
│  CORNERSTONE (Tier 4) ⭐⭐⭐⭐                              │
│  ├─ Key products in each tier                             │
│  ├─ Prominent display placement                           │
│  ├─ Full media assets                                     │
│  ├─ No special styling                                    │
│  └─ Conditions: PRO/MID tier + good completeness (70%+)   │
│                                                              │
│  SPECIALIST (Tier 3) ⭐⭐⭐                                │
│  ├─ Niche/specialized products                            │
│  ├─ Normal display placement                              │
│  ├─ Standard media (hero + gallery)                       │
│  ├─ Category-specific styling                             │
│  └─ Conditions: Default for most products                 │
│                                                              │
│  ENTRY (Tier 1) ⭐                                         │
│  ├─ Gateway/budget products                               │
│  ├─ Lower in product lists                                │
│  ├─ Minimal media                                         │
│  ├─ Muted styling                                         │
│  └─ Conditions: ENTRY tier + any completeness            │
│                                                              │
│  HIDDEN (Tier 0)                                           │
│  ├─ Internal/archived products                            │
│  ├─ Not displayed in UI                                  │
│  ├─ Only in admin views                                  │
│  └─ Conditions: LEGACY tier or manual hide               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📈 Data Completeness Scoring

```
COMPLETENESS SCORED: 0% → 100%

REQUIRED FIELDS (70% total weight):
  ├─ Identity (30%)
  │  ├─ halilit_id .................. +10%
  │  ├─ product_name ................ +10%
  │  └─ brand ....................... +10%
  │
  ├─ Pricing (20%)
  │  ├─ price_il .................... +10%
  │  └─ price_eilat ................. +10%
  │
  └─ Taxonomy (20%)
     ├─ canonical_category .......... +10%
     └─ canonical_subcategory ....... +10%

RECOMMENDED FIELDS (30% total weight):
  ├─ Description (10%)
  │  ├─ description_short ........... +5%
  │  └─ description_long ............ +5%
  │
  ├─ Media (10%)
  │  ├─ hero_image .................. +5%
  │  └─ gallery images .............. +5%
  │
  ├─ Specifications (5%)
  │  └─ specs_dict .................. +5%
  │
  └─ Official Source (5%)
     └─ official_data ............... +5%

THRESHOLDS:
  ✅ APPROVED: ≥ 40% completeness
  ⚠️  WARNING:  < 40% completeness
     💡 Recommended: 75%+ completeness
     🌟 Excellent:   90%+ completeness

CALCULATION EXAMPLE:
  Product A:
    ✓ ID, name, brand ............... +30%
    ✓ Both prices ................... +20%
    ✓ Category, subcategory ......... +20%
    ✓ Short description ............. +5%
    ✓ Hero image .................... +5%
    ─────────────────────────────
    TOTAL ........................... 80% (Excellent!)

  Product B:
    ✓ ID, name, brand ............... +30%
    ✓ Both prices ................... +20%
    ✓ Category, subcategory ......... +20%
    ─────────────────────────────
    TOTAL ........................... 70% (Good)

  Product C:
    ✓ ID, name, brand ............... +30%
    ✓ price_il only ................. +5%
    (missing price_eilat, category)
    ─────────────────────────────
    TOTAL ........................... 35% (REJECTED - below 40%)
```

---

## 🔄 Data Flow Example

### Real Product: Nord Lead A1 Through Pipeline

```
INPUT:
{
    "name": "Nord Lead A1",
    "price_il": 14500,
    "price_eilat": 12325,
    "source_url": "https://halilit.com/nord-lead-a1",
    "description": "Nord Lead A1 is a performance-oriented keyboard...",
}

PHASE 1: HARVEST
┌──────────────────────────────────────┐
│ IngestionProductDraft                │
├──────────────────────────────────────┤
│ halilit_id: "nord_001"               │
│ product_name: "Nord Lead A1"         │
│ brand: "Nord"                        │
│ pricing.price_il: 14500              │
│ pricing.price_eilat: 12325           │
│ pricing.tier: UNKNOWN                │
│ taxonomy: NOT YET CLASSIFIED         │
│ display: EMPTY                       │
│ validation_status: HARVESTED         │
└──────────────────────────────────────┘

PHASE 2: ENRICH (TAXONOMY)
TaxonomyManager.classify_product() runs:
  Search: "nord lead a1" in keywords
  Match: "nord lead" found in brand mappings
  Result: ("Keyboards & Synthesizers", "Nord Keyboard", 0.98)
┌──────────────────────────────────────┐
│ IngestionProductDraft (updated)      │
├──────────────────────────────────────┤
│ [all Phase 1 fields plus:]           │
│ taxonomy.canonical_category:         │
│   "Keyboards & Synthesizers"         │
│ taxonomy.canonical_subcategory:      │
│   "Nord Keyboard"                    │
│ validation_status: ENRICHED          │
└──────────────────────────────────────┘

PHASE 3: TIER (PRICING)
PricingEngine applies strategy:
  - Tier from price: 14500 NIS → PRO (1500-4000 range)
  - Validate prices: 14500 > 12325 ✓
  - Discount: (14500-12325)/14500 = 15% ✓ (perfect!)
  - Apply rules: All pass ✓
┌──────────────────────────────────────┐
│ IngestionProductDraft (updated)      │
├──────────────────────────────────────┤
│ [all previous fields plus:]          │
│ pricing.tier: PRO                    │
│ pricing.eilat_discount_percent: 15   │
│ validation_status: ENRICHED          │
└──────────────────────────────────────┘

PHASE 4: PREPARE (DISPLAY)
DisplayEngine calculates display properties:
  - Tier: PRO
  - Data completeness: 85%
  - Is official: false
  - Is flagship: false
  → Display role: CORNERSTONE
  → Tier level: 4
  → Should highlight: false
┌──────────────────────────────────────┐
│ IngestionProductDraft (updated)      │
├──────────────────────────────────────┤
│ [all previous fields plus:]          │
│ display.display_role: CORNERSTONE    │
│ display.display_tier_level: 4        │
│ display.hero_image: selected         │
│ data_completeness: 0.85              │
└──────────────────────────────────────┘

PHASE 5: VALIDATE
Check all rules:
  ✓ Required fields present
  ✓ Taxonomy valid
  ✓ Pricing valid
  ✓ Completeness ≥ 40%
  → VALID
┌──────────────────────────────────────┐
│ IngestionProductDraft (updated)      │
├──────────────────────────────────────┤
│ [all previous fields plus:]          │
│ validation_status: VALIDATED         │
│ validation_errors: []                │
└──────────────────────────────────────┘

PHASE 6: APPROVE
Mark for display:
┌──────────────────────────────────────┐
│ IngestionProductDraft (FINAL)        │
├──────────────────────────────────────┤
│ validation_status: APPROVED          │
│ [completely populated]               │
│                                      │
│ READY FOR DISPLAY ✅                │
└──────────────────────────────────────┘

FINAL OUTPUT:
✅ APPROVED: Nord Lead A1
   Category: Keyboards & Synthesizers > Nord Keyboard
   Tier: PRO (14500 NIS)
   Discount: 15% ✓
   Display: CORNERSTONE (tier level 4)
   Completeness: 85%
   Quality: EXCELLENT
```

---

## 🎯 Quick Reference Matrix

| Aspect       | Phase | Input                            | Output                           | Engine           |
| ------------ | ----- | -------------------------------- | -------------------------------- | ---------------- |
| **Harvest**  | 1     | Raw dict                         | IngestionProductDraft (basic)    | Orchestrator     |
| **Taxonomy** | 2     | Product name, brand, description | canonical_category, subcategory  | Taxonomy Manager |
| **Pricing**  | 3     | price_il, price_eilat            | Tier, discount%, valid           | Pricing Engine   |
| **Display**  | 4     | Tier, completeness, media        | Display role, tier level, images | Display Engine   |
| **Validate** | 5     | Complete product                 | is_valid, errors                 | Orchestrator     |
| **Approve**  | 6     | Valid product                    | IngestionProductDraft (final)    | Orchestrator     |

---

## 📞 Error Severity Levels

```
❌ CRITICAL (Blocks Approval)
   └─ Missing required fields
   └─ Eilat > IL price
   └─ Invalid category
   └─ Data completeness < 40%

⚠️  WARNING (Doesn't Block)
   └─ Eilat discount outside range
   └─ Incomplete data
   └─ Unusual price
   └─ Missing official source

ℹ️  INFO (Informational)
   └─ Processing steps
   └─ Confidence scores
   └─ Recommendations
```

---

## 🚀 Usage Pattern

```
orchestrator = get_ingestion_orchestrator()
           ↓
report = orchestrator.ingest_batch("Nord", raw_products)
           ↓
if report.approved_count > 0:
    print(f"✅ {report.approved_count} approved")
    for product in report.approved_products:
        use_product(product)
           ↓
if report.rejected_count > 0:
    print(f"❌ {report.rejected_count} rejected")
    for product, errors in report.rejected_products:
        log_rejection(product, errors)
           ↓
for recommendation in report.recommendations:
    log_recommendation(recommendation)
```
