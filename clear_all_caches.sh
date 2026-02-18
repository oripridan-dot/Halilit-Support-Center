#!/bin/bash
# Clear All Caches — Forces fresh rebuild on next start

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧹 Clearing all caches and build artifacts..."
echo ""

# Frontend caches
echo "Clearing frontend caches..."
rm -rf frontend/dist
rm -rf frontend/.vite
rm -rf frontend/node_modules/.vite
rm -rf frontend/.next 2>/dev/null || true
echo "✅ Frontend caches cleared"

# Backend caches
echo "Clearing backend caches..."
rm -f backend/data/catalog_cache.json.gz
rm -rf backend/data/__pycache__
rm -rf backend/__pycache__
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo "✅ Backend caches cleared"

# Python cache
echo "Clearing Python caches..."
find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
echo "✅ Python caches cleared"

# Log files
echo "Clearing log files..."
rm -f backend.log frontend.log 2>/dev/null || true
rm -f backend/logs/*.log 2>/dev/null || true
echo "✅ Log files cleared"

# Empty directories
echo "Removing empty directories..."
rmdir frontend/src/components/v0 2>/dev/null || true
rmdir frontend/src/components/views/galaxy 2>/dev/null || true
rmdir frontend/src/components/views/arena 2>/dev/null || true
echo "✅ Empty directories removed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All caches cleared!"
echo ""
echo "Next steps:"
echo "  1. Restart servers: ./start_console.sh"
echo "  2. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "  3. Clear browser cache if needed:"
echo "     Chrome: Settings → Privacy → Clear browsing data → Cached images"
echo "     Firefox: Settings → Privacy → Clear Data → Cached Web Content"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
