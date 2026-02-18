#!/bin/bash
# Complete rebuild script: Enrich → Rebuild Catalog → Verify

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Complete Rebuild Pipeline"
echo "=============================="
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./start_console.sh first."
    exit 1
fi

export PYTHONPATH="$(pwd):$PYTHONPATH"

# Step 1: Enrich (if brand specified)
if [ -n "$1" ]; then
    echo "📦 Step 1: Enriching brand '$1'..."
    python3 backend/conductor_main.py enrich "$1" --concurrent-products 30
else
    echo "📦 Step 1: Enriching ALL brands (this will take 30-60 minutes)..."
    echo "   (Press Ctrl+C to cancel, or wait for completion)"
    python3 backend/conductor_main.py enrich --concurrent-products 30
fi

if [ $? -ne 0 ]; then
    echo "❌ Enrichment failed. Check logs above."
    exit 1
fi

echo ""
echo "✅ Enrichment complete!"
echo ""

# Step 2: Rebuild Catalog
echo "🔨 Step 2: Rebuilding catalog..."
python3 backend/conductor_main.py rebuild-catalog

if [ $? -ne 0 ]; then
    echo "❌ Catalog rebuild failed. Check logs above."
    exit 1
fi

echo ""
echo "✅ Catalog rebuild complete!"
echo ""

# Step 3: Verify
echo "🔍 Step 3: Verifying data..."
./check_data_status.sh

echo ""
echo "🎉 Rebuild complete!"
echo ""
echo "Next steps:"
echo "  1. Restart servers: ./start_console.sh"
echo "  2. Open browser: http://localhost:5173"
echo "  3. Check a product - should show specs!"
