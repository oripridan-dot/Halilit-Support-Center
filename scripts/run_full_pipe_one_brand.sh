#!/usr/bin/env bash
# Full ingestion pipeline for ONE brand: commercial → enrich (with visual validation) → sync → relationships.
# Usage: ./scripts/run_full_pipe_one_brand.sh [BRAND] [--fast] [--validate-images]
#   BRAND: display name for commercial-ingest (e.g. "Bespeco", "Roland"), and stem for enrich/sync (e.g. "bespeco")
#   If omitted, uses "Bespeco" / "bespeco" as an easy small brand.
#
#   --fast              Skip ALL image validation (fastest; new images go in unvalidated)
#   --validate-images   Force full image validation even for cached URLs (re-validation run)
#
# Default behaviour: use the persistent URL cache (7-day TTL) — already-validated
# images are accepted instantly, only new/expired URLs are fetched and checked.
#
# Requires: Halilit.com reachable for commercial-ingest (sitemap) and enrich (product pages).

set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
export PYTHONPATH="$ROOT"
PY="${PY:-.venv/bin/python}"

# ── Parse flags ──────────────────────────────────────────────────────────────
BRAND_DISPLAY=""
FAST_MODE=false
FORCE_VALIDATE=false
for arg in "$@"; do
    case "$arg" in
        --fast)              FAST_MODE=true ;;
        --validate-images)   FORCE_VALIDATE=true ;;
        *)                   [[ -z "$BRAND_DISPLAY" ]] && BRAND_DISPLAY="$arg" ;;
    esac
done
BRAND_DISPLAY="${BRAND_DISPLAY:-Bespeco}"

if [[ "$FAST_MODE" == "true" ]]; then
    export INGESTION_SKIP_VISUAL_VALIDATION=1
    echo "⚡ Fast mode: image validation DISABLED"
elif [[ "$FORCE_VALIDATE" == "true" ]]; then
    export INGESTION_SKIP_VISUAL_VALIDATION=0
    # Clear the image validation cache for this brand so every URL is re-checked
    python3 -c "
import json, pathlib, re, sys
cache_path = pathlib.Path('backend/data/jit_cache/image_validation_cache.json')
if cache_path.exists():
    cache = json.loads(cache_path.read_text())
    brand_slug = '${BRAND_DISPLAY}'.lower()
    removed = [k for k in list(cache) if brand_slug in k.lower()]
    for k in removed: del cache[k]
    cache_path.write_text(json.dumps(cache, indent=2))
    print(f'   Cleared {len(removed)} cached entries for {brand_slug}')
" 2>/dev/null || true
    echo "🔍 Force-validate mode: ALL images will be re-checked"
else
    echo "📦 Cache mode: previously validated images skipped (7-day TTL)"
fi

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
