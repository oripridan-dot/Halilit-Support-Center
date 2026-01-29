# 3D Environment System - Quick Reference Guide

## 🎯 Quick Start

### 1. Display a 3D Environment Slot

```typescript
import { ThreeDSlotEnvironment } from '@/components/views/slots/ThreeDSlotEnvironment';

<ThreeDSlotEnvironment
  category="Guitars & Bass"
  brand="Fender"
  imageUrl="/data/thumbnails/fender_stratocaster.jpg"
  height="500px"
/>
```

### 2. Get a Brand Theme

```typescript
import { getBrandTheme } from "@/styles/brandThemes";

const theme = getBrandTheme("Nord");
// → { primary: "#e31e24", secondary: "#550000", emissive: "#FF0033", intensity: 1.8 }
```

### 3. Configure Scene Behavior

```typescript
import { useThreeDScene } from "@/hooks/useThreeDScene";

const { theme, layoutType, config } = useThreeDScene(
  "Drums & Percussion",
  "Pearl",
);
// → layoutType: "scatter", config: { scale: 0.75, rotationSpeed: 0.005, ... }
```

---

## 📁 File Locations

| Component             | Path                                                            |
| --------------------- | --------------------------------------------------------------- |
| ThreeDSlotEnvironment | `frontend/src/components/views/slots/ThreeDSlotEnvironment.tsx` |
| ProductStand          | `frontend/src/components/views/slots/ProductStand.tsx`          |
| useThreeDScene        | `frontend/src/hooks/useThreeDScene.ts`                          |
| Brand Themes          | `frontend/src/styles/brandThemes.ts`                            |

---

## 🎨 Brand Themes

### Available Brands

**Guitars & Bass**: fender, gibson, ibanez, vintage, solar, washburn, rapier  
**Amps**: marshall, orange, vox, ampeg, boss, roland  
**Keys**: nord, moog, arturia, teenageengineering  
**Studio**: admaudio, krk, universalaudio, warmaudio  
**Live**: mackie, rcf, akaiprofessional

### Theme Properties

```typescript
interface BrandTheme {
  primary: string; // Main brand color (hex)
  secondary: string; // Accent color
  emissive: string; // Light emission color
  intensity: number; // Lighting multiplier (0.6 - 2.0)
}
```

---

## 🏗️ Layout Types by Category

| Category          | Layout    | Count    | Description                  |
| ----------------- | --------- | -------- | ---------------------------- |
| Guitar / Bass     | `wall`    | 12 items | Curved back wall arrangement |
| Amp / Cabinet     | `stack`   | 9 items  | Vertical stacking (3×3 grid) |
| Drum / Percussion | `scatter` | 12 items | Randomized placement         |
| Key / Synth       | `circle`  | 8 items  | Ring arrangement             |
| Default           | `hero`    | 1 item   | Single featured product      |

---

## 🎬 Component Props

### ThreeDSlotEnvironment

```typescript
interface ThreeDSlotEnvironmentProps {
  category: string; // e.g., "Guitars & Bass"
  brand: string; // e.g., "Fender"
  imageUrl: string; // Product image path
  modelUrl?: string; // Optional GLB model path
  height?: number | string; // Container height (default: "400px")
}
```

### ProductStand

```typescript
interface ProductStandProps {
  imageUrl: string; // Product image URL
  category: string; // Category name (used to select stand type)
  brandColor: string; // Hex color for rim lighting
  scale?: number; // Scale multiplier (default: 1)
}
```

### useThreeDScene

```typescript
const {
  theme, // BrandTheme object
  layoutType, // 'wall' | 'circle' | 'stack' | 'scatter' | 'hero'
  config, // { scale, rotationSpeed, floatSpeed, floatIntensity }
} = useThreeDScene(category, brand, modelUrl);
```

---

## 🔧 Common Customizations

### Change Background Layout Count

```typescript
// In ThreeDSlotEnvironment.tsx, SlotScene component
<WallLayout count={20} spacing={2.5} />  // More items
<CircleLayout count={12} radius={4} />   // Larger circle
<StackLayout count={12} />                // More stacks
```

### Adjust Lighting Intensity

```typescript
// In ThreeDSlotEnvironment.tsx
<directionalLight
  intensity={theme.intensity * 2.0}  // Double the intensity
  // ...
/>
```

### Customize Procedural Props

```typescript
// In ProductStand.tsx
const GuitarStandProp = ({ color = "#2a2a2a" }) => {
  // Modify geometry, materials, positioning here
};
```

### Change Camera Position/Angle

```typescript
// In ThreeDSlotEnvironment.tsx
<PerspectiveCamera
  position={[0, 1.5, 6.0]}  // Adjust view
  fov={40}                   // Wider/narrower field of view
/>
```

