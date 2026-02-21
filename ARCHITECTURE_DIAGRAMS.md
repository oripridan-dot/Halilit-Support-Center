# Scraping Architecture Diagram

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HALILIT VS THOMANN SCRAPING PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   START PIPELINE │
                              │  orchestrator.py │
                              └────────┬─────────┘
                                       │
                  ┌────────────────────┼────────────────────┐
                  │                    │                    │
                  ▼                    ▼                    ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │    PHASE 1       │  │    PHASE 2       │  │    PHASE 3       │
        │  EXTRACT HALILIT │  │ SCRAPE THOMANN   │  │  PROCESS & MATCH │
        └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
                 │                     │                     │
                 │                     │                     │
    ┌────────────▼─────────────┐       │                     │
    │ halilit_full_extractor   │       │                     │
    │         .py              │       │                     │
    └────────┬─────────────────┘       │                     │
             │                         │                     │
    ┌────────▼──────────────────────┐  │                     │
    │ METHOD 1: JSON Files (2 min)   │  │                     │
    │ frontend/public/data/*.json    │  │                     │
    │ └─ 25 RCF products            │  │                     │
    │ └─ 25 Mackie products         │  │                     │
    │                                │  │                     │
    │ FALLBACK: METHOD 2: Database   │  │                     │
    │ backend/scrapers/*.db          │  │                     │
    │                                │  │                     │
    │ FALLBACK: METHOD 3: API (manu) │  │                     │
    │ Reverse engineer from browser  │  │                     │
    │                                │  │                     │
    │ FALLBACK: METHOD 4: Selenium   │  │                     │
    │ Automate browser (30-60 min)   │  │                     │
    └────────┬──────────────────────┘  │                     │
             │                         │                     │
    ┌────────▼──────────────────────┐  │                     │
    │ halilit_rcf_full.json          │  │                     │
    │ halilit_mackie_full.json       │  │                     │
    │ halilit_full_merged.json       │  │                     │
    └────────┬──────────────────────┘  │                     │
             │                         │                     │
             │                ┌────────▼──────────────────┐  │
             │                │ thomann_full_catalog_     │  │
             │                │ scraper.py (5-10 min)     │  │
             │                └────────┬──────────────────┘  │
             │                         │                     │
             │                ┌────────▼──────────────────┐  │
             │                │ FETCH RCF CATEGORY        │  │
             │                │ thomannmusic.com/rcf.html │  │
             │                │ └─ Parse pagination       │  │
             │                │ └─ Extract 80-150+ prod   │  │
             │                │                            │  │
             │                │ FETCH MACKIE CATEGORY     │  │
             │                │ thomannmusic.com/mackie.. │  │
             │                │ └─ Parse pagination       │  │
             │                │ └─ Extract 80-150+ prod   │  │
             │                │                            │  │
             │                │ DEDUPLICATE               │  │
             │                │ └─ Remove exact dups      │  │
             │                └────────┬──────────────────┘  │
             │                         │                     │
             │                ┌────────▼──────────────────┐  │
             │                │ thomann_rcf_full.json      │  │
             │                │ thomann_mackie_full.json   │  │
             │                │ thomann_full_merged.json   │  │
             │                └────────┬──────────────────┘  │
             │                         │                     │
             └─────────────────────────┼─────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │  data_processor.py  │
                            │  (2 minutes)        │
                            └──────────┬──────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     │                 │                 │
        ┌────────────▼──────────┐      │                 │
        │ LOAD DATA             │      │                 │
        │ Halilit: 25+ RCF+     │      │                 │
        │ Thomann: 80-150+ RCF+ │      │                 │
        └────────────┬──────────┘      │                 │
                     │                 │                 │
        ┌────────────▼──────────┐      │                 │
        │ FUZZY MATCHING        │      │                 │
        │ (60%+ threshold)      │      │                 │
        │ Compare names: │      │      │                 │
        │ SequenceMatcher       │      │                 │
        │ Result: ~70-80% match │      │                 │
        └────────────┬──────────┘      │                 │
                     │                 │                 │
        ┌────────────▼──────────┐      │                 │
        │ PRICE COMPARISON      │      │                 │
        │ USD vs ILS (÷3.7)     │      │                 │
        │ Find cheaper platform │      │                 │
        └────────────┬──────────┘      │                 │
                     │                 │                 │
                     │    ┌────────────▼────────────┐    │
                     │    │ GENERATE REPORTS        │    │
                     │    │ (CSV + JSON)            │    │
                     │    └────────────┬────────────┘    │
                     │                 │                 │
          ┌──────────┴──────┐   ┌──────┴─────────────┐  │
          │                 │   │                    │  │
   ┌──────▼──────┐   ┌──────▼──────┐  ┌─────────────▼──┘
   │     CSV     │   │     CSV     │  │
   │ rcf_        │   │ mackie_     │  │
   │comparison...│   │comparison...│  │
   │  _detailed  │   │  _detailed  │  │
   │  .csv       │   │  .csv       │  │
   └──────┬──────┘   └──────┬──────┘  │ (output dir)
          │                 │         │
          │    ┌────────────▼────────┐│
          │    │ comparison_summary  ││
          │    │ .json               ││
          │    │ Statistics:         ││
          │    │ - Total products    ││
          │    │ - Match counts      ││
          │    │ - Price analysis    ││
          │    └────────────────────┘│
          │                          │
          └──────────────┬───────────┘
                         │
                    ┌────▼─────┐
                    │ SUCCESS! │
                    │ Reports  │
                    │ in:      │
                    │ backend/ │
                    │ reports/ │
                    └──────────┘
```

## Data Structure Diagram

```
INPUT SOURCES:
┌─────────────────────────────────────────────────────┐
│                    HALILIT                          │
│  ┌──────────────────────────────────────────────┐   │
│  │ Method 1: JSON Files (FAST)                 │   │
│  │ frontend/public/data/                       │   │
│  │  ├─ rcf.json (25 products)                  │   │
│  │  └─ mackie.json (25 products)               │   │
│  │                                              │   │
│  │ Method 2: Database (MEDIUM)                 │   │
│  │ backend/scrapers/products.db                │   │
│  │                                              │   │
│  │ Method 3: API (MANUAL)                      │   │
│  │ Requires reverse engineering                │   │
│  │                                              │   │
│  │ Method 4: Selenium (SLOW)                   │   │
│  │ Automate browser scraping                   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    THOMANN                          │
│  ┌──────────────────────────────────────────────┐   │
│  │ Method: Full-Catalog Web Scraping (FAST)    │   │
│  │ Tools: cloudscraper + BeautifulSoup         │   │
│  │                                              │   │
│  │ RCF Category:                               │   │
│  │ thomannmusic.com/rcf.html                   │   │
│  │ ├─ Pagination handling                      │   │
│  │ ├─ Extract names, prices, URLs              │   │
│  │ └─ Expected: 80-150+ products               │   │
│  │                                              │   │
│  │ Mackie Category:                            │   │
│  │ thomannmusic.com/mackie.html                │   │
│  │ ├─ Pagination handling                      │   │
│  │ ├─ Extract names, prices, URLs              │   │
│  │ └─ Expected: 80-150+ products               │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

PROCESSING:
┌─────────────────────────────────────────────────────┐
│            DATA MERGER & DEDUPLICATION              │
│                                                      │
│ Step 1: Load all products                          │
│ ├─ Halilit RCF (25+) ─┐                            │
│ ├─ Halilit Mackie (25+) ├──▶ Merge & Normalize    │
│ ├─ Thomann RCF (80-150+) ├──▶ Deduplicate         │
│ └─ Thomann Mackie (80-150+)                        │
│                                                      │
│ Step 2: Normalize fields                           │
│ ├─ Standardize product names                       │
│ ├─ Convert prices (ILS → USD)                      │
│ ├─ Extract URLs and IDs                            │
│ └─ Validate required fields                        │
│                                                      │
│ Step 3: Deduplicate                                │
│ ├─ Remove exact duplicates (same name + price)     │
│ ├─ Keep first occurrence                           │
│ └─ Merge pricing data when available               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          FUZZY PRODUCT MATCHING                     │
│                                                      │
│ For each Thomann product:                          │
│ ├─ Find best match in Halilit                      │
│ ├─ Algorithm: SequenceMatcher (difflib)            │
│ ├─ Threshold: 60%  (configurable)                  │
│ └─ Output: Match confidence score (0-100%)         │
│                                                      │
│ Example:                                            │
│ "RCF EVOX 12" (Thomann)                            │
│ ├─ vs "RCF F 12XR" (Halilit) = 67% match          │
│ ├─ vs "RCF EVOX J8" (Halilit) = 45% match         │
│ └─ Best: 67% (F 12XR) ✓ MATCHED                    │
└─────────────────────────────────────────────────────┘

OUTPUT REPORTS:
┌──────────────────────────────────────────────────────┐
│            Generated CSV Reports                     │
│  backend/reports/                                   │
│  ├─ rcf_comparison_detailed.csv (50-150+ rows)      │
│  │  Columns: Brand, Product Names, Prices (USD/ILS) │
│  │  Price Difference, Cheaper Platform, Confidence  │
│  │                                                   │
│  ├─ mackie_comparison_detailed.csv (50-150+ rows)   │
│  │  (Same structure as RCF)                         │
│  │                                                   │
│  └─ comparison_summary.json                         │
│     ├─ Total products per brand                     │
│     ├─ Match rates (%)                              │
│     ├─ Price statistics                             │
│     └─ Availability by platform                     │
└──────────────────────────────────────────────────────┘
```

## Execution Timeline

```
START
  │
  ├─ PHASE 1: Halilit Extraction (2-60 min)
  │  ├─ Try JSON files ────────┐
  │  │  [1 min] → Success     │
  │  │            └─ 25 RCF   │
  │  │               25 Mackie│
  │  │                        │
  │  ├─ Try Database ──────────┤ (if JSON insufficient)
  │  │  [2 min] → Try it      │
  │  │                        │
  │  ├─ Try API Reverse Eng ───┤ (manual discovery needed)
  │  │  [10-20 min] → Report   │ to user
  │  │                        │
  │  └─ Fallback: Selenium ────┘ (last resort)
  │     [30-60 min] → Slow but reliable
  │
  ├─ PHASE 2: Thomann Scraping (5-10 min)
  │  ├─ Fetch RCF category ──────┐
  │  │  [2 min] → 80-150+ prod  │
  │  ├─ Fetch Mackie category ────┤
  │  │  [2 min] → 80-150+ prod  │
  │  └─ Deduplicate ─────────────┘
  │     [1 min]
  │
  ├─ PHASE 3: Data Processing (2-5 min)
  │  ├─ Load all data ────────┐
  │  ├─ Fuzzy matching ───────┤
  │  ├─ Price comparison ──────┤
  │  └─ Generate reports ──────┘
  │
  └─ SUCCESS
     Output: 3+ CSV files + JSON summary
     In: backend/reports/
```

## Matching Confidence Levels

```
Product Matching Examples:

High Confidence (95%+):
  "Mackie ProFX16v3" (Thomann) ──▶ "+Mackie ProFX6v3" (Halilit)
  Confidence: 94% ✓ MATCH

Medium Confidence (50-80%):
  "RCF EVOX 12" (Thomann) ──▶ "RCF F 12XR" (Halilit)
  Confidence: 67% ✓ MATCH

Low Confidence (40-50%):
  "RCF EVOX J8 B-Stock" ──▶ "RCF ART 708-A MK5"
  Confidence: 44% ✓ MATCH (still above 40% threshold)

No Match (< 40%):
  "Thomann Product" ──X──▶ "No similar Halilit product"
  Best confidence: 25% ✗ REJECTED (below 60% threshold)

Threshold is configurable:
  - 40% = Lenient (many matches, some false positives)
  - 60% = Balanced (standard, recommended)
  - 80% = Strict (fewer matches, high confidence)
```

---

This diagram shows the complete flow from source data through collection, processing, matching, and final reporting. All components work together in the pipeline orchestrator.
