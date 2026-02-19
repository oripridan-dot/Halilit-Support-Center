#!/usr/bin/env bash
# Full ingestion pipeline for ONE brand: commercial → enrich (with visual validation) → sync → relationships.
# Usage: ./scripts/run_full_pipe_one_brand.sh [BRAND]
#   BRAND: display name for commercial-ingest (e.g. "Bespeco", "Roland"), and stem for enrich/sync (e.g. "bespeco").
#   If omitted, uses "Bespeco" / "bespeco" as an easy small brand.
#
# Requires: Halilit.com reachable for commercial-ingest (sitemap) and enrich (product pages).
# Set INGESTION_SKIP_VISUAL_VALIDATION=1 to skip image validation (faster).

set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
export PYTHONPATH="$ROOT"
PY="${PY:-.venv/bin/python}"

BRAND_DISPLAY="${1:-Bespeco}"
# Slug for file names (enrich/sync use stem)
BRAND_SLUG=$(echo "$BRAND_DISPLAY" | tr '[:upper:]' '[:lower:]' | tr -s ' ' '-' | sed 's/[^a-z0-9-]//g')

echo "=============================================="
echo "  Full pipe: $BRAND_DISPLAY ($BRAND_SLUG)"
echo "  1. Commercial ingest  2. Enrich (validation)"
echo "  3. Sync               4. Rebuild catalog/graph"
echo "=============================================="

echo ""
echo "[1/4] Commercial ingest (Golden List, optional page scrape)..."
"$PY" backend/conductor_main.py commercial-ingest "$BRAND_DISPLAY" --try-scrape || true

echo ""
echo "[2/4] Enrich (Halilit pages + visual validation)..."
"$PY" backend/conductor_main.py enrich "$BRAND_SLUG" --delay 0.4 --concurrent-products 4

echo ""
echo "[3/4] Sync to frontend..."
"$PY" backend/conductor_main.py sync "$BRAND_SLUG"

echo ""
echo "[4/4] Rebuild catalog and relationship graph..."
"$PY" backend/conductor_main.py rebuild-catalog

echo ""
echo "=============================================="
echo "  Full pipe complete for $BRAND_DISPLAY"
echo "=============================================="
"$PY" backend/conductor_main.py catalog
