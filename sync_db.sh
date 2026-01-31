#!/bin/bash

# HALILIT DEV SYNC TOOL
# ---------------------
# Keeps DB (Raw/Processed) and CACHE (Frontend Assets) optimized and synced.

echo "🔄 [SYNC] Starting Development Sync..."

# 1. CLEAN CACHES (ensure no stale python or vite artifacts)
echo "🧹 [CLEAN] Cleaning runtime caches..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf frontend/.vite
echo "   cache cleared."

# 2. RUN REFINERY ON ALL ACTIVE BRANDS
# This ensures backend/data/processed matches raw logic
echo "🏭 [DB] Running Refinery on all brands..."
BRANDS="adam-audio warm-audio amphion bespeco fzone drumdots"

for brand in $BRANDS; do
    echo "   -> Refining $brand..."
    python3 backend/scripts/refine_brand.py $brand > /dev/null
done

# 3. DEPLOY TO FRONTEND (The "Sync" step)
# Moves from backend/data.processed -> frontend/public/data
echo "🚀 [DEPLOY] Syncing to Frontend Public Data..."
python3 backend/scripts/deploy_badged_catalog.py

echo "✅ [SUCCESS] DB and Frontend Cache are fully synced."
echo "   You can now run 'cd frontend && npm run dev' if not already running."
