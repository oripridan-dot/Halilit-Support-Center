#!/bin/bash
# Functionality Test — Tests key Operator Console features

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FUNCTIONALITY TEST — OPERATOR CONSOLE v9.6.0${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: Check if servers are running
echo -e "${BLUE}TEST 1: Server Status${NC}"
BACKEND_RUNNING=false
FRONTEND_RUNNING=false

if command -v curl &> /dev/null; then
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend API running on port 8000"
        BACKEND_RUNNING=true
        
        # Test health endpoint
        HEALTH=$(curl -s http://localhost:8000/api/health)
        echo "   Response: $HEALTH"
    else
        echo -e "${YELLOW}⚠${NC} Backend API not running"
    fi
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend dev server running on port 5173"
        FRONTEND_RUNNING=true
    else
        echo -e "${YELLOW}⚠${NC} Frontend dev server not running"
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not found, skipping server checks"
fi

echo ""

# Test 2: Catalog API endpoint
if [ "$BACKEND_RUNNING" = true ]; then
    echo -e "${BLUE}TEST 2: Catalog API Endpoint${NC}"
    
    CATALOG_RESPONSE=$(curl -s http://localhost:8000/api/conductor/catalog 2>&1)
    
    if echo "$CATALOG_RESPONSE" | grep -q "products"; then
        echo -e "${GREEN}✓${NC} Catalog endpoint returns valid JSON"
        
        # Extract key metrics using jq if available, otherwise use grep
        if command -v jq &> /dev/null; then
            TOTAL=$(echo "$CATALOG_RESPONSE" | jq -r '.metadata.total_products // "unknown"')
            BRANDS=$(echo "$CATALOG_RESPONSE" | jq -r '.metadata.brands | length // "unknown"')
            echo "   • Total products: $TOTAL"
            echo "   • Brands: $BRANDS"
        else
            echo "   • Response contains 'products' key"
            echo "   • Install jq for detailed metrics: brew install jq"
        fi
    elif echo "$CATALOG_RESPONSE" | grep -q "still building"; then
        echo -e "${YELLOW}⚠${NC} Catalog is still building (503 response)"
    else
        echo -e "${RED}✗${NC} Catalog endpoint error"
        echo "   Response: ${CATALOG_RESPONSE:0:200}"
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping catalog test (backend not running)"
fi

echo ""

# Test 3: Search API endpoint
if [ "$BACKEND_RUNNING" = true ]; then
    echo -e "${BLUE}TEST 3: Search API Endpoint${NC}"
    
    SEARCH_RESPONSE=$(curl -s "http://localhost:8000/api/products/search?q=roland" 2>&1)
    
    if echo "$SEARCH_RESPONSE" | grep -q "products"; then
        echo -e "${GREEN}✓${NC} Search endpoint returns valid JSON"
        
        if command -v jq &> /dev/null; then
            COUNT=$(echo "$SEARCH_RESPONSE" | jq -r '.products | length // 0')
            FIRST_NAME=$(echo "$SEARCH_RESPONSE" | jq -r '.products[0].product_name // "none"')
            echo "   • Results for 'roland': $COUNT products"
            if [ "$COUNT" -gt 0 ]; then
                echo "   • First result: $FIRST_NAME"
            fi
        fi
    else
        echo -e "${RED}✗${NC} Search endpoint error"
        echo "   Response: ${SEARCH_RESPONSE:0:200}"
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping search test (backend not running)"
fi

echo ""

# Test 4: Frontend component structure
echo -e "${BLUE}TEST 4: Frontend Component Structure${NC}"

COMPONENTS=(
    "frontend/src/components/GlobalSearch.tsx"
    "frontend/src/components/views/DashboardView.tsx"
    "frontend/src/components/views/InventoryView.tsx"
    "frontend/src/components/views/ProductDetailView.tsx"
    "frontend/src/hooks/useConductorCatalog.ts"
    "frontend/src/store/navigationStore.ts"
)

ALL_EXIST=true
for comp in "${COMPONENTS[@]}"; do
    if [ -f "$comp" ]; then
        echo -e "${GREEN}✓${NC} $comp"
    else
        echo -e "${RED}✗${NC} $comp (missing)"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = true ]; then
    echo -e "${GREEN}✓${NC} All required components present"
else
    echo -e "${RED}✗${NC} Some components missing"
fi

echo ""

# Test 5: Check for API usage (not static files)
echo -e "${BLUE}TEST 5: API Integration Check${NC}"

if grep -q "/api/conductor/catalog" frontend/src/hooks/useConductorCatalog.ts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} useConductorCatalog uses /api/conductor/catalog"
else
    echo -e "${RED}✗${NC} useConductorCatalog may not use API"
fi

if grep -q "/api/products/search" frontend/src/components/GlobalSearch.tsx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} GlobalSearch uses /api/products/search"
else
    echo -e "${RED}✗${NC} GlobalSearch may not use API"
fi

# Check for direct /data/ reads (should be minimal)
DATA_READS=$(grep -r "fetch.*'/data/" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DATA_READS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No direct /data/ file reads in frontend"
else
    echo -e "${YELLOW}⚠${NC} Found $DATA_READS direct /data/ reads (should use API)"
fi

echo ""

# Test 6: Navigation store structure
echo -e "${BLUE}TEST 6: Navigation Store Structure${NC}"

if grep -q "searchQuery" frontend/src/store/navigationStore.ts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Navigation store has searchQuery state"
else
    echo -e "${RED}✗${NC} Navigation store missing searchQuery"
fi

if grep -q "goToInventory.*searchQuery" frontend/src/store/navigationStore.ts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} goToInventory accepts searchQuery parameter"
else
    echo -e "${RED}✗${NC} goToInventory may not accept searchQuery"
fi

if ! grep -qi "camera\|zoom" frontend/src/store/navigationStore.ts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} No camera/zoom logic in navigation store"
else
    echo -e "${RED}✗${NC} Navigation store contains camera/zoom logic"
fi

echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo -e "${GREEN}✓${NC} Both servers running"
    echo ""
    echo "Open in browser:"
    echo "  Frontend: http://localhost:5173"
    echo "  API Docs: http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠${NC} Start servers with: ./start_console.sh"
fi

echo ""
echo "Next steps:"
echo "  1. Start servers: ./start_console.sh"
echo "  2. Open browser: http://localhost:5173"
echo "  3. Test search: Type in GlobalSearch (Cmd+K)"
echo "  4. Test navigation: Click product → Product Detail view"
echo ""
