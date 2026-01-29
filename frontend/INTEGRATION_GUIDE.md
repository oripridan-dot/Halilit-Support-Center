# Integration Guide: 3D Slots in GalaxyDashboard

## Overview

This guide shows how to integrate the new 3D slot environment system into the existing GalaxyDashboard and CategorySlot components.

---

## Current State (Before Integration)

```typescript
// GalaxyDashboard.tsx - Current Card Rendering
<CategorySlot
  id={sub.id}
  name={sub.name}
  image={sub.image}
  mainColor={sector.color}
  onClick={() => onSlotClick(sector.id, sub.id)}
/>
```

The `CategorySlot` component renders static 2D product images with a grayscale-to-color hover effect.

---

## Integration Strategy: Hybrid Approach

We'll implement a **"Lazy 3D Loading"** pattern where:

1. **Default State**: Show fast 2D CategorySlot (instant load)
2. **Hover State**: Spin up 3D environment (on interaction)
3. **Click**: Navigate to detailed product view

### Benefits

- ✅ Fast initial page load (2D images cached)
- ✅ 3D rendered on-demand (saves GPU memory)
- ✅ Smooth user experience (progressive enhancement)
- ✅ Fallback to 2D if 3D fails

---

## Implementation Option 1: Hover-Based Toggle

### Modified CategorySlot Wrapper

```typescript
import { ThreeDSlotEnvironment } from './slots/ThreeDSlotEnvironment';
import { CategorySlot } from './galaxy/CategorySlot';
import { useState } from 'react';

interface EnhancedCategorySlotProps {
  id: string;
  name: string;
  image: string;
  category: string;
  brand: string;
  mainColor: string;
  icon?: React.ElementType;
  onClick: () => void;
  enable3D?: boolean;  // Feature flag
}

export const EnhancedCategorySlot = ({
  id,
  name,
  image,
  category,
  brand,
  mainColor,
  icon,
  onClick,
  enable3D = true,
}: EnhancedCategorySlotProps) => {
  const [showThreeDSlot, setShowThreeDSlot] = useState(false);

  if (showThreeDSlot && enable3D) {
    return (
      <div
        className="relative rounded-lg overflow-hidden aspect-square cursor-pointer"
        onMouseLeave={() => setShowThreeDSlot(false)}
      >
        <ThreeDSlotEnvironment
          category={category}
          brand={brand}
          imageUrl={image}
          height="100%"
        />
        {/* Close button overlay */}
        <button
          className="absolute top-2 right-2 bg-black/50 hover:bg-black/75 text-white p-2 rounded z-20"
          onClick={() => setShowThreeDSlot(false)}
        >
          ✕
        </button>
      </div>
    );
  }

  return (
    <div onMouseEnter={() => enable3D && setShowThreeDSlot(true)}>
      <CategorySlot
        id={id}
        name={name}
        image={image}
        mainColor={mainColor}
        icon={icon}
        onClick={onClick}
      />
    </div>
  );
};
```

### Usage in GalaxyDashboard

```typescript
// In GalaxyDashboard.tsx
<EnhancedCategorySlot
  id={sub.id}
  name={sub.name}
  image={sub.image}
  category={sector.name}      // e.g., "Guitars & Bass"
  brand={extractBrand(sub.id)} // Extract brand from spectrum ID
  mainColor={sector.color}
  icon={sector.iconComponent}
  onClick={() => onSlotClick(sector.id, sub.id)}
  enable3D={true}             // Feature flag
/>
```

---

## Implementation Option 2: Full Replacement Mode

### Replace CategorySlot Entirely

```typescript
// In GalaxyDashboard.tsx, modify the mapping:
{sector.children.map((sub) => (
  <div key={sub.id} className="rounded-lg overflow-hidden">
    <ThreeDSlotEnvironment
      category={sector.name}
      brand={extractBrand(sub.id)}
      imageUrl={sub.image}
      height="280px"
    />
  </div>
))}
```

**Pros**: Cinematic visual consistency  
**Cons**: Higher initial GPU load, slower on weak devices

---

## Helper Function: Brand Extraction

Since categories can contain multiple brands, create a helper to determine brand:

```typescript
// In universalCategories.ts or utilities

/**
 * Extract brand from spectrum ID
 * Example: "boss-ev-1-expression-pedal" → "Boss"
 */
export const extractBrandFromSpectrumId = (spectrumId: string): string => {
  const brandMap: Record<string, string> = {
    // Guitars
    "electric-guitars": "fender",
    "acoustic-guitars": "lag",
    "bass-guitars": "spector",
    "guitar-amps": "marshall",
    "guitar-pedals": "boss",

    // Keys
    "digital-pianos": "nord",
    synthesizers: "moog",

    // Drums
    "acoustic-drums": "pearl",
    cymbals: "paiste",
    "electronic-drums": "roland",

    // Studio
    "studio-monitors": "krk",
    "audio-interfaces": "universalaudio",

    // Live
    "pa-speakers": "rcf",
    mixers: "mackie",
  };

  return brandMap[spectrumId] || "default";
};
```

### Usage

```typescript
const brand = extractBrandFromSpectrumId(sub.id);
const theme = getBrandTheme(brand);

<ThreeDSlotEnvironment
  category={sector.name}
  brand={brand}
  imageUrl={sub.image}
  height="280px"
/>
```

---

## Implementation Option 3: Progressive Enhancement (Recommended)

### Conditional Rendering Based on Screen Size & Device

