# 🆔 PROJECT IDENTITY

**Project:** Halilit Support Center v4.1  
**Status:** ✅ Production Ready  
**Architecture:** Static First (Vite + React + JSON)

## Quick Facts

- **Frontend:** React 18 + TypeScript + Tailwind CSS (Vite)
- **Backend:** Python scripts for data generation (no runtime API)
- **Data:** Pre-generated JSON catalog in `/frontend/public/data/`
- **Routing:** Client-side React Router
- **State:** Zustand stores + Custom hooks
- **Build:** Production-ready with TypeScript strict mode

## Key Directories

```
frontend/src/
├── components/     # React components
├── hooks/         # Data fetching hooks (AsyncResult pattern)
├── lib/           # Utilities, loaders, managers
├── store/         # Zustand state stores
├── types/         # TypeScript interfaces
└── assets/        # Static assets

backend/
├── services/      # Data processors
├── models/        # Data models
├── config/        # Configuration
└── data/          # Generated JSON blueprints
```

## Core Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Three.js** - 3D models
- **Vite** - Build tool
- **Python 3** - Backend data generation

## Standard Patterns

### AsyncResult Hook Pattern
All data hooks return:
```typescript
interface AsyncResult<T> {
  data: T | null
  loading: boolean
  error: Error | null
  isReady: boolean
  retry: () => void
}
```

### Component Standards
- Functional components with hooks
- Props extend `BaseComponentProps`
- Error boundaries for error handling
- Proper cleanup in useEffect

## Key Files

- `README.md` - Project overview
- `FINAL_SUMMARY.md` - Current status
- `frontend/QUICK_REFERENCE.md` - Developer guide
- `frontend/src/COMPONENT_STANDARDS.ts` - Dev rules
- `frontend/src/lib/communicationProtocol.ts` - Type definitions
