# Halilit Support Center

**Version 5.0** - Unified Data Pipeline Architecture

A modern product catalog and support center for professional audio equipment. Built with a "Static First" architecture where the backend generates optimized JSON files that the frontend consumes directly.

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         3 DATA SOURCES                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  OFFICIAL          │  COMMERCIAL         │  CONTEXTUAL                  │
│  (Manufacturer)    │  (Halilit Prices)   │  (Expert Reviews)            │
│  - Product specs   │  - SKU numbers      │  - Pros/Cons                 │
│  - Names, images   │  - Prices (ILS/USD) │  - Expert tips               │
│  - Manuals, docs   │  - Stock status     │  - Known issues              │
└──────────┬─────────┴──────────┬──────────┴──────────┬────────────────────┘
           │                    │                     │
           └────────────────────┼─────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      3 PROCESSING LAYERS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 1: NORMALIZE    │  LAYER 2: ENRICH      │  LAYER 3: OPTIMIZE     │
│  - Pydantic validation │  - Taxonomy mapping   │  - UI constraints      │
│  - Schema enforcement  │  - Tier assignment    │  - Slug generation     │
│  - Content hashing     │  - Image selection    │  - Search text         │
└────────────────────────┴───────────────────────┴────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT: frontend/public/data/                    │
│  index.json        - Brand catalog index                                │
│  {brand}.json      - Per-brand product catalogs                         │
└─────────────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│  React + Vite + TypeScript + Tailwind                                   │
│  Loads static JSON → Galaxy Dashboard → Spectrum View → Product Modal   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ / pnpm
- (Optional) Playwright for web scraping: `pip install playwright && playwright install`

### Installation

```bash
# Clone repository
git clone https://github.com/oripridan-dot/Halilit-Support-Center.git
cd Halilit-Support-Center

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
pnpm install
```

### Running the Pipeline

```bash
# Run complete pipeline (ingest → process → deploy)
python -m backend.pipeline run

# Run specific stages
python -m backend.pipeline ingest    # Only harvest data
python -m backend.pipeline process   # Only process through layers
python -m backend.pipeline deploy    # Only deploy to frontend

# Check status
python -m backend.pipeline status

# Generate TypeScript types
python -m backend.pipeline types
```

### Running the Frontend

```bash
cd frontend
pnpm dev    # Development server at http://localhost:5173
pnpm build  # Production build
```

## 📁 Project Structure

```
├── backend/
│   ├── pipeline/              # ⭐ MAIN PIPELINE (v5.0)
│   │   ├── __main__.py       # CLI entry point
│   │   ├── config.py         # Configuration
│   │   ├── models.py         # Pydantic schemas
│   │   ├── runner.py         # Pipeline orchestrator
│   │   ├── typescript_generator.py
│   │   ├── harvesters/       # Data ingestion
│   │   │   ├── official.py   # Manufacturer data
│   │   │   ├── commercial.py # Halilit prices
│   │   │   └── contextual.py # Reviews (real web search + AI)
│   │   └── layers/           # Processing layers
│   │       ├── normalize.py  # Layer 1
│   │       ├── enrich.py     # Layer 2
│   │       └── optimize.py   # Layer 3
│   ├── data/
│   │   ├── 1_official/       # Raw official data
│   │   ├── 2_commercial/     # Raw commercial data
│   │   ├── 3_contextual/     # Raw contextual data
│   │   ├── 4_validated/      # After layer processing
│   │   ├── 5_golden/         # Production-ready catalogs
│   │   └── reports/          # Pipeline reports
│   ├── scripts/              # Utility scripts
│   └── tests/                # Test suites
│
├── frontend/
│   ├── public/data/          # Static JSON (pipeline output)
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page views
│   │   └── types/            # TypeScript types (auto-generated)
│   └── package.json
│
└── docs/                     # Additional documentation
```

## 🔧 Configuration

### Environment Variables

```bash
# For real web search in Context Agent
export SERP_API_KEY=your_serpapi_key

# For AI synthesis of reviews
export OPENAI_API_KEY=your_openai_key

# Pipeline settings
export PIPELINE_DEBUG=true
export PIPELINE_SCRAPER_HEADLESS=false
```

### Pipeline Configuration

Edit `backend/pipeline/config.py` to customize paths, scraper settings, and tier thresholds.

## 🧪 Testing

```bash
# Run all tests
python -m pytest backend/tests/ -v

# Run specific test
python -m pytest backend/tests/test_pipeline_e2e.py -v

# Frontend tests
cd frontend && pnpm test
```

## 📊 Data Quality Tiers

Products are automatically assigned quality tiers based on data completeness:

| Tier       | Score | Requirements                             |
| ---------- | ----- | ---------------------------------------- |
| 💎 Diamond | 75+   | Complete data, verified, multiple images |
| 🥇 Gold    | 60-74 | Good data, minor gaps                    |
| 🥈 Silver  | 40-59 | Basic data, needs enrichment             |
| 🥉 Bronze  | 0-39  | Minimal data                             |

## 🔄 Data Flow

1. **Ingest**: Harvesters collect data from 3 sources
2. **Normalize**: Merge and validate against Pydantic schemas
3. **Enrich**: Map taxonomy, assign tiers, select images
4. **Optimize**: Generate slugs, search text, render hints
5. **Deploy**: Write to `frontend/public/data/`
6. **Types**: Auto-generate TypeScript types

## 📖 Documentation

- [Architecture Guide](ARCHITECTURE_v5.md)
- [Getting Started](GETTING_STARTED_v5.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE_v5.md)
- [Operations Manual](OPERATIONS.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests before committing
4. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details.
