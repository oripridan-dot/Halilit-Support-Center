#!/bin/bash
# =============================================================================
# DARK FACTORY — IGNITION SEQUENCE
# Halilit Support Center v9.7.1
#
# Builds all three UI views from their specs, then boots the full app.
# Requires: GEMINI_API_KEY (or GOOGLE_API_KEY) to be exported.
# Usage:
#   chmod +x ignite_factory.sh
#   export GEMINI_API_KEY="your-key-here"
#   ./ignite_factory.sh
# =============================================================================

set -e

# --- Guard: API key ---
if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌  Error: GEMINI_API_KEY is not set."
    echo "    Run: export GEMINI_API_KEY='your-key-here'"
    exit 1
fi

echo ""
echo "================================================================="
echo "⚙️  BOOTING HALILIT SUPPORT CENTER FACTORY"
echo "================================================================="

# --- Activate venv if not already active ----------------------------------
if [ -f ".venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
    echo "✅  Virtual environment activated (.venv)"
fi

# --- Tech Lead Morning Audit -----------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "👔  Tech Lead: Static Analysis Audit"
echo "────────────────────────────────────────"
python nexus.py --briefing

# --- Terminal Dashboard: Print Critical Section ----------------------------
if [ -f "DAILY_BRIEFING.md" ]; then
    echo ""
    echo "================================================================="
    echo "🚨  TECH LEAD DAILY BRIEFING — CRITICALS"
    echo "================================================================="
    # Print lines from the CRITICAL section until the MAJOR section begins
    awk '/🔴 CRITICAL/{flag=1; print; next} /🟠 MAJOR/{flag=0} flag' DAILY_BRIEFING.md
    echo "================================================================="
    echo "👉  Read DAILY_BRIEFING.md for the full report and copy-paste commands."
    echo ""
fi

# Ask operator to continue before handing off to Nexus
read -rp "Press ENTER to continue with the ignition sequence..."

echo ""
echo "🏭  DARK FACTORY — IGNITION SEQUENCE"
echo "========================================"

# 1. Scaffold folders --------------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🗂️   Step 1: Initializing folder structure"
echo "────────────────────────────────────────"
python factory.py init

# 2. Status check ------------------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🔍  Step 2: Environment health check"
echo "────────────────────────────────────────"
python factory.py status

# 3. Build Dashboard ---------------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🔨  Step 3: Building DashboardView"
echo "            (specs/interface/01_operator_dashboard.md)"
echo "────────────────────────────────────────"
python factory.py build specs/interface/01_operator_dashboard.md

# 4. Build Inventory Grid ----------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🔨  Step 4: Building InventoryView"
echo "            (specs/interface/02_inventory_grid.md)"
echo "────────────────────────────────────────"
python factory.py build specs/interface/02_inventory_grid.md

# 5. Build Product Detail ----------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🔨  Step 5: Building ProductDetailView"
echo "            (specs/interface/03_product_intelligence.md)"
echo "────────────────────────────────────────"
python factory.py build specs/interface/03_product_intelligence.md

# 6. Launch ------------------------------------------------------------------
echo ""
echo "────────────────────────────────────────"
echo "🚀  Step 6: Launching Application"
echo "    Backend  → http://localhost:8000"
echo "    Frontend → http://localhost:5173"
echo ""
echo "    Verification endpoints:"
echo "      http://localhost:8000/api/health"
echo "      http://localhost:8000/api/conductor/catalog"
echo "────────────────────────────────────────"
python factory.py start
