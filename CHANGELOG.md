# Changelog - v4.1.0

**Released:** January 2025

## 🎨 Visual Enhancements
### Galaxy Dashboard - Theatrical Slot Lighting
- **3D Room Geometry**: Each category slot now renders as a tiny dark 3D room with back wall, side walls, and perspective floor
- **God's Beams**: Sharp, focused theatrical stage lights (175° angle) from separated origins (8% from left/right edges)
- **Separated Color Origins**: Each beam color originates from different points above, allowing natural color mixing only where beams intersect
- **Enhanced Depth**: Added radial vignettes and horizontal side shadows for 3D perception
- **Dimmed Floor Reflections**: Reduced opacity to 0.06/0.25 for subtle ambiance
- **Removed Artifacts**: Eliminated horizontal seam lines that caused visual clutter

## 🧹 Repository Cleanup (~700MB Removed)
- Deleted `backend/.venv/` (198MB - unnecessary in devcontainer)
- Removed `frontend/dist/` (510MB - build artifacts)
- Purged all Python `__pycache__` directories and `.pyc` files
- Deleted `frontend/.vite` cache
- Removed 15+ unused backend scripts:
  - `debug_*.py` (bs4_copy, scraper, visual_factory)
  - `analyze_gaps.py`, `generate_review_bundle.py`, `split_commercial.py`
  - `manage.py`, `hydrate_env.sh`
  - `run_*.py` (clean_ingestion, data_factory, discovery, fast_regenerate, high_octane_ingestion)
- Cleaned backend data: removed processed `catalogs_brand/*` and `radar/*` (kept raw `blueprints/` and `vault/`)
- Removed frontend test/debug files: `test-data-load.*`, `test-images.html`, `debug_universals.ts`

## ⚙️ Devcontainer Simplification
**v4.0 → v4.1**: Complete rewrite to resolve Docker build failures
- **Base Image**: Changed from Python to TypeScript-Node (mcr.microsoft.com/devcontainers/typescript-node:1-20-bullseye)
- **Removed Features**: git, gh, docker-in-docker, redis (kept only Python 3.11 feature)
- **Removed Volume Mounts**: Eliminated `/workspace` and `/tmp` mounts causing syntax errors
- **Simplified Setup**: Single `postCreateCommand` (pnpm install) vs complex parallel setup.sh
- **Result**: Resolved "recovery mode" errors, faster container builds

## 🚀 Performance Optimizations
### Frontend Build
- **React Fast Refresh**: Enabled SWC for instant HMR
- **Pre-bundling**: Added `optimizeDeps` for react, react-dom, zustand, framer-motion, lucide-react, fuse.js
- **Build Target**: Set to `esnext` with esbuild minification
- **Source Maps**: Production-only to reduce dev overhead

### pnpm Configuration (.npmrc)
```ini
network-concurrency=16
store-dir=/home/vscode/.local/share/pnpm/store
cache-dir=/home/vscode/.cache/pnpm
side-effects-cache=true
```

## 📚 Documentation Updates
- Updated README.md to v4.1 with accurate architecture description
- Created backend/README.md explaining static-first pipeline
- Updated docs/context/01_PROJECT_IDENTITY.md to v4.1.0
- Simplified package.json scripts to essential 5 commands (dev, build, preview, lint, test)

## 🔧 Configuration Files
- **Standardized Slot Scenes**: All 40+ SLOT_SCENES now use uniform base properties (floorMat, bgMat) - only themeColors differ
- **CategorySlot Component**: Production-ready with sharp god's beams, 3D room, and depth enhancements

## Breaking Changes
None - all changes are visual enhancements and cleanup

## Migration Notes
1. **Rebuild Devcontainer**: Click "Rebuild Container" in VS Code after pulling v4.1
2. **Re-generate Data**: Run `python backend/forge_backbone.py` to regenerate catalog.json (processed data was deleted)
3. **Install Dependencies**: pnpm will auto-install on container rebuild

## Known Issues
None

## Next Version Preview (v4.2)
- Enhanced search with Fuse.js fuzzy matching
- Additional Galaxy sectors and categories
- Improved mobile responsiveness for 3D slots
