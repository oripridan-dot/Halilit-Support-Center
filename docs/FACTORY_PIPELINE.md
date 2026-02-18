# Factory Pipeline

How to run the app and the data pipeline. One place for all run and Conductor commands.

---

## Scripts (root)

| Script | Purpose |
|--------|---------|
| `./factory_reset.sh` | Start backend + frontend; checks catalog artifact. |
| `./factory_reset.sh --rebuild` | Rebuild catalog then start. |
| `./start_console.sh` | Alternative: venv, deps, then backend + frontend. |
| `./start.command` | Mac double-click: runs `factory_reset.sh`. |
| `./clear_all_caches.sh` | Clear frontend/backend caches; then restart. |
| `./rebuild_all.sh [brand]` | Enrich (all or one brand) → rebuild-catalog → check_data_status. |
| `./check_data_status.sh` | Quick check: sample brand file enrichment. |
| `./test_functionality.sh` | Require servers running: health + catalog + search API. |
| `python3 test_pipeline.py` | Optional: file structure + catalog build outcome (run from root). |

Legacy verification scripts (`verify_running_code.sh`, `validate_integration.sh`) were removed; use outcome checks above and `specs/` + golden scenarios.

---

## Run the App

### Option A: Factory script (recommended)

```bash
# From project root
./factory_reset.sh
```

- Checks that a catalog artifact exists (`backend/data/learned_taxonomy.json` or `backend/data/catalog_cache.json.gz`).
- Starts backend (port 8000) and frontend (port 5173).
- If no artifact: run `./factory_reset.sh --rebuild` first.

### Option B: Rebuild catalog then run

```bash
./factory_reset.sh --rebuild
```

- Runs `conductor_main.py rebuild-catalog`, then starts both servers.
- Use when you’ve re-ingested or changed data and want a fresh catalog.

### Option C: Existing console script

```bash
./start_console.sh
```

- Uses your existing startup (venv, deps, backend then frontend).
- Does not run rebuild unless you run Conductor separately.

---

## Conductor Commands (Data Pipeline)

From project root, with venv activated and `PYTHONPATH=.`:

| Command | Description |
|---------|-------------|
| `python backend/conductor_main.py skeleton-sync` | Fast inventory from Halilit (~30s). |
| `python backend/conductor_main.py commercial-ingest [brand]` | Ingest one or all brands. |
| `python backend/conductor_main.py commercial-ingest "Roland" --try-scrape` | Single-brand test with page scrape. |
| `python backend/conductor_main.py commercial-ingest --try-scrape --workers 4` | Full re-scrape, parallel (hours). |
| `python backend/conductor_main.py enrich [brand]` | Enrich from Halilit product pages. |
| `python backend/conductor_main.py ingest-all` | Full pipeline: commercial → enrich → sync → rebuild-catalog. |
| `python backend/conductor_main.py sync` | Rebuild frontend data from brand JSONs. |
| `python backend/conductor_main.py rebuild-catalog` | Rebuild catalog + product graph. |
| `python backend/conductor_main.py catalog` | Print catalog stats. |
| `python backend/conductor_main.py dev` | Start backend + frontend (alternative to factory_reset.sh). |

**Example: test one brand then rebuild**

```bash
source .venv/bin/activate
export PYTHONPATH=.
python backend/conductor_main.py commercial-ingest "adam audio" --try-scrape
python backend/conductor_main.py rebuild-catalog
./factory_reset.sh
```

---

## After Re-scraping

1. Rebuild catalog: `python backend/conductor_main.py rebuild-catalog`
2. Optionally prebuild cache for fast first load: `python backend/scripts/prebuild_catalog_cache.py`
3. Start app: `./factory_reset.sh`

---

## Validation

- **Artifact check:** `factory_reset.sh` ensures at least one of `backend/data/learned_taxonomy.json` or `backend/data/catalog_cache.json.gz` exists before starting.
- **Golden scenarios:** Relationship and data quality are validated against `backend/tests/golden_scenarios.json`. Use the "Compliance Report" prompt (see [SPEC_DRIVEN_DEVELOPMENT.md](SPEC_DRIVEN_DEVELOPMENT.md)) to compare catalog vs golden set; no code review—approve the data.
- **Optional pipeline check:** From project root, `python3 test_pipeline.py` runs file-structure and catalog-build outcome checks. Use `./test_functionality.sh` when servers are running for API/health checks.

---

## Specs for the Pipeline

- Ingestion and normalization: `specs/data_pipeline/01_ingestion_rules.md`
- Relationships and golden scenarios: `specs/data_pipeline/02_relationship_logic.md`
- Pricing: `specs/pricing_logic.md`
