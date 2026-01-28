# Halilit Support Center

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://img.shields.io/badge/status-production-brightgreen)
[![Version](https://img.shields.io/badge/version-4.1.0-blue)](https://github.com/oripridan-dot/Halilit-Support-Center/releases/tag/v4.1)
[![TypeScript](https://img.shields.io/badge/typescript-5.9+-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/react-19.2-blue)](https://react.dev)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)

A fast, static-first support center catalog system. Browse 5,000+ musical instruments from 75+ brands with zero API overhead.

> **v4.1 Release**: Production-ready repository cleanup. Removed all outdated documentation, kept essential code and data. Now optimized for deployment.

## 🎯 What is Halilit?

Halilit Support Center is a **static-first catalog system** serving a professional music support center with 5,000+ products including instruments, audio equipment, and accessories from premium brands (Roland, Boss, Moog, Nord, and many more).

**Key Features**:
- ⚡ **Lightning Fast**: Static JSON, <50ms load time
- 🎯 **Zero API Calls**: All data pre-generated, browser-only
- 🔍 **Full-Text Search**: Instant product search with Fuse.js
- 📱 **Responsive Design**: Works on kiosks, tablets, desktops
- 🏭 **Offline-First**: Backend generates JSON, frontend consumes

## 🚀 Quick Start

```bash
# Frontend (React + Vite)
cd frontend
pnpm install
pnpm dev
```

Open **http://localhost:5173**

## 🏗️ Architecture

**Static-First Design**: Backend generates static JSON catalogs that the frontend consumes directly. No runtime API calls.

```
Raw Data (blueprints/, vault/)
    ↓
Backend Pipeline (Python)
    ↓
Static JSON Assets (frontend/public/data/)
    ↓
React Frontend (TypeScript)
    ↓
Browser
```

**No Backend at Runtime**: Everything is pre-built static files. The React app loads JSON and renders with zero server dependency.

## 📂 Project Structure

```
frontend/                  # React + TypeScript + Tailwind
├── src/
│   ├── components/       # React components (views, UI)
│   ├── lib/             # Utilities & helpers
│   ├── store/           # Zustand state management
│   ├── hooks/           # Custom React hooks
│   └── types/           # TypeScript type definitions
├── public/
│   └── data/            # Generated static catalogs (JSON)
└── tests/               # Unit & integration tests

backend/                  # Python data pipeline
├── forge_backbone.py    # Main orchestrator
├── mass_ingest_protocol.py  # Data ingestion
├── services/            # Scrapers & processors
│   ├── boss_scraper.py
│   ├── moog_scraper.py
│   ├── nord_scraper.py
│   ├── roland_scraper.py
│   └── [75+ brand services]
├── models/              # Pydantic data models
└── data/
    ├── blueprints/      # Raw brand specifications
    ├── vault/           # Raw Halilit data
    └── catalogs_brand/  # Processed data (git-ignored)

docs/context/            # System documentation
├── 01_PROJECT_IDENTITY.md      # Project overview
├── 02_BACKEND_PIPELINE.md      # Data pipeline
├── 03_FRONTEND_ARCHITECTURE.md # React structure
├── 04_DESIGN_SYSTEM.md         # Design patterns
└── 05_WORKFLOWS.md             # Development workflows

.devcontainer/           # Dev environment (Codespaces)
```

## 🔧 Backend Operations

### Generate Catalogs

```bash
cd backend
python3 forge_backbone.py
```

**What it does**:
1. Loads raw brand data from `data/blueprints/` and `data/vault/`
2. Runs scrapers for each brand (Boss, Roland, Moog, Nord, etc.)
3. Processes and normalizes product data
4. Generates static JSON catalogs
5. Outputs to `frontend/public/data/`

The frontend automatically loads these JSON files at runtime.

## 📦 Tech Stack

| Layer       | Technology                     | Purpose                    |
| ----------- | ------------------------------ | -------------------------- |
| **Frontend** | React 19 + TypeScript 5 + Vite | SPA, component framework   |
| **Styling** | Tailwind CSS                   | Utility-first CSS          |
| **State**   | Zustand                        | Global state management    |
| **Search**  | Fuse.js                        | Client-side full-text search |
| **Backend** | Python 3.11+                   | Data generation pipeline   |
| **Models**  | Pydantic                       | Type-safe data validation  |
| **Build**   | Vite 7 + SWC                   | Fast bundling & dev server |

## 🔄 Development Workflow

### 1. Start Development Server
```bash
cd frontend
pnpm dev
```

### 2. Update Data (Optional)
If you modify scrapers or data sources:
```bash
cd backend
python3 forge_backbone.py
```
This regenerates JSON catalogs in `frontend/public/data/`

### 3. Build for Production
```bash
cd frontend
pnpm build
```
Output goes to `dist/` folder, ready to deploy to any static host (Netlify, Vercel, etc.)

## 📚 Documentation

- **[01_PROJECT_IDENTITY.md](docs/context/01_PROJECT_IDENTITY.md)** - Project overview & manifest
- **[02_BACKEND_PIPELINE.md](docs/context/02_BACKEND_PIPELINE.md)** - Data generation architecture
- **[03_FRONTEND_ARCHITECTURE.md](docs/context/03_FRONTEND_ARCHITECTURE.md)** - React component structure
- **[04_DESIGN_SYSTEM.md](docs/context/04_DESIGN_SYSTEM.md)** - UI/UX patterns
- **[05_WORKFLOWS.md](docs/context/05_WORKFLOWS.md)** - Development workflows

## 🔗 Resources

- **Repository**: https://github.com/oripridan-dot/Halilit-Support-Center
- **Release**: https://github.com/oripridan-dot/Halilit-Support-Center/releases/tag/v4.1
- **Current Branch**: `main` (default, production-ready)

## ✅ v4.1 Changes

**Release Date**: January 28, 2026

### What's New
- ✅ Repository cleanup: removed outdated Blender/3D documentation
- ✅ Kept all core frontend, backend, and essential data
- ✅ Updated all documentation for v4.1 context
- ✅ Production-optimized codebase

### What Was Removed
- ❌ 13 outdated documentation files
- ❌ 2 Blender-related scripts
- ❌ 4 3D integration docs
- ❌ Unused 3D directories

See [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) for details.

## 📝 License

See LICENSE file for details.

---

**Version**: 4.1.0 | **Release Tag**: v4.1 | **Status**: Production Ready  
**Updated**: January 28, 2026 | **Branch**: main | **Commit**: 0398ddc
