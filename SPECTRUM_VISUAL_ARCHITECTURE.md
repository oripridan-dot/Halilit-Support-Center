# Spectrum Screen v5.3.0 - Visual Architecture Guide

## System Architecture Diagram

```
╔════════════════════════════════════════════════════════════════════════════╗
║                     SPECTRUM SCREEN DATA PIPELINE v5.3.0                   ║
╚════════════════════════════════════════════════════════════════════════════╝

                              FRONTEND
                          (React + TypeScript)
                                  │
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼────────┐        ┌────────▼────────┐
            │  useSpectrumData │      │ SpectrumModule   │
            │  Custom Hooks    │      │ Component        │
            └────────┬────────┘       └────────┬─────────┘
                     │                         │
                     └──────────┬──────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   API ENDPOINTS       │
                    │  /api/spectrum/*      │
                    └───────────┬───────────┘
                                │
╔═══════════════════════════════╩══════════════════════════════════════════╗
║                          BACKEND (Python/FastAPI)                        ║
└═══════════════════════════════╬══════════════════════════════════════════┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
    ┌───────▼──────────┐  ┌────▼─────────┐  ┌─────▼────────────┐
    │ SPECTRUM PIPELINE │  │  VALIDATION  │  │ ENRICHMENT       │
    │                   │  │              │  │                  │
    │ Phase 1: Scrape   │  │ Validator:   │  │ Official Specs   │
    │   Halilit         │  │ ├─Critical   │  │ Enricher:        │
    │                   │  │ ├─Warnings   │  │ ├─Specs          │
    │ Phase 2: Organize │  │ ├─Quality    │  │ ├─Images         │
    │   by Price        │  │ │   Score    │  │ └─Warranty       │
    │                   │  │ └──────      │  │                  │
    │ Phase 3: Enrich   │  │              │  │ Review           │
    │   Official        │  │ Provenance   │  │ Aggregator:      │
    │                   │  │ Tracker:     │  │ ├─Thomann (35%)  │
    │ Phase 4: Enrich   │  │ ├─Source     │  │ ├─Sweetwater (35)│
    │   Reviews         │  │ ├─Confidence │  │ ├─Reverb (20%)   │
    │                   │  │ └─Attribution│  │ └─Gearspace (10%)│
    │ Phase 5: Build    │  │              │  │                  │
    │   Hierarchy       │  │ Report Gen:  │  │ Normalizer:      │
    │                   │  │ ├─Summary    │  │ ├─Units          │
    └─────────┬─────────┘  │ ├─Metrics    │  │ ├─Field Names    │
              │            │ └─Recommend. │  │ └─Data Types     │
              │            └──────────────┘  └──────────────────┘
              │
    ┌─────────▼──────────────────────────────────┐
    │        DATA SOURCES & ENRICHMENT           │
    │                                            │
    │  PRIMARY SOURCE:                           │
    │  ┌──────────────────────────────────┐     │
    │  │ Halilit.com (Commerce)           │     │
    │  │ • Product IDs                    │     │
    │  │ • Product Names                  │     │
    │  │ • Prices (IL + Eilat)            │     │
    │  │ • Stock Status                   │     │
    │  │ Confidence: 0.98                 │     │
    │  └──────────────────────────────────┘     │
    │                                            │
    │  OFFICIAL SOURCES:                        │
    │  ┌──────────────────────────────────┐     │
    │  │ Manufacturer APIs                │     │
    │  │ • Nord   → nord.com/api          │     │
    │  │ • Moog   → moog.com/api          │     │
    │  │ • Roland → roland.com/api        │     │
    │  │ • Yamaha → yamaha.com/api        │     │
    │  │ • Korg   → korg.com/api          │     │
    │  │ • U-Audio→ uaudio.com/api        │     │
    │  │ Confidence: 0.95                 │     │
    │  └──────────────────────────────────┘     │
    │                                            │
    │  TRUSTED REVIEWS:                         │
    │  ┌──────────────────────────────────┐     │
    │  │ Thomann (Europe, 35% weight)     │     │
    │  │ • Ratings & review count         │     │
    │  │ • Customer feedback              │     │
    │  │ Confidence: 0.90                 │     │
    │  ├──────────────────────────────────┤     │
    │  │ Sweetwater (USA, 35% weight)     │     │
    │  │ • Expert reviews                 │     │
    │  │ • Pro feedback                   │     │
    │  │ Confidence: 0.90                 │     │
    │  ├──────────────────────────────────┤     │
    │  │ Reverb (Community, 20% weight)   │     │
    │  │ • User ratings                   │     │
    │  │ • Community insights             │     │
    │  │ Confidence: 0.85                 │     │
    │  ├──────────────────────────────────┤     │
    │  │ Gearspace (Forum, 10% weight)    │     │
    │  │ • User discussions               │     │
    │  │ • Recommendations                │     │
    │  │ Confidence: 0.80                 │     │
    │  └──────────────────────────────────┘     │
    └────────────────────────────────────────────┘
```

