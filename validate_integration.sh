#!/bin/bash
# Integration Validation Script — Tests the complete Operator Console pipeline

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  HALILIT OPERATOR CONSOLE — INTEGRATION VALIDATION"
echo "  Version 9.6.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: Python environment
echo "TEST 1: Python Environment"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_test "Python 3 found: $PYTHON_VERSION"
else
    print_fail "Python 3 not found"
    exit 1
fi

# Test 2: Node.js environment
echo ""
echo "TEST 2: Node.js Environment"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_test "Node.js found: $NODE_VERSION"
else
    print_fail "Node.js not found"
    exit 1
fi

# Test 3: Project structure
echo ""
echo "TEST 3: Project Structure"
if [ -d "backend" ] && [ -d "frontend" ]; then
    print_test "Project structure valid"
else
    print_fail "Missing backend/ or frontend/ directories"
    exit 1
fi

# Test 4: Python dependencies
echo ""
echo "TEST 4: Python Dependencies"
if [ -f "backend/requirements.txt" ]; then
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        if python3 -c "import fastapi, uvicorn" 2>/dev/null; then
            print_test "Python dependencies installed"
        else
            print_warn "Python dependencies not installed (run: pip install -r backend/requirements.txt)"
        fi
    else
        print_warn "Virtual environment not found (will be created by start_console.sh)"
    fi
else
    print_fail "backend/requirements.txt not found"
    exit 1
fi

# Test 5: Frontend dependencies
echo ""
echo "TEST 5: Frontend Dependencies"
if [ -d "frontend/node_modules" ]; then
    print_test "Frontend dependencies installed"
else
    print_warn "Frontend dependencies not installed (run: cd frontend && npm install)"
fi

# Test 6: Brand JSON files
echo ""
echo "TEST 6: Brand JSON Files"
if [ -d "frontend/public/data" ]; then
    JSON_COUNT=$(find frontend/public/data -maxdepth 1 -name "*.json" -not -name "index.json" -not -name "search_index*.json" | wc -l | tr -d ' ')
    if [ "$JSON_COUNT" -gt 0 ]; then
        print_test "Found $JSON_COUNT brand JSON file(s)"
    else
        print_warn "No brand JSON files found (run: python backend/conductor_main.py skeleton-sync)"
    fi
else
    print_warn "frontend/public/data directory not found"
fi

# Test 7: Catalog cache
echo ""
echo "TEST 7: Catalog Cache"
if [ -f "backend/data/catalog_cache.json.gz" ]; then
    CACHE_SIZE=$(du -h backend/data/catalog_cache.json.gz | cut -f1)
    print_test "Catalog cache exists ($CACHE_SIZE)"
else
    print_warn "Catalog cache not found (will be built on first API request)"
fi

# Test 8: Startup script
echo ""
echo "TEST 8: Startup Script"
if [ -f "start_console.sh" ] && [ -x "start_console.sh" ]; then
    print_test "start_console.sh is executable"
else
    print_fail "start_console.sh not found or not executable"
    exit 1
fi

# Test 9: API server (if running)
echo ""
echo "TEST 9: API Server Status"
if command -v curl &> /dev/null; then
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_test "API server is running on port 8000"
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
        echo "   Response: $HEALTH_RESPONSE"
    else
        print_warn "API server not running (start with: ./start_console.sh)"
    fi
else
    print_warn "curl not found, skipping API server check"
fi

# Test 10: Frontend dev server (if running)
echo ""
echo "TEST 10: Frontend Dev Server Status"
if command -v curl &> /dev/null; then
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_test "Frontend dev server is running on port 5173"
    else
        print_warn "Frontend dev server not running (start with: ./start_console.sh)"
    fi
else
    print_warn "curl not found, skipping frontend server check"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  VALIDATION COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start the Operator Console:"
echo "  ./start_console.sh"
echo ""
echo "To run detailed Python tests:"
echo "  python3 test_pipeline.py"
echo ""
