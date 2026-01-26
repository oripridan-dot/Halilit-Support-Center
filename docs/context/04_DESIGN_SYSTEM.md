# 🎨 04_DESIGN_SYSTEM.md

**Philosophy:** "See Then Read" - Visual First.

## 🌈 Color Palette (Category Anchors)
The application uses a strict color coding system for the 8 main categories.

```css

...
```

## 📐 Layout Principles
1. **Navigator (Left)**: Fixed interaction point.
2. **Workbench (Center)**: Dynamic content area.
3. **MediaDeck (Bottom)**: Persistent tool control.

## 🖼️ Visual Factory
All product images are processed offline into high-quality WebP with removed backgrounds.
- Source: `backend/visual_factory.py`
- Output: `frontend/public/data/product_images/`