```typescript
export const ProgressiveEnhancedSlot = ({
  category,
  brand,
  image,
  ...props
}: EnhancedCategorySlotProps) => {
  // Detect if device can handle 3D
  const [canRender3D, setCanRender3D] = useState(() => {
    // Check for GPU capability
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2');
    return !!gl;
  });

  // Detect screen size
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Desktop with capable GPU: Show 3D on hover
  if (!isMobile && canRender3D) {
    return (
      <EnhancedCategorySlot
        category={category}
        brand={brand}
        image={image}
        {...props}
        enable3D={true}
      />
    );
  }

  // Mobile or low-end device: Show 2D
  return (
    <CategorySlot
      image={image}
      mainColor={props.mainColor}
      icon={props.icon}
      {...props}
    />
  );
};
```

---

## Data Enrichment: Adding Brand Info to UNIVERSAL_CATEGORIES

To support brand detection, enhance the spectrum definition:

```typescript
// In universalCategories.ts

export interface UniversalSpectrum extends Spectrum {
  image: string;
  glowColor: string;
  brand?: string; // NEW: Primary brand for this spectrum
}

export const UNIVERSAL_CATEGORIES = CONSOLIDATED_CATEGORIES.map((galaxy) => ({
  ...galaxy,
  iconName: GALAXY_ICONS[galaxy.id] || "HelpCircle",
  spectrum: galaxy.spectrum.map((spec) => ({
    ...spec,
    image: SPECTRUM_IMAGES[spec.id] || "/assets/thumbs/default.svg",
    glowColor: SPECTRUM_GLOW[spec.id] || GLOW_COLORS.roland,
    brand: SPECTRUM_BRANDS[spec.id] || "default", // NEW
  })),
}));

// Add new mapping
const SPECTRUM_BRANDS: Record<string, string> = {
  "electric-guitars": "fender",
  "acoustic-guitars": "lag",
  "bass-guitars": "spector",
  "guitar-amps": "marshall",
  "guitar-pedals": "boss",
  // ... add all spectrum IDs
};
```

### Usage

```typescript
<EnhancedCategorySlot
  category={sector.name}
  brand={sub.brand || 'default'}  // Now directly available
  image={sub.image}
  {...props}
/>
```

---

## Feature Flags for Rollout

Add configuration to enable/disable 3D gradually:

```typescript
// In frontend/src/lib/featureFlags.ts

export const FEATURE_FLAGS = {
  ENABLE_3D_SLOTS: process.env.REACT_APP_3D_SLOTS === 'true',
  LAZY_LOAD_3D: true,
  FALLBACK_TO_2D_ON_ERROR: true,
  SHOW_3D_LOADING_SPINNER: true,
};

// Usage
import { FEATURE_FLAGS } from '@/lib/featureFlags';

{FEATURE_FLAGS.ENABLE_3D_SLOTS && (
  <EnhancedCategorySlot {...props} />
)}
```

Enable via environment variable:

```bash
REACT_APP_3D_SLOTS=true npm run build
```

---

## Error Handling & Fallback

```typescript
export const SafeThreeDSlot = (props: ThreeDSlotEnvironmentProps) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  if (hasError) {
    return (
      <CategorySlot
        image={props.imageUrl}
        mainColor="#999"
        onClick={() => {}}
      />
    );
  }

  return (
    <>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
        </div>
      )}
      <ErrorBoundary onError={() => setHasError(true)}>
        <Suspense fallback={null}>
          <ThreeDSlotEnvironment
            {...props}
            onLoad={() => setIsLoading(false)}
          />
        </Suspense>
      </ErrorBoundary>
    </>
  );
};
```

---

## Recommended Integration Plan

### Phase 1: Safe Rollout

1. Create `EnhancedCategorySlot` wrapper (hybrid approach)
2. Use feature flag `ENABLE_3D_SLOTS=false` by default
3. Deploy to production (uses 2D fallback)
4. Gather performance metrics

### Phase 2: Limited Rollout

1. Enable for desktop users only: `canRender3D && !isMobile`
2. Use hover-based toggle (lazy loading)
3. Rollout to 25% of users

### Phase 3: Full Rollout

1. Monitor performance, user engagement
2. If metrics good, enable for all users
3. Optimize based on feedback

### Phase 4: Full 3D

1. Consider replacing 2D entirely
2. Preload models in background
3. Add advanced features (animation, interaction)

---

## Performance Impact Estimates

| Metric                | 2D Slot | 3D Slot (Lazy) | 3D Slot (Full) |
| --------------------- | ------- | -------------- | -------------- |
| Initial Load Time     | 50ms    | 55ms           | 200ms          |
| Memory Usage          | 2MB     | 8MB            | 15MB           |
| GPU Memory            | 5MB     | 50MB           | 150MB          |
| FPS (on render)       | 60      | 50-55          | 30-45          |
| Mobile Battery Impact | Low     | Medium         | High           |

**Recommendation**: Use lazy-loading hybrid approach for best user experience.

---

## Testing Checklist

- [ ] 2D fallback works when 3D disabled
- [ ] 3D loads on hover/interaction
- [ ] Performance acceptable on target devices
- [ ] Error handling prevents white screens
- [ ] Mobile responsive (scales correctly)
- [ ] Brand colors applied correctly
- [ ] Layout changes based on category
- [ ] No memory leaks on navigate away

---

**Status**: Ready for Implementation  
**Recommended Approach**: Option 3 (Progressive Enhancement)  
**Timeline**: 1-2 weeks for phased rollout
