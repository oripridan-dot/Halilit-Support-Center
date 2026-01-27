# Halilit Support Center - Galaxy Edition (v4.1)

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://img.shields.io/badge/status-production-brightgreen)
[![TypeScript](https://img.shields.io/badge/typescript-5.9+-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/react-19.2-blue)](https://react.dev)

**Ultra-fast static catalog for Halilit Support Center.** Browse 5,000+ products in a single-screen immersive interface.

- 🌌 **Galaxy Dashboard** - 3D room slots with theatrical stage lighting
- 🎹 **5,268 Products** - Roland, Boss, Nord, Moog, and 75+ brands
- ⚡ **Lightning Fast** - Static JSON, <50ms load time, no API calls
- 📱 **Responsive** - Optimized for support center kiosks

---

## 🚀 Quick Start (Codespaces)

Your devcontainer will auto-install everything. Just:

```bash
cd frontend && pnpm dev
```

Open **http://localhost:5173**

---

## 🏗️ Architecture

### Static-First Design

```
Raw Data (brands/halilit websites)
    ↓
Backend Pipeline (forge_backbone.py)
    ↓
Static JSON (frontend/public/data/)
    ↓
React App (pure frontend, no backend)
    ↓
Browser (instant load)
```

**No runtime API.** Everything is pre-built.

### Tech Stack

| Layer        | Technology              |
| ------------ | ----------------------- |
| **Frontend** | React 19 + TypeScript 5 |
| **Build**    | Vite 7 (SWC)           |
| **Styling**  | Tailwind CSS           |
| **State**    | Zustand                |
| **Search**   | Fuse.js                |

---

## 📂 Structure

```
frontend/
├── src/
│   ├── components/views/  ← GalaxyDashboard, SpectrumModule
│   ├── lib/              ← Utilities
│   └── store/            ← State
└── public/data/          ← Static JSON catalogs

backend/
├── forge_backbone.py     ← Main pipeline
├── mass_ingest_protocol.py
├── services/            ← Brand scrapers
├── models/              ← Data models
└── data/
    ├── blueprints/      ← Raw brand data (KEEP)
    ├── vault/           ← Raw Halilit data (KEEP)
    └── catalogs_brand/  ← Processed (git-ignored)
```

---

## 🔧 Maintenance

### Regenerate Catalog

```bash
cd backend
python3 forge_backbone.py
```

Output goes to `frontend/public/data/`

---

**Version**: 4.1.0 | **Status**: Production | **Updated**: January 27, 2026
