#!/bin/bash
set -e

# Persist cache locations
WORKSPACE_ROOT="/workspaces/hsc-jit-v3"
PLAYWRIGHT_BROWSERS_PATH="$WORKSPACE_ROOT/.playwright-browsers"
export PLAYWRIGHT_BROWSERS_PATH

echo "Starting setup..."

# 1. System Dependencies
# Only run update if we haven't recently (implied by fresh container)
echo "Installing system packages..."
sudo apt-get update -qq
# Combined list including Playwright dependencies to minimize apt calls
PACKAGES="redis-server lsof curl wget \
    libasound2 libatk-bridge2.0-0 libgtk-3-0 libnss3 libx11-xcb1 libxss1 libxtst6 \
    libgbm1 libdrm2 libxkbcommon0 libwayland-client0 libwayland-cursor0 libwayland-egl1"
sudo apt-get install -y -qq --no-install-recommends $PACKAGES

# 2. Python Dependencies
echo "Installing Backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    # --upgrade-strategy only-if-needed helps speed
    pip install --disable-pip-version-check --no-cache-dir -r backend/requirements.txt
fi

# 3. Playwright
if [ -f "backend/requirements-playwright.txt" ]; then
    echo "Configuring Playwright..."
    # Install playwright python package
    pip install --disable-pip-version-check --no-cache-dir -r backend/requirements-playwright.txt
    
    # Check if browsers exist in persisted location
    if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ] && [ "$(ls -A $PLAYWRIGHT_BROWSERS_PATH)" ]; then
        echo "Found existing Playwright browsers in $PLAYWRIGHT_BROWSERS_PATH. Skipping download."
    else
        echo "Downloading Playwright browsers to $PLAYWRIGHT_BROWSERS_PATH..."
        playwright install
    fi
    
    # Install system deps (redundant safely)
    sudo playwright install-deps
fi

# 4. Frontend
echo "Installing Frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    # pnpm is fast if node_modules exists
    pnpm install
    cd ..
fi

echo "Setup complete."