## Data Structure Diagram

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    SPECTRUM PRODUCT DATA STRUCTURE                       ║
╚══════════════════════════════════════════════════════════════════════════╝

SpecProduct
├── HALILIT SOURCE (Primary)
│   ├── halilit_id: "NORD_001"        [From: Halilit API]
│   ├── name: "Nord Lead A1"          [From: Halilit]
│   ├── brand: "Nord"                 [From: Halilit]
│   ├── price_il: 8500.0              [From: Halilit] ⭐ Key
│   ├── price_eilat: 7225.0           [From: Halilit] ⭐ Key
│   └── stock_status: "in_stock"      [From: Halilit]
│
├── OFFICIAL ENRICHMENT (Secondary)
│   └── official_specs: {
│       ├── polyphony: 64             [From: Nord API]
│       ├── voices: 8                 [From: Nord API]
│       ├── connectivity: ["MIDI", "USB"]
│       ├── power_supply: "230V AC"
│       ├── warranty: {
│       │   └── standard_years: 2
│       ├── dimensions: {...}
│       └── weight: 20.5 kg
│   }
│
├── OFFICIAL IMAGES (Secondary)
│   └── official_images: [{
│       ├── type: "hero"
│       ├── url: "/assets/nord_lead_a1_hero.jpg"
│       └── source: "official_manufacturer"
│   }]
│
├── REVIEW ENRICHMENT (Community)
│   └── review_data: {
│       ├── aggregate_rating: 4.7
│       ├── total_reviews: 45
│       ├── sources: ["thomann", "sweetwater", "reverb"]
│       ├── rating_distribution: {
│       │   ├── '5': 32
│       │   ├── '4': 10
│       │   ├── '3': 2
│       │   ├── '2': 1
│       │   └── '1': 0
│       └── pros_and_cons: {
│           ├── pros: ["Great build quality", "Excellent sound"]
│           ├── cons: ["Expensive", "Heavy"]
│           └── verdict: "Highly recommended"
│       }
│   }
│
├── DATA PROVENANCE (Tracking)
│   └── data_provenance: {
│       ├── halilit: {
│       │   ├── source: "Halilit Commerce API"
│       │   ├── confidence: 0.98
│       │   └── url: "https://halilit.com/NORD_001"
│       ├── official: {
│       │   ├── sources: ["nord.com/api"]
│       │   └── confidence: 0.95
│       └── reviews: {
│           ├── sources: ["thomann", "sweetwater", "reverb"]
│           └── confidence: 0.87
│       }
│   }
│
├── METADATA
│   ├── sources: ["halilit_direct", "official_specs", "trusted_reviews"]
│   ├── quality_score: 95.0          (0-100 scale)
│   └── validation_status: "APPROVED" (APPROVED|REVIEW_PENDING|REJECTED)
│
└── QUALITY INDICATORS
    ├── tier: "pro"                  (entry|mid|pro|flagship)
    ├── price_consistency: ✅ PASS   (IL to Eilat ratio check)
    ├── completeness: ✅ PASS         (All fields present)
    └── source_credibility: ✅ PASS   (Multiple sources)
```

## Validation Pipeline Diagram

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    VALIDATION RULE ENGINE                             ║
╚═══════════════════════════════════════════════════════════════════════╝

Product Data Input
        │
        ▼
┌─────────────────────────────────────┐
│ CRITICAL RULES (Must Pass)          │  Weight  Penalty
├─────────────────────────────────────┤
│ 1. Halilit Price Required           │  1.0  →  -10
│    └─ price_il > 0                  │
├─────────────────────────────────────┤
│ 2. Product Name Quality             │  1.0  →  -10
│    └─ len(name) > 3 chars           │
├─────────────────────────────────────┤
│ 3. Brand Consistency                │  0.8  →  -8
│    └─ brand in taxonomy             │
└────────────┬──────────────────────────┘
             │
        ALL PASS?
        /        \
      YES        NO
      │           │
      │    ┌──────▼────────┐
      │    │ REJECT PRODUCT│
      │    │ quality=0     │
      │    └───────────────┘
      │
      ▼
┌──────────────────────────────────┐
│ WARNING RULES (Should Pass)      │  Penalty
├──────────────────────────────────┤
│ 1. Price Consistency             │  -5
│    └─ 0.75 ≤ eilat/il ≤ 0.95    │
├──────────────────────────────────┤
│ 2. Source Credibility            │  -3
│    └─ ≥1 official source         │
├──────────────────────────────────┤
│ 3. Data Provenance               │  -2
│    └─ lineage tracked            │
└────────────┬─────────────────────┘
             │
      ▼──────────────────────┐
      │ Calculate Quality     │
      │ quality = 100 - penalties
      │ quality = clamp(0, 100)
      │
      ▼
     ╔═══════════════════════╗
     ║  Quality Score: 0-100 ║
     ║                       ║
     ║  90-100: Excellent   ║
     ║  80-89:  Good        ║
     ║  70-79:  Acceptable  ║
     ║  60-69:  Needs Work  ║
     ║  <60:    Poor        ║
     ╚═══════════════════════╝
```

## Frontend Component Hierarchy

```
╔═══════════════════════════════════════════════════════════════════════╗
║                      SPECTRUM MODULE LAYOUT                           ║
╚═══════════════════════════════════════════════════════════════════════╝

SpectrumModule (Main Container)
├── TOP DECK (Header)
│   ├── BackButton
│   ├── TitleDisplay ("KEYBOARDS")
│   └── ProductCountBadge
│
├── DATA SCREENS (45vh)
│   ├── LEFT PANEL (4 cols) - Image Preview
│   │   └── ProductImageDisplay
│   │       ├── Product Hero Image
│   │       └── Fallback Text
│   │
│   ├── CENTER PANEL (5 cols) - Information
│   │   ├── ProductHeader
│   │   │   ├── IDRef Badge
│   │   │   ├── ProductName
│   │   │   └── BrandName
│   │   │
│   │   ├── ProductDescription
│   │   │
│   │   ├── SpecificationsGrid
│   │   │   └── 4 Key Specs (from Halilit)
│   │   │
│   │   └── EnrichmentPanel (NEW)
│   │       ├── OfficialSpecsSection
│   │       │   ├── Polyphony
│   │       │   ├── Connectivity
│   │       │   └── Power
│   │       │
│   │       ├── ReviewDataSection
│   │       │   ├── StarRating
│   │       │   ├── ReviewCount
│   │       │   └── ProsCons
│   │       │
│   │       └── DataSourcesSection
│   │           └── DataSourcesBadge
│   │               ├── 🇮🇱 Halilit (Blue)
│   │               ├── ✓ Official (Green)
│   │               └── ★ Reviews (Amber)
│   │
│   └── RIGHT PANEL (3 cols) - Price & Action
│       ├── PriceDisplay (Large)
│       ├── PriceLabel ("Price (VAT Included)")
│       └── AnalyzeButton
│
├── MATRIX AREA (Main - Flex)
│   ├── AxisLabels
│   │   └── "LOW PRICE" → "HIGH PRICE"
│   │
│   └── BrandSwimlanes (Scrollable)
│       ├── Row per Brand
│       │   ├── BrandHeader
│       │   │   └── BrandLogo
│       │   │
│       │   └── Track (Products by Price)
│       │       ├── Product Dot (hover to expand)
│       │       │   ├── OnHover: Expand to show details
│       │       │   ├── OnClick: Open detail panel
│       │       │   └── Y-Axis: Relevance score
│       │       │       X-Axis: Price position
│       │       └── Products ordered left→right by price
│       │
│       └── More Brand Rows...
│
└── BOTTOM DECK (Filter Controls)
    ├── "ALL" Button
    └── Category Filter Buttons
        ├── Keyboards
        ├── Synthesizers
        ├── Modules
        └── etc.
```

## API Request/Response Flow

```
FRONTEND REQUEST:
━━━━━━━━━━━━━━━━━
GET /api/spectrum/data/Nord
  ?include_enrichment=true
  &force_refresh=false

BACKEND PROCESSING:
━━━━━━━━━━━━━━━━━━
SpectrumDataPipeline.execute({
  brand: 'Nord',
  include_enrichment: true,
  force_refresh: false
})

  Phase 1: _scrape_halilit('Nord')
  ├─ Query Halilit API
  ├─ Extract: [
  │   { halilit_id: 'NORD_001', name: 'Lead A1', price_il: 8500, ... },
  │   { halilit_id: 'NORD_002', name: 'Lead A1X', price_il: 9500, ... }
  │ ]
  └─ Return: 12 products

  Phase 2: _organize_by_price_spectrum(products)
  ├─ Categorize by tier:
  │   - entry (0-500)
  │   - mid (500-1500)
  │   - pro (1500-4000)
  │   - flagship (4000+)
  └─ Sort within tier by price

  Phase 3: _enrich_with_official_sources(tracks)
  ├─ For each product:
  │   ├─ OfficialSpecsEnricher.execute()
  │   │   └─ Fetch from Nord API
  │   └─ TrustedReviewAggregator.execute()
  │       ├─ Thomann (35%)
  │       ├─ Sweetwater (35%)
  │       ├─ Reverb (20%)
  │       └─ Gearspace (10%)
  └─ Aggregate specs & reviews

  Phase 4: SpectrumValidator.execute()
  ├─ For each product: validate()
  │   ├─ Check critical rules
  │   ├─ Check warning rules
  │   └─ Calculate quality score
  └─ Quality Score: 95/100 ✅

  Phase 5: _attach_provenance(data)
  └─ Add lineage: halilit → official → reviews

FRONTEND RESPONSE:
━━━━━━━━━━━━━━━━━
{
  "brand": "Nord",
  "timestamp": "2024-02-04T12:00:00Z",
  "total_products": 12,
  "tracks": [
    {
      "tier": "entry",
      "products": [
        {
          "halilit_id": "NORD_001",
          "name": "Nord Lead A1",
          "price_il": 8500,
          "official_specs": {...},
          "review_data": {...},
          "data_provenance": {...},
          "quality_score": 95
        },
        ...
      ]
    },
    ...
  ],
  "metadata": {...}
}

FRONTEND RENDERING:
━━━━━━━━━━━━━━━━━━
1. Organize products by tier (horizontal swimlanes)
2. Position by price (logarithmic X-axis)
3. Hover to show enrichment panel
4. Display official specs, ratings, sources
5. Show quality badges
```

## Quality Score Formula

```
Quality Score = Base (100)
                 - Critical Penalties
                 - Warning Penalties
                 - Clamp to [0, 100]

Critical Penalties (Product REJECTED if any):
  Halilit Price Missing      -10  (Critical)
  Name Too Short             -10  (Critical)
  Brand Not in Taxonomy      -10  (Critical)

Warning Penalties (Product APPROVED but warnings):
  Price Ratio Off            -5   (Product works, but suspicious)
  No Official Source         -3   (Less enriched)
  No Provenance Info         -2   (Tracking missing)

Examples:
  ✅ All pass, no warnings       → 100
  ✅ All pass, 1 warning         → 95-97
  ✅ All pass, 2 warnings        → 92-94
  ✅ All pass, 3 warnings        → 90-92
  ⚠️  Critical fail               → 0 (REJECTED)
```

---

This visual guide shows the complete architecture, data flow, validation process, and UI layout of the Spectrum Screen v5.3.0 system.
