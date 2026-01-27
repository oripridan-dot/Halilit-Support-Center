# HSC Frontend v4.1 - Galaxy Edition

Modern React + TypeScript frontend with theatrical 3D slot lighting.

## 🏗️ Architecture: Static First (ONE SOURCE OF TRUTH)

- **Data Source**: All data loaded from `/public/data/*.json` (pre-built static files)
- **No Backend**: Zero runtime API calls, no database, no server dependency
- **State Management**: Zustand for navigation state
- **Search**: Fuse.js for client-side fuzzy search (<50ms)
- **Type Safety**: TypeScript 5 with strict mode
- **Animation**: Framer Motion 12 for 3D theatrical effects

## 🎨 Key Features

- ✅ **Galaxy Dashboard**: 40+ category slots with 3D room geometry
- ✅ **Theatrical Lighting**: Sharp god's beams from angled origins (175°)
- ✅ **Separated Color Origins**: Natural color mixing in 3D space
- ✅ **Depth Perception**: Vignettes, side shadows, perspective floors
- ✅ **Instant Search** with fuzzy matching
- ✅ **Type Safe** end-to-end with TypeScript

## 🚀 Tech Stack

- **React 19.2** - Latest React with improved performance
- **TypeScript 5.9** - Strict type checking
- **Vite 7** - Lightning-fast dev server with SWC & pre-bundling
- **Tailwind CSS 3.4** - Utility-first styling
- **Framer Motion 12** - 3D animations and lighting effects
- **Zustand 5.0** - Minimal state management
- **Fuse.js 7.1** - Fuzzy search
- **Lucide React** - Icon system
- **Framer Motion 12** - Optional animations

## 📁 Project Structure

```
src/
├── components/
│   ├── App.tsx              # Main app component
│   ├── Navigator.tsx        # Category tree navigation
│   ├── Workbench.tsx        # Product detail view
│   ├── ErrorBoundary.tsx    # Error handling
│   ├── ui/                  # Reusable UI components
│   └── smart-views/         # Feature components (TierBar, etc.)
│
├── hooks/
│   ├── useBrandCatalog.ts   # Load brand data
│   ├── useRealtimeSearch.ts # Search integration
│   └── useCopilot.ts        # Copilot integration
│
├── lib/
│   ├── catalogLoader.ts     # ⭐ Load static JSON (ONE WAY)
│   ├── instantSearch.ts     # ⭐ Fuse.js wrapper (ONE WAY)
│   ├── devTools.ts          # Development utilities
│   └── schemas.ts           # Zod validation schemas
│
├── store/
│   └── navigationStore.ts   # Zustand global state
│
└── types/
    └── index.ts             # TypeScript type definitions
```

## 🔧 Development

### Install Dependencies

```bash
pnpm install
```

### Start Dev Server

```bash
pnpm dev
# → http://localhost:5173
```

### Build for Production

```bash
pnpm build
# → Output in dist/
```

### Type Check

```bash
pnpm typecheck
# Or watch mode:
npx tsc --noEmit --watch
```

### Run Tests

```bash
pnpm test           # Unit tests (Vitest)
pnpm test:ui        # Visual test runner
pnpm test:e2e       # E2E tests (Playwright)
pnpm test:coverage  # Coverage report
```

## 📊 Data Loading Pattern

### The ONE WAY to Load Data

```typescript
import { catalogLoader } from "./lib/catalogLoader";

// Load master index
const index = await catalogLoader.loadIndex();

// Load specific brand
const catalog = await catalogLoader.loadBrand("roland");

// Access products
catalog.products.forEach((product) => {
  console.log(product.name);
});
```

### The ONE WAY to Search

```typescript
import { instantSearch } from "./lib/instantSearch";

// Initialize (done automatically in App.tsx)
await instantSearch.initialize();

// Search
const results = instantSearch.search("piano", {
  keys: ["name", "category", "description"],
  limit: 10,
});
```

## 🎨 Styling Approach

### Tailwind CSS + CSS Variables

```tsx
// Component styling
<div className="bg-slate-900 text-slate-100 rounded-lg p-4">
  <h2 className="text-xl font-bold">Product Name</h2>
</div>

// Brand theming with CSS variables
<div style={{
  color: 'var(--brand-primary)',
  borderColor: 'var(--brand-secondary)'
}}>
  Brand-themed content
</div>
```

### CSS Variables (Dynamically set per brand)

```css
:root {
  --brand-primary: #f89a1c; /* Roland Orange */
  --brand-secondary: #18181b;
  --bg-panel: #15171e;
  --text-primary: #f3f4f6;
}
```

## 🧪 Testing

### Unit Tests (Vitest)

```bash
pnpm test
```

Located in `tests/unit/`

### E2E Tests (Playwright)

```bash
pnpm test:e2e
```

Located in `tests/e2e/`

### Test Configuration

- **Vitest**: `vitest.config.ts`
- **Playwright**: `playwright.config.ts`

## 🚀 Production Deployment

### Build

```bash
pnpm build
```

### Preview Build Locally

```bash
pnpm preview
```

### Deploy to Static Hosting

```bash
# Netlify
netlify deploy --dir=dist --prod

# Vercel
vercel --prod

# AWS S3
aws s3 sync dist/ s3://your-bucket/ --acl public-read
```

## 📝 Key Files

| File                           | Purpose                             |
| ------------------------------ | ----------------------------------- |
| `src/App.tsx`                  | Main app, initializes search system |
| `src/components/Navigator.tsx` | Category tree & product list        |
| `src/components/Workbench.tsx` | Product detail view                 |
| `src/lib/catalogLoader.ts`     | Static JSON loader                  |
| `src/lib/instantSearch.ts`     | Fuse.js search wrapper              |
| `src/store/navigationStore.ts` | Zustand state                       |
| `public/data/index.json`       | Master catalog index                |
| `public/data/{brand}.json`     | Brand catalogs                      |

## 🔍 Troubleshooting

### Data Not Loading

```bash
# Verify data files exist
ls -la public/data/*.json

# Should see: index.json, roland.json, boss.json, nord.json
```

### TypeScript Errors

```bash
# Clear cache
rm -rf node_modules/.vite

# Reinstall
pnpm install

# Type check
pnpm typecheck
```

### Search Not Working

Check browser console for initialization errors:

```javascript
// Should see in console:
"✅ Catalog initialized from static data";
```

---

**Version**: 3.7.5  
**Status**: Production Ready  
**Last Updated**: January 22, 2026
// Alternatively, use this for stricter rules
tseslint.configs.strictTypeChecked,
// Optionally, add this for stylistic rules
tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },

},
]);

````

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs["recommended-typescript"],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
]);
````
