# Backend Tools

**Status:** Data Refinement & Synchronization Pipeline (v4.6.1)

## Overview

The backend is a complete data ingestion and refinement system:
1. Harvests raw data from web sources (Halilit, Official sites)
2. Processes and cleans the data
3. Applies strict taxonomy mapping
4. Assigns quality tiers (Diamond, Gold, Silver, Bronze)
5. Tracks all operations in SQLite for 100% audit trail
6. Deploys refined data to frontend cache

## Database & Synchronization

**Location:** `backend/data/ingestion_history.db`

**Optimization:** WAL mode + Indexes + Vacuumed
**Sync Status:** 100% (All 114+ products synchronized)

## Available Scripts

`ingest_brand.py`: Full pipeline with DB tracking

```bash
python3 backend/scripts/ingest_brand.py adam-audio
```

`refine_brand.py`: Refine processed data

```bash
python3 backend/scripts/refine_brand.py adam-audio
```

`deploy_badged_catalog.py`: Update frontend index

```bash
python3 backend/scripts/deploy_badged_catalog.py
```

## Setup

```bash
pip install -r requirements.txt
```
