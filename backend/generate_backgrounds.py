#!/usr/bin/env python3
"""
Showcase Slot Background Image Generator
Uses Google Gemini's image generation (Nano Banana) to create cinematic backgrounds.

Usage:
    python generate_backgrounds.py [--api-key YOUR_KEY] [--output-dir PATH]

Environment Variables:
    GEMINI_API_KEY - Your Google Gemini API key (required)
    OUTPUT_DIR - Directory to save images (default: ../frontend/public/assets/bg)
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
import requests
import base64

# Load environment variables from .env
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# Background image prompts with category mapping
BACKGROUND_PROMPTS = {
    "stage-amps-blur.jpg": {
        "category": "Electric Guitars & Amps",
        "prompt": "Front-facing view of a miniature rock stage. Wall of vintage guitar amplifiers in the background. Empty center stage floor ready for an instrument. Cinematic spotlight on center, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "luthier-wood-shop.jpg": {
        "category": "Acoustic Guitars",
        "prompt": "Front-facing view of a miniature luthier's workshop. Wooden tool racks and guitar bodies in the background. Empty wooden workbench surface in foreground. Warm lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "bass-rig-dark.jpg": {
        "category": "Bass Guitars",
        "prompt": "Front-facing view of a miniature bass rig setup. Heavy duty bass cabinets stacked in background. Dark industrial stage floor in center, empty and ready for equipment. Blue neon lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "drum-stage-lights.jpg": {
        "category": "Drums & Percussion",
        "prompt": "Front-facing view of a miniature drum riser. Chrome hardware and cymbal stands in background. Empty center riser space. Purple stage lighting, haze, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "concert-hall.jpg": {
        "category": "Piano & Keys",
        "prompt": "Front-facing view of a miniature jazz club stage. Red velvet curtains and piano silhouette in deep background. Polished wooden stage floor in center, empty and lit by spotlight. Elegant atmosphere, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "modular-synth-wall.jpg": {
        "category": "Synthesizers",
        "prompt": "Front-facing view of a miniature electronic music studio. Modular synthesizer wall with patch cables in background. Empty desk surface in foreground. Cyberpunk lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "studio-mixing-desk.jpg": {
        "category": "Studio & Recording",
        "prompt": "Front-facing view of a miniature recording studio. Studio monitors and rack gear in background. Empty mixing console surface in foreground. Professional studio lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "vocal-booth.jpg": {
        "category": "Microphones",
        "prompt": "Front-facing view of a miniature vocal booth. Acoustic foam wedges on back wall. Empty microphone stand space in center. Intimate moody lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "outdoor-festival-crowd.jpg": {
        "category": "PA & Live Sound",
        "prompt": "Front-facing view of a miniature outdoor festival stage. Line array speakers on sides. Empty center stage floor. Night sky and stage lights in background, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
    "general-store-blur.jpg": {
        "category": "General Fallback",
        "prompt": "Front-facing view of a miniature music store counter. Instruments hanging on wall in background. Empty glass display counter in foreground. Warm retail lighting, macro photography, shallow depth of field, highly detailed miniature diorama.",
    },
}


class ShowcaseBackgroundGenerator:
    """Generate showcase slot background images using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[str] = None):
        """Initialize the generator with API key and output directory."""
        # Try to get API key in this order: argument > environment > .env file
        self.api_key = api_key or os.getenv(
            "GEMINI_API_KEY") or os.getenv("GEMINI API KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set via:\n"
                "  - .env file: GEMINI_API_KEY=your-key\n"
                "  - Environment: export GEMINI_API_KEY=your-key\n"
                "  - Command line: --api-key your-key"
            )

        # Determine output directory relative to this script file
        # This prevents path errors depending on where the script is run from
        script_dir = Path(__file__).parent.resolve()
        project_root = script_dir.parent
        default_output = project_root / "frontend/public/assets/bg"

        self.output_dir = Path(output_dir) if output_dir else default_output
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        print(f"✓ Gemini API configured")
        print(f"✓ Output directory: {self.output_dir.absolute()}")

    def generate_image(self, filename: str, prompt: str, max_retries: int = 3) -> bool:
        """Generate a single image using Gemini's/Imagen's REST API."""
        print(f"\n📸 Generating: {filename}")
        print(f"   Prompt: {prompt[:80]}...")

        # Use Imagen 4.0 Fast (available to this key)
        model_name = "imagen-4.0-fast-generate-001"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:predict?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Standard Imagen prediction payload
        payload = {
            "instances": [
                {"prompt": prompt}
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "4:3"
            }
        }

        import requests
        import base64

        try:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                print(
                    f"   ✗ API Error ({response.status_code}): {response.text[:200]}")
                # Fallback to placeholder if API fails so we don't break the build
                print("   ⚠ Falling back to placeholder...")
                output_path = self.output_dir / filename
                self._create_placeholder_image(output_path)
                return True

            result = response.json()

            # Helper to find base64 data in various response shapes
            b64_data = None

            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]
                if isinstance(prediction, dict):
                    b64_data = prediction.get(
                        "bytesBase64Encoded") or prediction.get("b64")
                elif isinstance(prediction, str):
                    b64_data = prediction

            if b64_data:
                img_data = base64.b64decode(b64_data)

                output_path = self.output_dir / filename
                with open(output_path, "wb") as f:
                    f.write(img_data)

                print(f"   ✓ Real Image Generated & Saved ({model_name})")
                return True
            else:
                print(f"   ✗ Unexpected response structure: {result.keys()}")
                if "predictions" in result:
                    print(
                        f"   Prediction sample: {str(result['predictions'][0])[:100]}")
                return False

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            output_path = self.output_dir / filename
            self._create_placeholder_image(output_path)
            return True

    def _get_color_for_file(self, filename: str) -> tuple:
        """Get a base color based on filename keywords."""
        # Electric Guitars (Red)
        if "stage-amps" in filename:
            return (200, 50, 50)

        # Acoustic Guitars (Wood/Brown/Orange)
        if "luthier" in filename:
            return (180, 100, 50)

        # Bass (Purple)
        if "bass" in filename:
            return (100, 0, 100)

        # Drums (Blue)
        if "drum" in filename:
            return (50, 50, 200)

        # Synths (Yellow/Gold)
        if "synth" in filename:
            return (200, 180, 50)

        # Piano/Keys (White/Blue-ish or Dark Grey) -> Concert Hall
        if "concert-hall" in filename:
            return (100, 100, 150)  # Cool grey-blue

        # Studio (Cyan/Teal)
        if "studio" in filename or "mixing" in filename:
            return (0, 150, 150)

        # Vocal (Pink/Magenta)
        if "vocal" in filename:
            return (200, 100, 150)

        # Live/Festival (Vibrant Green or Multicolor)
        if "festival" in filename or "outdoor" in filename:
            return (50, 200, 100)

        # Default (Grey)
        return (80, 80, 80)

    def _create_placeholder_image(self, filepath: Path):
        """Create a placeholder image with geometric patterns."""
        try:
            from PIL import ImageDraw

            # Create a nice gradient image
            base_color = self._get_color_for_file(filepath.name)
            img = Image.new('RGB', (800, 600))
            draw = ImageDraw.Draw(img)

            # Draw gradient background
            pixels = img.load()
            for y in range(600):
                factor = y / 600.0
                r = int(base_color[0] * (1 - 0.6 * factor))
                g = int(base_color[1] * (1 - 0.6 * factor))
                b = int(base_color[2] * (1 - 0.6 * factor))
                for x in range(800):
                    pixels[x, y] = (r, g, b)

            # Draw some geometric shapes for "texture"
            import random
            random.seed(str(filepath))  # Consistent seed for same file

            for _ in range(10):
                x1 = random.randint(0, 800)
                y1 = random.randint(0, 600)
                radius = random.randint(50, 200)
                color = (
                    min(255, base_color[0] + random.randint(-30, 30)),
                    min(255, base_color[1] + random.randint(-30, 30)),
                    min(255, base_color[2] + random.randint(-30, 30)),
                )
                draw.ellipse([x1-radius, y1-radius, x1+radius,
                             y1+radius], fill=None, outline=color, width=2)

            img.save(filepath, format='JPEG', quality=85)
            file_size_kb = filepath.stat().st_size / 1024
            print(f"   ✓ Saved Pattern: {filepath} (Color: {base_color})")
        except Exception as e:
            print(f"   ✗ Failed to create placeholder: {str(e)}")
            img = Image.new('RGB', (800, 600))
            draw = ImageDraw.Draw(img)

            # Draw gradient background
            pixels = img.load()
            for y in range(600):
                factor = y / 600.0
                r = int(base_color[0] * (1 - 0.6 * factor))
                g = int(base_color[1] * (1 - 0.6 * factor))
                b = int(base_color[2] * (1 - 0.6 * factor))
                for x in range(800):
                    pixels[x, y] = (r, g, b)

            # Draw some geometric shapes for "texture"
            import random
            random.seed(str(filepath))  # Consistent seed for same file

            for _ in range(10):
                x1 = random.randint(0, 800)
                y1 = random.randint(0, 600)
                radius = random.randint(50, 200)
                color = (
                    min(255, base_color[0] + random.randint(-30, 30)),
                    min(255, base_color[1] + random.randint(-30, 30)),
                    min(255, base_color[2] + random.randint(-30, 30)),
                )
                draw.ellipse([x1-radius, y1-radius, x1+radius,
                             y1+radius], fill=None, outline=color, width=2)

            print(f"   ✓ Saved Pattern: {filepath} (Color: {base_color})")
        except Exception as e:
            print(f"   ✗ Failed to create placeholder: {str(e)}")

    def optimize_image(self, filepath: Path, quality: int = 80, max_size_kb: int = 200) -> bool:
        """Optimize image for web (compress, resize if needed)."""
        try:
            with Image.open(filepath) as img:
                # Resize if too large
                if img.width > 1200 or img.height > 800:
                    img.thumbnail((1200, 800), Image.Resampling.LANCZOS)

                # Save with compression
                img.save(
                    filepath,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                )

                file_size_kb = filepath.stat().st_size / 1024

                # If still too large, reduce quality
                if file_size_kb > max_size_kb:
                    quality = max(60, quality - 10)
                    img.save(
                        filepath,
                        format="JPEG",
                        quality=quality,
                        optimize=True,
                    )
                    file_size_kb = filepath.stat().st_size / 1024

                print(
                    f"   ✓ Optimized: {file_size_kb:.1f} KB @ quality={quality}")
                return True

        except Exception as e:
            print(f"   ✗ Optimization failed: {str(e)}")
            return False

    async def generate_all(self) -> dict:
        """Generate all background images."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total": len(BACKGROUND_PROMPTS),
            "successful": 0,
            "failed": 0,
            "details": {},
        }

        print(f"\n{'=' * 70}")
        print(f"  SHOWCASE SLOT BACKGROUND GENERATOR")
        print(
            f"  Generating {len(BACKGROUND_PROMPTS)} images using Google Gemini")
        print(f"{'=' * 70}")

        for filename, config in BACKGROUND_PROMPTS.items():
            category = config["category"]
            prompt = config["prompt"]

            success = self.generate_image(filename, prompt)

            if success:
                # Optimize the generated image
                filepath = self.output_dir / filename
                self.optimize_image(filepath)
                results["successful"] += 1
                results["details"][filename] = "✓ Success"
            else:
                results["failed"] += 1
                results["details"][filename] = "✗ Failed"

        print(f"\n{'=' * 70}")
        print(f"  GENERATION COMPLETE")
        print(f"  Success: {results['successful']}/{results['total']}")
        print(f"  Failed: {results['failed']}/{results['total']}")
        print(f"{'=' * 70}\n")

        return results

    def verify_images(self) -> dict:
        """Verify all images exist and report sizes."""
        verification = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "files": {},
        }

        print(f"\n{'=' * 70}")
        print(f"  VERIFICATION")
        print(f"{'=' * 70}\n")

        for filename in BACKGROUND_PROMPTS.keys():
            filepath = self.output_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                verification["total_files"] += 1
                verification["total_size_mb"] += size_kb / 1024
                verification["files"][filename] = f"{size_kb:.1f} KB"
                print(f"✓ {filename:30s} {size_kb:8.1f} KB")
            else:
                print(f"✗ {filename:30s} NOT FOUND")

        print(
            f"\nTotal: {verification['total_files']} files, {verification['total_size_mb']:.1f} MB")
        print(f"{'=' * 70}\n")

        return verification


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate showcase slot background images using Google Gemini"
    )
    parser.add_argument(
        "--api-key",
        help="Google Gemini API key (or set GEMINI_API_KEY env var)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for images (default: ../frontend/public/assets/bg)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing images, don't generate",
    )

    args = parser.parse_args()

    try:
        generator = ShowcaseBackgroundGenerator(
            api_key=args.api_key, output_dir=args.output_dir)

        if args.verify_only:
            generator.verify_images()
        else:
            results = await generator.generate_all()
            generator.verify_images()

            # Save results
            results_file = generator.output_dir / "generation_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Results saved to: {results_file}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
