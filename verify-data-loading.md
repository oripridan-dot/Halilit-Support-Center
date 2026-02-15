# Verify New Data Is Loading (v9.2)

See also [IMPLEMENTATION-COMPLETE.md](IMPLEMENTATION-COMPLETE.md) for full run/verify steps.

## Data on disk (already verified)

- **`frontend/public/data/index.json`**: 7,911 products, 192 brands, build timestamp `2026-02-15T10:47:59` (from commercial ingest + index rebuild).
- Brand JSONs in `frontend/public/data/*.json` are present and many were updated during ingestion (e.g. `roland.json`, `nord.json`, `allen heath.json`).

## Run the app

From **project root** with venv activated:

```bash
source .venv/bin/activate   # or: . .venv/bin/activate
./start.sh
```

- Backend: http://localhost:8000  
- Frontend: http://localhost:5173 (or 5174 if 5173 is in use)  
- Browser should open automatically; if not, open http://localhost:5173

## Confirm new data is loading

1. **Galaxy screen**  
   You should see category tiles with non-zero product counts (e.g. "Guitars & Bass", "Studio & Recording") and a total around **7,911 products**. The header may show a health score and "X products".

2. **Spectrum screen**  
   Click any subcategory (e.g. "Electric Guitars"). The product grid should show real products with images, prices, and brands (not "sample" or empty).

3. **Backend catalog (optional)**  
   In another terminal:
   ```bash
   curl -s "http://localhost:8000/api/conductor/catalog" | python3 -c "
   import sys, json
   d = json.load(sys.stdin)
   m = d.get('metadata', {})
   print('Products:', m.get('total_products'), '| Brands:', len(m.get('brands', [])), '| Galaxies:', len(m.get('galaxy_counts', {})))
   "
   ```
   First request can take 30–60 seconds while the catalog is built; later requests are cached (~5 min).

## If you see "sample data" or empty catalog

- Run full pipeline: `PYTHONPATH=. python backend/conductor_main.py ingest-all` (then optionally `rebuild-catalog`).
- Or: `commercial-ingest` then `enrich`; then `rebuild-catalog` to refresh catalog and graph.
- Restart the backend so it picks up the new files (Ctrl+C, then `./start.sh` or `conductor_main.py dev` again).
