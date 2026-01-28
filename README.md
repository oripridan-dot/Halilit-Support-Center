# Halilit Support Center

[![Status](https://img.shields.io/badge/status-production-brightgreen)](https://img.shields.io/badge/status-production-brightgreen)
[![TypeScript](https://img.shields.io/badge/typescript-5.9+-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/react-19.2-blue)](https://react.dev)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)

A fast, static-first support center catalog system. Browse 5,000+ musical instruments and products with zero API overhead.

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
Backend Pipeline (Python)
    ↓
Static JSON Assets
    ↓
React Frontend (TypeScript)
    ↓
Browser
```

## 📂 Project Structure

```
frontend/                  # React + TypeScript + Tailwind
├── src/
│   ├── components/       # React components
│   ├── lib/             # Utilities
│   ├── store/           # Zustand state management
│   └── types/           # TypeScript types
└── public/data/         # Generated static catalogs (JSON)

backend/                  # Python data pipeline
├── forge_backbone.py    # Main catalog generation
├── mass_ingest_protocol.py
├── services/            # Data scrapers & processors
├── models/              # Pydantic data models
└── data/
    ├── blueprints/      # Raw brand specifications
    ├── vault/           # Raw Halilit data
    └── catalogs_brand/  # Processed data (git-ignored)

docs/                     # Architecture & integration docs
```

## 🔧 Backend Operations

### Generate Catalogs

```bash
cd backend
python3 forge_backbone.py
```

Output generated to `frontend/public/data/`

## 📦 Tech Stack

| Component       | Technology                       |
| --------------- | -------------------------------- |
| **Frontend**    | React 19 + TypeScript 5 + Vite 7 |
| **Styling**     | Tailwind CSS                     |
| **State**       | Zustand                          |
| **Search**      | Fuse.js                          |
| **Backend**     | Python 3.11+                     |
| **Data Models** | Pydantic                         |

## 📝 License

See LICENSE file for details.

---

**Version**: 4.1.0 | **Release**: v4.1 | **Status**: Production | **Updated**: January 28, 2026 | **Branch**: main
