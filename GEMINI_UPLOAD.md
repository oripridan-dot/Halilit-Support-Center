# 🎹 Halilit Support Center - Complete Source Code

**Project:** Musical Instrument Support Center v4.1  
**Architecture:** Static-First React SPA with 3D Models  
**Status:** Production Ready

---

## 📋 PROJECT OVERVIEW

A static-first support center for musical instruments built with React, TypeScript, and Three.js. The backend generates static JSON catalogs that the frontend consumes. No runtime API - everything is pre-generated static assets.

### Tech Stack
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Vite
- **Backend:** Python (data generation only)
- **3D:** Three.js + Blender exports
- **State:** Zustand
- **Build:** Vite

---

## 🏗️ CORE ARCHITECTURE

### Communication Pattern (AsyncResult)
All async hooks return this standardized interface:
```typescript
interface AsyncResult<T> {
  data: T | null
  loading: boolean
  error: Error | null
  isReady: boolean
  retry: () => void
}
```

---

## 📁 SOURCE CODE STRUCTURE

```
frontend/src/
├── components/          # React UI components
│   ├── GlobalSearch.tsx
│   ├── views/          # Page views
│   └── ui/             # Reusable UI elements
├── hooks/              # Data fetching hooks (AsyncResult pattern)
│   ├── useBrandCatalog.ts
│   ├── useCategoryCatalog.ts
│   ├── useRealtimeSearch.ts
│   ├── useCategoryProducts.ts
│   ├── useTaxonomy.ts
│   └── useThreeDScene.ts
├── lib/                # Utilities and managers
│   ├── communicationProtocol.ts
│   ├── catalogLoader.ts
│   ├── instantSearch.ts
│   └── productModelLoader.ts
├── store/              # Zustand state management
│   └── navigationStore.ts
└── types/              # TypeScript interfaces

backend/
├── models/             # Data models
│   ├── brand_taxonomy.py
│   ├── category_consolidator.py
│   └── product_hierarchy.py
├── config/             # Configuration
└── core/               # Core utilities
```

---

## 🔑 KEY FILES & THEIR ROLES

### 1. Communication Protocol
**File:** `frontend/src/lib/communicationProtocol.ts`
- Defines AsyncResult<T> interface
- EventHandler<T> for callbacks
- BaseComponentProps for components
- All async patterns documented

### 2. Component Standards
**File:** `frontend/src/COMPONENT_STANDARDS.ts`
- 10 critical development rules
- Best practices with examples
- Pre-submission checklist

### 3. Navigation Store
**File:** `frontend/src/store/navigationStore.ts`
- Global navigation state
- Product pop-up management
- Filter management
- Error tracking

### 4. Catalog Loader
**File:** `frontend/src/lib/catalogLoader.ts`
- Loads pre-generated JSON catalogs
- Caches with localStorage
- Validates schema with Zod

### 5. Search System
**File:** `frontend/src/lib/instantSearch.ts`
- Real-time search across catalog
- Instant results
- Brand/category filtering

---

## 🎯 DATA FETCHING HOOKS

### useBrandCatalog
```typescript
// Load products from specific brand
const { data: catalog, loading, error, isReady, retry } = 
  useBrandCatalog('roland')
```

### useCategoryCatalog
```typescript
// Load products from category/spectrum
const { data, loading, error, isReady, retry } = 
  useCategoryCatalog('keys-production')
```

### useRealtimeSearch
```typescript
// Real-time search results
const { data: results, loading, error, isReady, retry } = 
  useRealtimeSearch(query, { limit: 10 })
```

### useCategoryProducts
```typescript
// Products filtered by subcategory
const { data: products, loading, error, isReady, retry } = 
  useCategoryProducts(subcategoryId)
```

### useTaxonomy
```typescript
// Brand taxonomy structure
const { data: taxonomy, loading, error, isReady, retry } = 
  useTaxonomy('roland')
```

### useThreeDScene
```typescript
// 3D scene management
const { data: scene, loading, error, isReady, retry } = 
  useThreeDScene(sceneConfig)
```

