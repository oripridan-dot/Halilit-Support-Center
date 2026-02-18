#!/bin/bash
# HALILIT OPERATOR CONSOLE — FACTORY PIPELINE
# 1. Optional: Rebuild catalog (--rebuild)
# 2. Enforce artifact existence (learned_taxonomy or catalog_cache)
# 3. Launch Backend + Frontend

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏭 Starting Factory Pipeline..."

# Step 1: Backend Data Fabrication (optional)
if [ "$1" == "--rebuild" ]; then
    echo "⚙️  Running Conductor (Data Ingestion)..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    cd backend
    python3 conductor_main.py rebuild-catalog
    cd ..
fi

# Step 2: Validation — at least one catalog artifact must exist
CATALOG_ARTIFACT="backend/data/learned_taxonomy.json"
CACHE_ARTIFACT="backend/data/catalog_cache.json.gz"
if [ ! -f "$CATALOG_ARTIFACT" ] && [ ! -f "$CACHE_ARTIFACT" ]; then
    echo "❌ CRITICAL: No catalog artifact found."
    echo "   Run: ./factory_reset.sh --rebuild"
    echo "   Or:  PYTHONPATH=. python backend/conductor_main.py rebuild-catalog"
    exit 1
fi

# Step 3: Launch Assembly (Backend + Frontend)
echo "🚀 Launching Operator Console..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

(cd backend && python3 -m uvicorn server:app --reload --host 0.0.0.0 --port 8000) &
PID_BACKEND=$!

(cd frontend && (command -v pnpm &>/dev/null && pnpm run dev || npm run dev)) &
PID_FRONTEND=$!

trap "kill $PID_BACKEND $PID_FRONTEND 2>/dev/null; exit 0" SIGINT SIGTERM EXIT

echo ""
echo "   📊 Backend:  http://localhost:8000/docs"
echo "   🖥️  Frontend: http://localhost:5173"
echo "   Press Ctrl+C to stop."
echo ""
wait
