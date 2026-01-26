#!/bin/bash

# HSC-JIT Lean - Environment Setup Script
# Run this script immediately after opening the new Codespace.

set -e # Exit on error

echo "🚀 [1/4] Initializing HSC-JIT Lean Environment..."

# --- Backend Setup ---
echo "🐍 [2/4] Installing Backend Dependencies (Python)..."
if [ -f "backend/requirements.txt" ]; then
    pip install --user -r backend/requirements.txt
    echo "   ✅ Backend dependencies installed."
else
    echo "   ⚠️ Warning: backend/requirements.txt not found."
fi

# --- Frontend Setup ---
echo "🎨 [3/4] Installing Frontend Dependencies (Node/React)..."
if [ -d "frontend" ]; then
    # Ensure pnpm is available
    if ! command -v pnpm &> /dev/null; then
        echo "   ...Install pnpm globally"
        npm install -g pnpm
    fi
    
    cd frontend
    pnpm install
    cd ..
    echo "   ✅ Frontend dependencies installed."
else
    echo "   ⚠️ Warning: frontend/ directory not found."
fi

# --- Validation ---
echo "🔍 [4/4] Verifying Installation..."
echo "   - Python: $(python3 --version)"
echo "   - Node: $(node --version)"
echo "   - PNPM: $(pnpm --version)"

echo ""
echo "✅ SETUP COMPLETE!"
echo "---------------------------------------------------"
echo "To start the development server:"
echo "   cd frontend && pnpm dev"
echo "---------------------------------------------------"
