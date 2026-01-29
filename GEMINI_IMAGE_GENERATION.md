# Generate Showcase Backgrounds with Google Gemini

Quick guide to generate all 10 background images using Google Gemini's image generation.

## Prerequisites

1. **Google Gemini API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Click "Create API Key"
   - Copy your key (keep it safe!)

2. **Dependencies** (already installed)
   ```bash
   pip install google-generativeai pillow
   ```

## Usage

### Method 1: Environment Variable (Recommended)

```bash
# Set your API key as environment variable
export GEMINI_API_KEY="your-api-key-here"

# Run the generator
cd backend
python generate_backgrounds.py
```

### Method 2: Command Line Argument

```bash
cd backend
python generate_backgrounds.py --api-key "your-api-key-here"
```

### Method 3: Custom Output Directory

```bash
cd backend
python generate_backgrounds.py \
  --api-key "your-api-key-here" \
  --output-dir "/path/to/output"
```

## What It Does

The script:

1. ✅ Generates 10 cinematic background images using Google **Imagen 4.0 Fast** (`imagen-4.0-fast-generate-001`)
2. ✅ Saves them to `frontend/public/assets/bg/`
3. ✅ Automatically compresses and optimizes each image
4. ✅ Resizes to 1200×800px (16:9 aspect ratio)
5. ✅ Ensures file size < 200KB per image
6. ✅ Creates a `generation_results.json` report

## Images Generated

| File                         | Category                |
| ---------------------------- | ----------------------- |
| `stage-amps-blur.jpg`        | Electric Guitars & Amps |
| `luthier-wood-shop.jpg`      | Acoustic Guitars        |
| `bass-rig-dark.jpg`          | Bass Guitars            |
| `drum-stage-lights.jpg`      | Drums & Percussion      |
| `concert-hall.jpg`           | Piano & Keys            |
| `modular-synth-wall.jpg`     | Synthesizers            |
| `studio-mixing-desk.jpg`     | Studio & Recording      |
| `vocal-booth.jpg`            | Microphones             |
| `outdoor-festival-crowd.jpg` | PA & Live Sound         |
| `general-store-blur.jpg`     | General Fallback        |

## Verify Existing Images

To check what images exist and their file sizes:

```bash
cd backend
python generate_backgrounds.py --verify-only
```

Output:

```
======================================================================
  VERIFICATION
======================================================================

✓ stage-amps-blur.jpg                 145.3 KB
✓ luthier-wood-shop.jpg               152.1 KB
✓ bass-rig-dark.jpg                   138.7 KB
...

Total: 10 files, 1.4 MB
======================================================================
```

## Troubleshooting

### "GEMINI_API_KEY not provided"

```bash
# Make sure you set the environment variable
export GEMINI_API_KEY="your-key-here"
python generate_backgrounds.py
```

### "google-generativeai not installed"

```bash
pip install -r requirements.txt
```

### Images look wrong / wrong aspect ratio

The script automatically resizes to 1200×800px. If you want to regenerate, just run the script again—it will overwrite the existing images.

### Images too large (> 200KB)

The script automatically reduces quality if needed. You can also manually compress using:

```bash
convert image.jpg -quality 75 -resize 1200x800 optimized.jpg
```

## API Cost

Google Gemini image generation is **extremely affordable**:

- ~$0.02-0.04 per image
- Total for 10 images: ~$0.20-0.40 USD

## After Generation

1. Images automatically appear in `frontend/public/assets/bg/`
2. Refresh your browser to see them in the app
3. No code changes needed—they'll load automatically!

## Generated Images Report

After running, check `frontend/public/assets/bg/generation_results.json` for detailed results:

```json
{
  "timestamp": "2026-01-28T23:15:30.123456",
  "total": 10,
  "successful": 10,
  "failed": 0,
  "details": {
    "stage-amps-blur.jpg": "✓ Success",
    "luthier-wood-shop.jpg": "✓ Success",
    ...
  }
}
```

---

**Ready to generate?** Just set your API key and run:

```bash
export GEMINI_API_KEY="your-key"
cd backend && python generate_backgrounds.py
```

The app will automatically use the generated images! 🎨
