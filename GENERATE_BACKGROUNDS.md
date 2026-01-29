# Generate Background Images for Showcase Slots

This document provides detailed instructions for generating the 10 background images needed for the Cinematic Showcase Slots system.

## Overview

The ShowcaseSlot component displays high-quality background images that match each product category. These images should have:

- **Heavy blur/bokeh effect** for depth
- **Dark, moody lighting** (studio/professional atmosphere)
- **High contrast** for text overlay readability
- **Neutral color palette** so brand colors stand out
- **16:9 aspect ratio** (widescreen)
- **~150KB file size** (compressed JPG)

---

## Quick Start

1. **Generate** using Midjourney (Discord), DALL-E 3 (ChatGPT), or Stable Diffusion
2. **Select** the darkest, most blurred version
3. **Download** as JPG (highest quality)
4. **Compress** to ~150KB using [TinyJPG](https://tinyjpg.com) or [Squoosh](https://squoosh.app)
5. **Resize** to 1200×800px
6. **Save** to `frontend/public/assets/bg/`

---

## Image Generation Prompts (Copy & Paste)

### 1. Electric Guitars → `stage-amps-blur.jpg`

```
A blurred background photo of a wall of vintage guitar amplifiers in a dark recording
studio. Warm glowing tubes, black grill cloth, leather textures. Cinematic lighting,
shallow depth of field, 8k resolution, macro photography style, dark atmosphere,
out of focus. --ar 16:9
```

**Alternative (if first doesn't work):**

```
Close-up bokeh of guitar amplifier tubes glowing warm orange in a dark studio. Shallow
depth of field, professional photography, moody lighting, black and orange tones.
```

---

### 2. Acoustic Guitars → `luthier-wood-shop.jpg`

```
A blurred background photo of a luthier's workbench. Wood shavings, raw maple and
rosewood textures, acoustic guitar bodies hanging in the background. Soft warm window
light, dusty atmosphere, extremely shallow depth of field, bokeh, dark brown tones.
--ar 16:9
```

**Alternative:**

```
Wooden guitar workbench with hand tools, wood dust, partially finished acoustic guitar
in background. Warm window light, bokeh out of focus, artisanal craftsman atmosphere.
```

---

### 3. Bass Guitars → `bass-rig-dark.jpg`

```
A blurred close-up of heavy duty bass amplifier cabinets and thick instrument cables
on a concrete floor. Industrial vibe, metallic textures, dark grey and blue lighting.
Out of focus, cinematic 35mm lens, underground club atmosphere. --ar 16:9
```

**Alternative:**

```
Bass amplifier speaker cabinets stacked in a dark room. Heavy gauge cables, industrial
metal textures, moody blue and grey lighting, bokeh background.
```

---

### 4. Drums & Percussion → `drum-stage-lights.jpg`

```
A blurred view from behind a drum kit looking out at a dark stage. Chrome cymbal stands,
drum hardware, stage haze, purple and blue stage lights in the background. High contrast,
bokeh lights, concert atmosphere, 8k photorealistic. --ar 16:9
```

**Alternative:**

```
Drum kit silhouette on a dark concert stage. Stage fog, purple and blue spotlights
blurred in background, professional photography, atmospheric lighting.
```

---

### 5. Piano & Keys → `concert-hall.jpg`

```
A blurred background of a grand piano silhouette in a dark jazz club. Polished black
wood reflections, soft spotlight, red velvet curtain in very far background. Elegant,
sophisticated atmosphere, shallow depth of field, noir style. --ar 16:9
```

**Alternative:**

```
Grand piano keys in warm soft light, jazz club ambiance, velvet curtains slightly
visible out of focus, elegant and moody atmosphere.
```

---

### 6. Synths & Modular → `modular-synth-wall.jpg`

```
A blurred background of a modular synthesizer wall. Patch cables, blinking LED lights
(red, green, amber), knobs and metallic panels. Cyberpunk studio vibe, dark room,
glowing electronics, macro photography, heavy bokeh. --ar 16:9
```

**Alternative:**

```
Close-up of modular synthesizer with glowing LED lights. Patch cables, knobs, metallic
surfaces. Dark room, cyberpunk aesthetic, electronic glow.
```

---

### 7. Studio & Recording → `studio-mixing-desk.jpg`

```
A blurred background POV sitting at a professional audio mixing console. Faders, meters,
studio monitor speakers in the distance. Soundproofing foam texture on walls. Dark grey
and orange color palette, professional studio lighting, out of focus. --ar 16:9
```

**Alternative:**

```
Professional mixing console with faders and knobs. Studio monitors on stands in
background. Acoustic foam walls, professional lighting, blurred focus.
```

---

### 8. Microphones → `vocal-booth.jpg`

```
A blurred background of a professional vocal booth. Acoustic foam wedges, pop filter
silhouette, microphone stand. Intimate atmosphere, soft shadow lighting, dark grey and
black tones, high fidelity texture. --ar 16:9
```

**Alternative:**

```
Close-up of professional microphone with pop filter. Acoustic foam padding blurred
in background. Intimate studio ambiance, soft professional lighting.
```

---

### 9. PA & Live Sound → `outdoor-festival-crowd.jpg`

```
A blurred background of an outdoor music festival stage at night. Massive line array
speaker stacks, trussing, crowd silhouette in distance. Atmospheric smoke, spotlights,
epic scale, dark night sky, out of focus. --ar 16:9
```

**Alternative:**

```
Large outdoor concert stage with massive speaker systems and stage lighting. Crowd
silhouettes, stage fog, night sky. Epic festival atmosphere.
```

---

### 10. Default/Fallback → `general-store-blur.jpg`

```
A blurred background of a modern music store interior. Instruments hanging on walls,
string lights, warm ambient lighting. Professional retail space, shallow depth of field,
welcoming but sophisticated atmosphere. --ar 16:9
```

**Alternative:**

```
Music store interior with instruments on display. Warm lighting, bokeh effect,
professional retail ambiance.
```

---

## File Specifications

| Property        | Value                          |
| --------------- | ------------------------------ |
| **Format**      | JPG (high quality)             |
| **Dimensions**  | 1200×800px (16:9 aspect ratio) |
| **File Size**   | 100–200 KB (after compression) |
| **Quality**     | 80–85% (JPEG quality)          |
| **Color Space** | sRGB                           |

---

## Compression & Processing Steps

### Using TinyJPG (Web-based, Free)

1. Go to https://tinyjpg.com
2. Drag and drop your generated image
3. Download the compressed version
4. Rename to match the filename in the table above
5. Verify file size is under 200KB

### Using Squoosh (Google's Web Tool, Free)

1. Go to https://squoosh.app
2. Upload your image
3. Set:
   - **Format:** JPG
   - **Quality:** 75–80
   - **Resize:** 1200×800px (if needed)
4. Download and save

### Using ImageMagick (Command Line)

```bash
convert input.jpg -resize 1200x800 -quality 80 -strip output.jpg
```

---

## Upload Instructions

Once your images are compressed and sized correctly:

```bash
# Copy images to the public assets directory
cp stage-amps-blur.jpg /path/to/frontend/public/assets/bg/
cp luthier-wood-shop.jpg /path/to/frontend/public/assets/bg/
cp bass-rig-dark.jpg /path/to/frontend/public/assets/bg/
cp drum-stage-lights.jpg /path/to/frontend/public/assets/bg/
cp concert-hall.jpg /path/to/frontend/public/assets/bg/
cp modular-synth-wall.jpg /path/to/frontend/public/assets/bg/
cp studio-mixing-desk.jpg /path/to/frontend/public/assets/bg/
cp vocal-booth.jpg /path/to/frontend/public/assets/bg/
cp outdoor-festival-crowd.jpg /path/to/frontend/public/assets/bg/
cp general-store-blur.jpg /path/to/frontend/public/assets/bg/
```

---

## Fallback System

If images are not yet available, the component automatically uses **CSS gradients** as fallbacks:

```typescript
// Example fallback for Electric Guitars
fallbackGradient: 'linear-gradient(135deg, #2a1a0a 0%, #1a0a00 50%, #4a3a2a 100%)',
```

This means **the app will work beautifully even without the images** while you generate them.

---

## Recommended Tools

### AI Image Generation (Free Tier Available)

- **Midjourney** (Recommended for realism) - https://www.midjourney.com
- **DALL-E 3** (via ChatGPT) - https://chat.openai.com
- **Stable Diffusion** (Free, self-hosted) - https://huggingface.co/spaces/stabilityai/stable-diffusion

### Image Compression (Free)

- **TinyJPG** - https://tinyjpg.com (best compression)
- **Squoosh** - https://squoosh.app (Google's tool, no upload limit)

### Batch Processing

- **ImageMagick** (command line, powerful)
- **ffmpeg** (video + image processing)

---

## Tips for Best Results

1. **Request HIGH CONTRAST** - Ask for "high contrast" and "dark atmosphere" in your prompt
2. **Emphasize BLUR** - Use words like "shallow depth of field", "bokeh", "out of focus", "blurred"
3. **Specify LIGHTING** - Mention "cinematic lighting", "moody", "studio lights"
4. **Darker is Better** - Choose the darkest version—text needs contrast
5. **Test the Overlay** - Imagine a brand color gradient on top; make sure text is readable

---

## Quality Checklist

- [ ] Image is dark enough (RGB: ~30-50 brightness on average)
- [ ] Blur/bokeh effect is strong (background should be out of focus)
- [ ] Subject matter matches category (e.g., amps for guitars)
- [ ] File size is under 200KB
- [ ] Dimensions are 1200×800px
- [ ] Text overlay is readable over the gradient + image
- [ ] No watermarks or AI artifact artifacts visible
- [ ] Color palette is neutral (blacks, greys, browns, not bright colors)

---

## Example: Full Workflow

```bash
# 1. Generate image in Midjourney/DALL-E
# 2. Download as PNG or JPG

# 3. Resize and compress
convert stage-amps-raw.jpg \
  -resize 1200x800 \
  -quality 80 \
  -strip \
  stage-amps-blur.jpg

# 4. Verify file size
ls -lh stage-amps-blur.jpg
# Output: -rw-r--r-- 1 user 147K stage-amps-blur.jpg ✓

# 5. Copy to project
cp stage-amps-blur.jpg /workspaces/Halilit-Support-Center/frontend/public/assets/bg/

# 6. Verify in browser
# http://localhost:5173/ → Should display with background image
```

---

## Troubleshooting

### Images Not Loading

- Check file path: `frontend/public/assets/bg/<filename>.jpg`
- Verify filenames match exactly in `slotBackgrounds.ts`
- Check browser console for 404 errors
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)

### Slow Load Times

- Ensure JPEG quality is 75–80 (not 100)
- Target file size: 100–150KB per image
- Consider using a CDN for final production

### Text Not Readable

- Image might be too bright; generate darker version
- Increase gradient overlay opacity (change `opacity-80` to `opacity-90`)
- Boost blur/bokeh effect

---

## Next Steps

1. ✅ Generate all 10 images using the prompts above
2. ✅ Compress and resize to 1200×800px
3. ✅ Copy to `frontend/public/assets/bg/`
4. ✅ Test in browser (http://localhost:5173)
5. ✅ Verify fallback gradients work if images missing

---

**Questions?** The ShowcaseSlot component has built-in fallback gradients, so development can continue while you generate images at your pace!
