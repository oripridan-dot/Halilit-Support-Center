# Halilit Support Center

**Version:** 4.6
**Status:** Data Refinement & Optimization

## Overview

The Halilit Support Center is a "Static First" web application designed to showcase musical instruments with high-fidelity visuals, without requiring a dynamic backend at runtime.

## Architecture

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS.
- **Backend**: Python scripts for data ingestion and static asset generation (HTML/JSON).
- **Filesystem**: Data is served from `public/data`.

## Key Features

- **Galaxy Dashboard**: 6-sector grid navigation.
- **Spectrum Module**: Detailed product listing with tier-based sorting.

## Development

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend (Data Generation)

```bash
cd backend
pip install -r requirements.txt
python generate_backgrounds.py
```

## Project Structure

- `frontend/src/components/views`: Main page views (Galaxy, Spectrum, etc).
- `frontend/src/lib`: Core logic (Category mapping, brand extraction).
- `frontend/public/data`: Generated catalogs.
