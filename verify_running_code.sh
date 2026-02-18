#!/bin/bash
# Verify Running Code — Checks if changes are actually in the running application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  VERIFY RUNNING CODE — OPERATOR CONSOLE v9.6.0${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check 1: Verify GlobalSearch uses API
echo -e "${BLUE}CHECK 1: GlobalSearch Implementation${NC}"
if grep -q "/api/products/search" frontend/src/components/GlobalSearch.tsx; then
    echo -e "${GREEN}✓${NC} GlobalSearch.tsx uses /api/products/search"
else
    echo -e "${RED}✗${NC} GlobalSearch.tsx does NOT use /api/products/search"
fi

if ! grep -q "useRealtimeSearch\|instantSearch\|searchWorker" frontend/src/components/GlobalSearch.tsx; then
    echo -e "${GREEN}✓${NC} GlobalSearch.tsx does NOT use old search worker"
else
    echo -e "${RED}✗${NC} GlobalSearch.tsx still uses old search worker"
fi

# Check 2: Verify InventoryView uses API hook
echo ""
echo -e "${BLUE}CHECK 2: InventoryView Implementation${NC}"
if grep -q "useConductorCatalog" frontend/src/components/views/InventoryView.tsx; then
    echo -e "${GREEN}✓${NC} InventoryView uses useConductorCatalog hook"
else
    echo -e "${RED}✗${NC} InventoryView does NOT use useConductorCatalog"
fi

if grep -q "searchQuery" frontend/src/components/views/InventoryView.tsx; then
    echo -e "${GREEN}✓${NC} InventoryView reads searchQuery from store"
else
    echo -e "${RED}✗${NC} InventoryView does NOT read searchQuery"
fi

# Check 3: Verify Navigation Store
echo ""
echo -e "${BLUE}CHECK 3: Navigation Store${NC}"
if grep -q "searchQuery" frontend/src/store/navigationStore.ts; then
    echo -e "${GREEN}✓${NC} Navigation store has searchQuery state"
else
    echo -e "${RED}✗${NC} Navigation store missing searchQuery"
fi

if grep -q "goToInventory.*searchQuery" frontend/src/store/navigationStore.ts; then
    echo -e "${GREEN}✓${NC} goToInventory accepts searchQuery parameter"
else
    echo -e "${RED}✗${NC} goToInventory does NOT accept searchQuery"
fi

if ! grep -qi "camera\|zoom" frontend/src/store/navigationStore.ts; then
    echo -e "${GREEN}✓${NC} No camera/zoom logic in navigation store"
else
    echo -e "${RED}✗${NC} Navigation store still has camera/zoom logic"
fi

# Check 4: Verify old components are removed
echo ""
echo -e "${BLUE}CHECK 4: Old Components Removed${NC}"
OLD_COMPONENTS=(
    "frontend/src/components/views/GalaxyDashboard.tsx"
    "frontend/src/components/views/SpectrumModule.tsx"
    "frontend/src/components/views/ProductPage.tsx"
    "frontend/src/components/views/ItemsView.tsx"
    "frontend/src/components/v0"
    "frontend/src/lib/catalogLoader.ts"
    "frontend/src/lib/taxonomyService.ts"
    "frontend/src/lib/instantSearch.ts"
    "frontend/src/hooks/useRealtimeSearch.ts"
)

ALL_REMOVED=true
for comp in "${OLD_COMPONENTS[@]}"; do
    if [ ! -e "$comp" ]; then
        echo -e "${GREEN}✓${NC} Removed: $comp"
    else
        echo -e "${RED}✗${NC} Still exists: $comp"
        ALL_REMOVED=false
    fi
done

# Check 5: Verify API endpoints
echo ""
echo -e "${BLUE}CHECK 5: Backend API Endpoints${NC}"
if grep -q "/api/conductor/catalog" backend/server.py; then
    echo -e "${GREEN}✓${NC} /api/conductor/catalog endpoint exists"
else
    echo -e "${RED}✗${NC} /api/conductor/catalog endpoint missing"
fi

if grep -q "/api/products/search" backend/server.py; then
    echo -e "${GREEN}✓${NC} /api/products/search endpoint exists"
else
    echo -e "${RED}✗${NC} /api/products/search endpoint missing"
fi

if grep -q "Mount images directory" backend/server.py; then
    echo -e "${GREEN}✓${NC} Image serving endpoint configured"
else
    echo -e "${RED}✗${NC} Image serving endpoint missing"
fi

# Check 6: Verify no direct /data/ reads
echo ""
echo -e "${BLUE}CHECK 6: No Direct File Reads${NC}"
DATA_READS=$(grep -r "fetch.*'/data/" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "node_modules" | wc -l | tr -d ' ')
if [ "$DATA_READS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No direct /data/ file reads in frontend"
else
    echo -e "${RED}✗${NC} Found $DATA_READS direct /data/ reads (should use API)"
    grep -r "fetch.*'/data/" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "node_modules"
fi

# Check 7: Verify App.tsx only imports new views
echo ""
echo -e "${BLUE}CHECK 7: App.tsx Imports${NC}"
if ! grep -q "GalaxyDashboard\|SpectrumModule\|ProductPage\|ItemsView" frontend/src/App.tsx; then
    echo -e "${GREEN}✓${NC} App.tsx does NOT import old views"
else
    echo -e "${RED}✗${NC} App.tsx still imports old views"
    grep "GalaxyDashboard\|SpectrumModule\|ProductPage\|ItemsView" frontend/src/App.tsx
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  VERIFICATION COMPLETE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "If all checks pass but UI looks the same:"
echo "  1. Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "  2. Restart servers: ./start_console.sh"
echo "  3. Check browser DevTools → Network tab for API requests"
echo "  4. Verify you're on branch v9.6-ui: git branch"
echo ""