---

## 🎨 COMPONENT PATTERNS

### Standard Functional Component
```typescript
import { BaseComponentProps } from '../lib/communicationProtocol'

interface MyComponentProps extends BaseComponentProps {
  productId: string
  onSelect?: (id: string) => void
}

export const MyComponent = ({ 
  productId, 
  onSelect,
  className 
}: MyComponentProps) => {
  const { data, loading, error } = useBrandCatalog(brandId)
  
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div className={className}>
      {/* Component JSX */}
    </div>
  )
}
```

---

## 🗂️ STATE MANAGEMENT (Zustand)

### Navigation Store
```typescript
import { useNavigationStore } from '../store/navigationStore'

export const MyComponent = () => {
  const { 
    activeTribeId, 
    openProductPop, 
    closeProductPop,
    goToGalaxy 
  } = useNavigationStore()
  
  return (
    <button onClick={() => openProductPop('product-id')}>
      View Product
    </button>
  )
}
```

---

## ⚙️ SETUP & DEVELOPMENT

### Frontend Development
```bash
cd frontend
npm install
npm run dev        # Start dev server on :5173
npm run build      # Production build
npm run preview    # Preview production build
```

### Backend (Data Generation)
```bash
cd backend
pip install -r requirements.txt
python forge_backbone.py  # Generate catalogs
```

---

## 📊 DATA FLOW

1. **Backend generates** static JSON files (`forge_backbone.py`)
2. **Generated JSON** stored in `frontend/public/data/`
3. **Frontend loads** JSON with `catalogLoader.ts`
4. **React components** render using hooks (AsyncResult pattern)
5. **Zustand store** manages global state
6. **Three.js** renders 3D models from `frontend/public/models/`

---

## 🔄 Error Handling

All async operations follow this pattern:

```typescript
const { data, loading, error, isReady, retry } = useMyHook()

if (loading) return <LoadingState />
if (error) return <ErrorState error={error} onRetry={retry} />
if (isReady) return <DataView data={data} />
```

---

## 📦 Key Dependencies

- **react**: 18.x
- **typescript**: Latest
- **zustand**: State management
- **three.js**: 3D rendering
- **tailwind-css**: Styling
- **vite**: Build tool
- **zod**: Schema validation
- **framer-motion**: Animations

---

## 🚀 3D Models

Located in: `frontend/public/models/`
- `guitars/` - Electric guitars
- `synths/` - Synthesizers
- `drums/` - Drum kits
- `amps/` - Amplifiers

All Blender exports (.obj/.mtl format)

---

## 🎯 BEST PRACTICES

1. **Always use AsyncResult pattern** for async hooks
2. **Error boundaries** around major sections
3. **Memoize callbacks** with useCallback when passed to children
4. **Use Zustand hooks** for global state
5. **Type everything** with TypeScript
6. **Clean up effects** (return cleanup function)

---

## 📝 FILE LOCATIONS

- **Component Standards:** `frontend/src/COMPONENT_STANDARDS.ts`
- **Communication Protocol:** `frontend/src/lib/communicationProtocol.ts`
- **Dev Guide:** `frontend/QUICK_REFERENCE.md`
- **Main README:** `README.md`

---

## ✨ KEY FEATURES

✅ Static-first architecture (no runtime API)
✅ Full 3D model integration
✅ Real-time search
✅ Brand-specific catalogs
✅ Product filtering by category
✅ Taxonomy system
✅ Error handling & retry logic
✅ TypeScript strict mode
✅ Responsive design with Tailwind
✅ Production ready

---

## 🔗 IMPORTANT FILES TO REVIEW

For understanding the codebase:
1. `frontend/src/COMPONENT_STANDARDS.ts` - Development rules
2. `frontend/src/lib/communicationProtocol.ts` - Type definitions
3. `frontend/QUICK_REFERENCE.md` - Implementation guide
4. `frontend/src/hooks/` - See how AsyncResult is used
5. `frontend/src/store/navigationStore.ts` - State management example

---

**Status:** ✅ Production Ready | 🟢 All Systems Active