---

## 🎯 Layout Type Selection Logic

```typescript
const getLayoutType = (category: string) => {
  const cat = category.toLowerCase();

  if (cat.includes("guitar") || cat.includes("bass")) return "wall"; // Wall of guitars
  if (cat.includes("amp") || cat.includes("cabinet")) return "stack"; // Stack of amps
  if (cat.includes("drum") || cat.includes("percussion")) return "scatter"; // Scattered drums
  if (cat.includes("key") || cat.includes("synth") || cat.includes("piano"))
    return "circle"; // Circle of synths

  return "hero"; // Default single item
};
```

---

## 🎨 Lighting Architecture

### Three-Point Lighting System

1. **Ambient Light** (0.5 intensity)
   - Base illumination for entire scene
   - Prevents dark shadows

2. **Directional Key Light** (brand-colored)
   - Main highlight source
   - Casts shadows (1024×1024 shadow map)
   - Position: [8, 12, 8] (front-top-right)
   - Intensity: theme.intensity × 1.2

3. **Point Rim Light** (secondary color)
   - Back accent light
   - Creates depth separation
   - Position: [-8, 6, -8] (back-top-left)
   - Intensity: theme.intensity × 0.6

### Brand Color Injection

```
theme.primary   → directionalLight color (key light)
theme.secondary → pointLight color (rim light)
theme.emissive  → ProductStand rim light glow
theme.intensity → Multiplier for all lights
```

---

## 📦 Dependencies

```json
{
  "dependencies": {
    "three": "^0.163.0",
    "@react-three/fiber": "^13.x.x",
    "@react-three/drei": "^9.x.x"
  }
}
```

### Key Imports

```typescript
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Instances,
  Instance,
  Environment,
  ContactShadows,
  PerspectiveCamera,
  useTexture,
} from "@react-three/drei";
import * as THREE from "three";
```

---

## ⚡ Performance Tips

### Optimize GPU Usage

- Use `dpr={[1, 2]}` on Canvas for mobile efficiency
- Limit shadow map resolution to 1024×1024
- Use ContactShadows instead of full shadow maps for static geometry

### Optimize Textures

- Pre-load images via `useTexture()` preload
- Use compressed image formats (WebP)
- Keep product images under 500KB

### Optimize Rendering

- Keep procedural item counts under 50 (via Instances)
- Use `Suspense` boundaries for async loading
- Lazy load 3D slots with `React.lazy()`

### Monitor Performance

```typescript
// Three.js DevTools
import { Dev } from '@react-three/drei';

<Canvas>
  <Dev />  {/* Performance profiler */}
</Canvas>
```

---

## 🐛 Troubleshooting

### Issue: Images appear stretched

**Solution**: Check ProductStand component's aspect ratio calculation

```typescript
const aspect = texture.image.width / texture.image.height;
// Should match your actual image dimensions
```

### Issue: Dark/dim lighting

**Solution**: Increase theme intensity or adjust light multipliers

```typescript
<directionalLight intensity={theme.intensity * 2.0} />
```

### Issue: Background items not visible

**Solution**: Ensure Instances component has items positioned correctly

```typescript
// Check WallLayout, CircleLayout, or StackLayout positioning
console.log("Positions:", positions); // Debug output
```

### Issue: Canvas not rendering

**Solution**: Check for Suspense fallback and ensure Three.js is properly initialized

```typescript
<Suspense fallback={<LoadingFallback />}>
  <SlotScene {...props} />
</Suspense>
```

---

## 📚 Example Integration

### In a Product Card Component

```typescript
import { ThreeDSlotEnvironment } from '@/components/views/slots/ThreeDSlotEnvironment';
import { useState } from 'react';

export function ProductCard({ product }) {
  const [show3D, setShow3D] = useState(false);

  return (
    <div className="relative group">
      {show3D ? (
        <ThreeDSlotEnvironment
          category={product.category}
          brand={product.brand}
          imageUrl={product.imageUrl}
          height="300px"
        />
      ) : (
        <img
          src={product.imageUrl}
          alt={product.name}
          onMouseEnter={() => setShow3D(true)}
          onMouseLeave={() => setShow3D(false)}
        />
      )}
    </div>
  );
}
```

---

## 🚀 Deployment Checklist

- [ ] All TypeScript types validated
- [ ] Build completes without errors: `npm run build`
- [ ] No console warnings or errors
- [ ] Images load correctly
- [ ] Lighting looks cinematic
- [ ] Performance acceptable on target devices
- [ ] Fallback UI works if 3D fails to load
- [ ] Responsive layout on mobile

---

**Version**: 1.0.0  
**Last Updated**: January 28, 2026  
**Status**: Production Ready ✅
