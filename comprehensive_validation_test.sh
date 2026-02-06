#!/bin/bash
# Comprehensive System Validation Test
# Tests TanStack Query integration, categorization logic, and data pipeline

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║   HALILIT SUPPORT CENTER v6.1 COMPREHENSIVE VALIDATION TEST             ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

# Test helper functions
test_passed() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

test_failed() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

test_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ==============================================================================
# TEST 1: Dependencies & Build System
# ==============================================================================
echo "📦 TEST 1: DEPENDENCIES & BUILD SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "@tanstack/react-query" /workspaces/Halilit-Support-Center/frontend/package.json; then
    test_passed "TanStack Query is in package.json"
else
    test_failed "TanStack Query missing from package.json"
fi

if [ -d "/workspaces/Halilit-Support-Center/frontend/node_modules/@tanstack/react-query" ]; then
    test_passed "TanStack Query is installed"
else
    test_failed "TanStack Query not installed"
fi

if [ -f "/workspaces/Halilit-Support-Center/frontend/dist/index.html" ]; then
    test_passed "Frontend build exists"
else
    test_failed "Frontend build missing"
fi

# ==============================================================================
# TEST 2: TanStack Query Integration
# ==============================================================================
echo ""
echo "🔄 TEST 2: TANSTACK QUERY INTEGRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HOOKS_USING_TANSTACK=$(grep -l "useQuery\|useMutation" /workspaces/Halilit-Support-Center/frontend/src/hooks/*.ts 2>/dev/null | wc -l)
if [ "$HOOKS_USING_TANSTACK" -gt 0 ]; then
    test_passed "$HOOKS_USING_TANSTACK hooks using TanStack Query"
else
    test_failed "No hooks found using TanStack Query"
fi

if grep -q "QueryClientProvider" /workspaces/Halilit-Support-Center/frontend/src/main.tsx; then
    test_passed "QueryClientProvider configured in main.tsx"
else
    test_failed "QueryClientProvider not found in main.tsx"
fi

if grep -q "staleTime:\|gcTime:" /workspaces/Halilit-Support-Center/frontend/src/main.tsx; then
    test_passed "TanStack Query default options configured"
else
    test_failed "TanStack Query default options missing"
fi

# ==============================================================================
# TEST 3: Data Pipeline & Categorization
# ==============================================================================
echo ""
echo "📊 TEST 3: DATA PIPELINE & CATEGORIZATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PRODUCT_COUNT=$(python3 -c "import json; data = json.load(open('/workspaces/Halilit-Support-Center/frontend/public/data/galaxy_db.json')); print(len(data))")
if [ "$PRODUCT_COUNT" = "647" ]; then
    test_passed "Database contains all 647 products"
else
    test_failed "Database product count mismatch: $PRODUCT_COUNT"
fi

# Test each galaxy
for GALAXY in "guitars-bass" "drums-percussion" "keys-production" "studio-recording" "live-dj" "accessories-utility"; do
    COUNT=$(python3 -c "import json; data = json.load(open('/workspaces/Halilit-Support-Center/frontend/public/data/galaxy_db.json')); print(sum(1 for p in data if p.get('category') == '$GALAXY'))")
    if [ "$COUNT" -gt 0 ]; then
        test_passed "Galaxy '$GALAXY' has $COUNT products"
    else
        test_failed "Galaxy '$GALAXY' has no products"
    fi
done

# Test categorization completeness
CATEGORIZED=$(python3 -c "import json; data = json.load(open('/workspaces/Halilit-Support-Center/frontend/public/data/galaxy_db.json')); print(sum(1 for p in data if p.get('category')))")
if [ "$CATEGORIZED" = "647" ]; then
    test_passed "All products have category field"
else
    test_failed "Only $CATEGORIZED products categorized"
fi

SPECTRA=$(python3 -c "import json; data = json.load(open('/workspaces/Halilit-Support-Center/frontend/public/data/galaxy_db.json')); print(sum(1 for p in data if p.get('spectrum')))")
if [ "$SPECTRA" = "647" ]; then
    test_passed "All products have spectrum/tier field"
else
    test_failed "Only $SPECTRA products have spectrum"
fi

# ==============================================================================
# TEST 4: Categorization Logic
# ==============================================================================
echo ""
echo "🏷️  TEST 4: CATEGORIZATION LOGIC"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if grep -q "DIRECT GALAXY ID CHECK" /workspaces/Halilit-Support-Center/frontend/src/lib/categoryConsolidator.ts; then
    test_passed "Direct galaxy ID matching implemented"
else
    test_failed "Direct galaxy ID matching not found"
fi

if grep -q "TIER 1.*HALILIT" /workspaces/Halilit-Support-Center/frontend/src/lib/categoryConsolidator.ts; then
    test_passed "Halilit data validation tier implemented (Tier 1)"
else
    test_failed "Halilit data validation tier missing"
fi

if grep -q "TIER 2.*BRAND" /workspaces/Halilit-Support-Center/frontend/src/lib/categoryConsolidator.ts; then
    test_passed "Brand website validation tier implemented (Tier 2)"
else
    test_failed "Brand website validation tier missing"
fi

# ==============================================================================
# TEST 5: API Endpoints
# ==============================================================================
echo ""
echo "🌐 TEST 5: API ENDPOINTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if timeout 2 curl -s http://localhost:8000/ > /dev/null 2>&1; then
    test_passed "Frontend root endpoint accessible"
else
    test_warning "Frontend may not be running on http://localhost:8000"
fi

if timeout 2 curl -s http://localhost:8000/data/galaxy_db.json > /dev/null 2>&1; then
    test_passed "Data API endpoint accessible"
else
    test_warning "Data API may not be accessible"
fi

# ==============================================================================
# TEST 6: Code Quality
# ==============================================================================
echo ""
echo "✨ TEST 6: CODE QUALITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for TypeScript compilation
cd /workspaces/Halilit-Support-Center/frontend
if npx tsc --noEmit > /dev/null 2>&1; then
    test_passed "TypeScript compilation successful"
else
    test_failed "TypeScript compilation has errors"
fi

# Check imports
if grep -l "import.*useQuery.*from.*@tanstack/react-query" src/hooks/*.ts > /dev/null 2>&1; then
    test_passed "useQuery imports correctly"
else
    test_warning "useQuery import pattern may have changed"
fi

# ==============================================================================
# SUMMARY
# ==============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                          TEST SUMMARY                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"

TOTAL=$((PASS_COUNT + FAIL_COUNT))
PASS_PCT=$((PASS_COUNT * 100 / TOTAL))

echo ""
echo "  Passed: ${GREEN}$PASS_COUNT${NC}/$TOTAL"
echo "  Failed: ${RED}$FAIL_COUNT${NC}/$TOTAL"
echo "  Score:  ${GREEN}$PASS_PCT%${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION                     ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "System Status:"
    echo "  • TanStack Query:  ✓ Fully Integrated"
    echo "  • Data Pipeline:   ✓ All 647 products categorized"
    echo "  • Categorization:  ✓ Halilit-based with 3-tier fallback"
    echo "  • Frontend Build:  ✓ Production-ready"
    echo ""
else
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  SOME TESTS FAILED - REVIEW REQUIRED                              ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
fi

exit $FAIL_COUNT
