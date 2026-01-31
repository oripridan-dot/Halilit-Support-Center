# Halilit Support Center

**Version:** 4.6.1
**Status:** Data Refinement & Optimization Complete (100% Diamond Tier, Fully Synced)
**Database:** Synchronized & Optimized (WAL mode, Indexed, 100% Audit Trail)

## Overview

The Halilit Support Center is a "Static First" web application designed to showcase musical instruments with high-fidelity visuals.

**v4.6 Final** delivers the complete "Data Refinery" with full database synchronization and optimization. A strict ingestion pipeline ensures only "Diamond Tier" badged data is loaded, with 100% sync between SQLite history and processed JSON cache. All 114+ products across 6 brands are now fully optimized and visible in the UI.

## Architecture

- **Frontend**: React 18, Vite, TypeScript. **Strictly Typed & Gated**.
- **Backend**: Python Data Refinery & Monitoring.
  - `ingest_brand.py`: Raw Harvest with DB Tracking.
  - `refine_brand.py`: Cleaning, Taxonomy Mapping & Tier Assignment.
  - `deploy_badged_catalog.py`: Index Generation.
  - `tracker.py` & `db.py`: SQLite History & Sync.
- **Data**: Static JSONs in `frontend/public/data` (100% synced with SQLite).
- **Database**: SQLite (WAL mode, indexed) for audit trail and change detection.

## Key Features

- **Galaxy Dashboard**: Context-aware grid that greys out empty categories.
- **Tier Bar**: Physics-based scatter plot for product visualization.
- **Smart Filters**: "1176" style buttons that toggle sub-categories instantly.

## Development

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173/

### Backend (Refinement Pipeline)

```bash
# 1. Harvest & Refine a brand (Full pipeline with DB tracking)
python3 backend/scripts/ingest_brand.py adam-audio

# 2. OR refine already-processed data
python3 backend/scripts/refine_brand.py adam-audio

# 3. Update frontend index
python3 backend/scripts/deploy_badged_catalog.py
```

### Database Verification

```bash
python3 -c "
import json, sqlite3
from pathlib import Path

conn = sqlite3.connect('backend/data/ingestion_history.db')
c = conn.cursor()
for row in c.execute('SELECT brand_id, COUNT(*) FROM product_snapshots GROUP BY brand_id'):
    print(f'{row[0]}: {row[1]} snapshots')
conn.close()
"
```

## Project Structure

- `frontend/src/components/views`: Main page views (Galaxy, Spectrum, etc).
- `frontend/src/lib`: Core logic (Category mapping, brand extraction).
- `frontend/public/data`: Generated catalogs.
