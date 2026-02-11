# Frontend — React 18 + TypeScript + Vite

## Setup

```bash
pnpm install
pnpm dev          # http://localhost:5173 (proxies API to :8000)
pnpm build        # Production build
pnpm test         # Vitest
```

## Stack

- **React 18** + **TypeScript 5** + **Vite 5**
- **Zustand 5** — app state (navigation, selection)
- **React Query 5** — server state (catalog fetching, caching)
- **Tailwind CSS 3.4** — `slate-900` dark theme, `blue-500` accents
- **Framer Motion** — animations
- **Fuse.js** — client-side fuzzy search (via Web Worker)

## Views

| View            | Path                | Purpose                       |
| --------------- | ------------------- | ----------------------------- |
| GalaxyDashboard | `components/views/` | Category navigation overview  |
| SpectrumModule  | `components/views/` | Product browsing & filtering  |
| ProductPage     | `components/views/` | Full product detail & gallery |

## Data Flow

```
/api/conductor/catalog (backend)
  → useConductorCatalog() hook (React Query)
    → Zustand store
      → View components
```

## Conventions

- Functional components with hooks only (class components only for ErrorBoundary)
- `Product` type imported from `types/index.ts` (generated from backend Pydantic models)
- All product data from `/api/conductor/catalog` — never hardcoded
- Tailwind utility classes — no custom CSS except `index.css` base styles
