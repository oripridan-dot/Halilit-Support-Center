#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Starting Workspace Verification...${NC}"

# Backend Checks
echo -e "\n${YELLOW}🐍 Checking Backend...${NC}"
cd backend

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

if [ -f "requirements.txt" ]; then
    # Assumes environment is ready or venv activated
    echo "Running Ruff Linting..."
    # use ruff directly or via python module
    ruff check . || { echo -e "${RED}❌ Ruff failed${NC}"; exit 1; }
    
    echo "Running Tests..."
    # Only run if tests exist
    if [ -d "tests" ] || ls test_*.py 1> /dev/null 2>&1; then
        pytest || { echo -e "${RED}❌ Pytest failed${NC}"; exit 1; }
    else
        echo "No standard tests found, skipping pytest."
    fi
else
    echo "No requirements.txt found in backend, skipping."
fi
cd ..

# Frontend Checks
echo -e "\n${YELLOW}⚛️ Checking Frontend...${NC}"
cd frontend
if [ -f "package.json" ]; then
    echo "Running Frontend Verification (Types, Lint)..."
    # Skip full 'verify' which builds the app. Just check code quality.
    npm run quality:types && npm run quality:lint || { echo -e "${RED}❌ Frontend Verification failed${NC}"; exit 1; }
    
    # Optional: Run tests if they are fast
    echo "Running Unit Tests..."
    npm run test:run || { echo -e "${RED}❌ Frontend Tests failed${NC}"; exit 1; }
else
    echo "No package.json found in frontend, skipping."
fi
cd ..

echo -e "\n${GREEN}✅ Workspace Verified! Everything is tight.${NC}"
