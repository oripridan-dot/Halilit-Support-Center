#!/bin/bash
set -e

echo "🧹 Starting DEEP CLEAN..."

# 1. Remove ALL Python cache
echo "Removing Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# 2. Remove venv (it's not needed, devcontainer provides Python)
echo "Removing venv..."
rm -rf venv

# 3. Remove frontend build artifacts
echo "Cleaning frontend artifacts..."
rm -rf frontend/dist
rm -rf frontend/.vite
rm -rf frontend/node_modules/.cache

# 4. Remove processed data (keep raw)
echo "Cleaning processed data..."
rm -rf backend/data/catalogs_brand/*
rm -rf backend/debug_output
rm -rf backend/logs/*.log 2>/dev/null || true

# 5. Remove IDE/system files
echo "Removing IDE files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# 6. Clean git
echo "Cleaning git..."
git gc --prune=now --aggressive 2>/dev/null || true

echo "✨ Deep clean complete!"
