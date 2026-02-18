#!/bin/bash

# Halilit Operator Console — One-Click Startup Script
# Ensures backend starts before frontend, respects the unified pipeline architecture

set -e

echo "🚀 Initializing Halilit Operator Console v9.6.0..."
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found. Please install Python 3.11+"
    exit 1
fi

# 2. Check if virtual environment exists, create if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# 3. Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# 4. Install/update dependencies if needed
if [ ! -f ".venv/.deps_installed" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -q -r backend/requirements.txt
    touch .venv/.deps_installed
fi

# 5. Check if catalog data exists (warn but don't fail)
if [ ! -f "backend/data/catalog_cache.json.gz" ] && [ ! -d "frontend/public/data" ]; then
    echo "⚠️  WARNING: Catalog data missing."
    echo "   Run 'python backend/conductor_main.py rebuild-catalog' first."
    echo "   The app will work but may be slow on first load."
    echo ""
fi

# 6. Set PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# 7. Start Backend (Background Process)
echo "🔌 Starting API Server (Port 8000)..."
cd backend
# Use PYTHONPATH from environment
python3 -m uvicorn server:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
# Check if curl is available, otherwise use python
if command -v curl &> /dev/null; then
    HEALTH_CHECK_CMD="curl -s http://localhost:8000/api/health > /dev/null 2>&1"
else
    HEALTH_CHECK_CMD="python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')\" > /dev/null 2>&1"
fi

for i in {1..30}; do
    if eval "$HEALTH_CHECK_CMD"; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ ERROR: Backend failed to start after 30 seconds"
        echo "   Check backend.log for errors: tail -20 backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# 8. Check Node.js environment
if ! command -v npm &> /dev/null && ! command -v pnpm &> /dev/null; then
    echo "❌ ERROR: npm or pnpm not found. Please install Node.js 18+"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 9. Start Frontend
echo "🖥️  Starting Frontend (Port 5173)..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    if command -v pnpm &> /dev/null; then
        pnpm install
    else
        npm install
    fi
fi

# Start dev server
if command -v pnpm &> /dev/null; then
    pnpm run dev > ../frontend.log 2>&1 &
else
    npm run dev > ../frontend.log 2>&1 &
fi
FRONTEND_PID=$!
cd ..

# 10. Handle Cleanup on Exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "✅ Shutdown complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 11. Wait a moment for frontend to start
sleep 2

# 12. Display status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Halilit Operator Console is ONLINE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   📊 Backend API:  http://localhost:8000/docs"
echo "   🖥️  Frontend UI:  http://localhost:5173"
echo ""
echo "   Logs:"
echo "   • Backend:  tail -f backend.log"
echo "   • Frontend: tail -f frontend.log"
echo ""
echo "   Press Ctrl+C to stop both servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 13. Keep script running
wait
