# Repository Instructions & Context

## Project Overview
This repository hosts the "Halilit Support Center".
- **Architecture**: "Static First". The backend generates static assets (JSON, images) that the frontend consumes directly.
- **Frontend**: Located in `frontend/`. Built with Vite, React, TypeScript, and Tailwind CSS.
- **Backend**: Located in `backend/`. Python scripts primarily used for data ingestion ("Mass Ingest Protocol"), processing, and generating the static "Backbone" (JSON catalog).

## Tech Stack
- **Frontend**: 
  - Framework: React 18
  - Build Tool: Vite
  - Language: TypeScript
  - Styling: Tailwind CSS
  - Package Manager: pnpm
- **Backend**: 
  - Language: Python 3.x
  - Key Libraries: Pydantic (for models)

## Conventions & Patterns
- **Data Access**: The frontend reads static JSON files from `/data` (mapped to `frontend/public/data`). It does not call a dynamic API at runtime for catalog data.
- **Routing**: Frontend uses client-side routing.
- **File Structure**:
  - `frontend/src/components`: Reusable UI components.
  - `frontend/src/pages`: Page views.
  - `frontend/public/data`: Generated static data (catalog.json, etc.).
- **Git**: Large asset folders (`product_images`, `thumbnails`) are git-ignored.

## Code Style
- Use functional React components with hooks.
- Use strong typing in TypeScript.
- Python scripts should be modular and run from the `backend/` directory or root as configured.
