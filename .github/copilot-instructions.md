# Repository Instructions & Context

## Project Overview

This repository hosts the "Halilit Support Center" v5.0.

- **Architecture**: "Static First". The backend pipeline generates static JSON assets that the frontend consumes directly.
- **Frontend**: Located in `frontend/`. Built with Vite, React, TypeScript, and Tailwind CSS.
- **Backend**: Located in `backend/`. Single unified pipeline at `backend/pipeline/` processes data from 3 sources through 3 layers.

## Pipeline Architecture (v5.0)

### Three Data Sources

1. **Official** - Manufacturer data (specs, names, images, manuals)
2. **Commercial** - Halilit website (prices, SKUs, stock status)
3. **Contextual** - Expert reviews via web search + AI synthesis (pros, cons, tips)

### Three Processing Layers

1. **Normalize** - Merge & validate with Pydantic schemas
2. **Enrich** - Taxonomy mapping, tier assignment (Diamond/Gold/Silver/Bronze)
3. **Optimize** - UI-ready JSON with slugs, search text, render hints

### Running the Pipeline

```bash
python -m backend.pipeline run        # Full pipeline
python -m backend.pipeline status     # Check status
python -m backend.pipeline types      # Generate TypeScript types
```

## Tech Stack

- **Frontend**:
  - Framework: React 18
  - Build Tool: Vite
  - Language: TypeScript
  - Styling: Tailwind CSS
  - Package Manager: pnpm
- **Backend**:
  - Language: Python 3.11+
  - Key Libraries: Pydantic v2, Playwright (web scraping), httpx, openai

## Conventions & Patterns

- **Data Access**: The frontend reads static JSON files from `/data` (mapped to `frontend/public/data`). It does not call a dynamic API at runtime for catalog data.
- **Routing**: Frontend uses client-side routing.
- **File Structure**:
  - `backend/pipeline/`: Main pipeline (harvesters, layers, models)
  - `backend/data/`: Data storage (1_official, 2_commercial, 3_contextual, 4_validated, 5_golden)
  - `frontend/src/types/generated.ts`: Auto-generated TypeScript types from Pydantic models
  - `frontend/public/data`: Pipeline output (index.json + per-brand catalogs)
- **Git**: Large asset folders (`product_images`, `thumbnails`) are git-ignored.

## Code Style

- Use functional React components with hooks.
- Use strong typing in TypeScript (auto-generated from backend models).
- Python code follows Pydantic v2 patterns.
- Pipeline CLI is the single entry point for all data processing.
