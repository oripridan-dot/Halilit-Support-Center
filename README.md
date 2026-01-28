# 🎹 Halilit Support Center v4.1

**Status:** ✅ Production Ready

## What is this?

A **static-first** support center for musical instruments. Pre-generated JSON catalog + React SPA frontend with 3D models.

## Quick Start

```bash
# Frontend
cd frontend && npm install && npm run dev

# Backend (generates data)
cd backend && pip install -r requirements.txt
```

## Key Tech

- **Frontend:** React 18 + TypeScript + Tailwind + Three.js
- **Backend:** Python (data generation only)
- **Data:** Static JSON in `/frontend/public/data/`
- **Architecture:** No runtime API, all static

## Core Files

- `frontend/src/hooks/` - Data fetching (AsyncResult pattern)
- `frontend/src/lib/communicationProtocol.ts` - Type definitions
- `frontend/src/COMPONENT_STANDARDS.ts` - Dev rules
- `frontend/QUICK_REFERENCE.md` - Implementation guide

## Pattern Used

All async operations return:
```typescript
{ data, loading, error, isReady, retry }
```

## 3D Models

- Electric guitars
- Synthesizers  
- Drum kits
- Amplifiers

All powered by Three.js and Blender exports.
