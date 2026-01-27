# Halilit Support Center - Galaxy Edition (v4)

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://img.shields.io/badge/status-production%20ready-brightgreen)
[![TypeScript](https://img.shields.io/badge/typescript-%235.0+-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/react-18+-blue)](https://react.dev)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**The specialized static catalog for Halilit support center.** A lightning-fast, single-screen interface for browsing 5,000+ products.

- 🌌 **Galaxy Dashboard** - Unified visual interface for all product categories.
- 🎹 **5,268 Products** - Roland, Boss, Nord, Moog, and 75+ brands.
- 🚀 **Lightning Fast** - Static JSON architecture, <50ms load time.
- 📱 **Responsive Design** - Optimized for support center kiosks and devices.

---

## 🚀 Quick Start

```bash
# Clone and enter
git clone [repo-url]
cd Halilit-Support-Center

# Run the setup script (installs everything)
./setup_fresh_env.sh

# Start development server
cd frontend && pnpm dev
```

Open **http://localhost:5173** in your browser.

---

## 🏗️ Architecture

### "Static First" Design

```
Data Generation (Offline)
    ↓
Scrapers (Backend Services)
    ↓
forge_backbone.py (Data pipeline)
    ↓
Static JSON Files (frontend/public/data/)
    ↓
Frontend (React + TypeScript)
    ↓
Browser (No API calls, instant load)
```

**Key Principle**: All data is pre-built. The frontend is a pure React application consuming static JSON assets.

### Tech Stack

| Layer        | Technology              | Why                                    |
| ------------ | ----------------------- | -------------------------------------- |
| **Frontend** | React 18 + TypeScript 5 | Type-safe, modern, fast                |
| **Build**    | Vite 7                  | Lightning-fast dev & production builds |
| **Styling**  | Tailwind CSS            | Utility-first, responsive              |
| **State**    | Zustand                 | Lightweight logic                      |
| **Search**   | Fuse.js                 | Fast client-side fuzzy search          |

---

## 📂 Project Structure

```
Halilit-Support-Center/
├── frontend/                 ← React app
│   ├── src/
│   │   ├── components/      
│   │   │   ├── views/       ← Main Views (GalaxyDashboard, SpectrumModule)
│   │   │   └── ui/          ← Reusable atomic components
│   │   ├── lib/             ← Utilities (catalogLoader, search)
│   │   └── store/           ← Global state
│   └── public/data/         ← Generated static JSON catalogs
│
├── backend/                  ← Data pipeline
│   ├── forge_backbone.py     ← Main coordinator
│   └── services/             ← Ingestion scripts
│
└── docs/                     ← Documentation
```

---

## 🔧 Maintenance

### Regenerating Data
To update the product catalog:

```bash
cd backend
python3 forge_backbone.py
```

### Verification
Run the verification suite to ensure system health:

```bash
./verify_workspace.sh
```

---

**Made with ❤️ for Halilit Support Center.**

**Version**: 4.0.0 | **Status**: Production Ready | **Updated**: January 2026
