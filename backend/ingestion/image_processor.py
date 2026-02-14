"""
Enhanced Image Processor — Phase 5 Improvement

Adds to the existing VisualValidator + VisualComparator:
- WebP conversion for smaller file sizes
- Multi-variant generation (hero, thumbnail, gallery, OG)
- Broken/placeholder image detection
- CDN-ready directory structure
- JPEG fallback for browser compatibility

This is a POST-PROCESSING layer — it takes already-validated images from
the existing visual pipeline and optimizes them for production delivery.

Usage:
    processor = ImageProcessor()
    result = processor.process_image("https://example.com/img.jpg", "product-123")
    print(result.variants)  # [ImageVariant(hero), ImageVariant(thumbnail), ...]

Requirements:
    pip install Pillow
"""

import hashlib
import io
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict

logger = logging.getLogger("ImageProcessor")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ImageVariant:
    """A processed image variant (e.g., hero, thumbnail, gallery)."""
    path: str              # Relative path for serving
    width: int
    height: int
    format: str            # "webp" | "jpeg"
    size_bytes: int
    variant_type: str      # "hero" | "thumbnail" | "gallery" | "og" | "original"

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "size_kb": round(self.size_bytes / 1024, 1),
            "variant_type": self.variant_type,
        }


@dataclass
class ImageProcessingResult:
    """Result from processing a single product image."""
    original_url: str
    success: bool
    variants: List[ImageVariant] = field(default_factory=list)
    error: Optional[str] = None
    content_hash: Optional[str] = None
    is_valid: bool = True
    validation_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "original_url": self.original_url,
            "success": self.success,
            "is_valid": self.is_valid,
            "content_hash": self.content_hash,
            "variant_count": len(self.variants),
            "variants": [v.to_dict() for v in self.variants],
            "issues": self.validation_issues,
            "error": self.error,
        }


# Image size presets — each variant serves a specific UI purpose
IMAGE_PRESETS: Dict[str, Dict] = {
    "hero": {
        "max_width": 800,
        "max_height": 800,
        "quality": 85,
        "description": "Main product image on detail page",
    },
    "gallery": {
        "max_width": 600,
        "max_height": 600,
        "quality": 80,
        "description": "Gallery/carousel images",
    },
    "thumbnail": {
        "max_width": 200,
        "max_height": 200,
        "quality": 75,
        "description": "Small thumbnails in product lists/grids",
    },
    "og": {
        "max_width": 1200,
        "max_height": 630,
        "quality": 85,
        "description": "Open Graph meta images for social sharing",
    },
}

# Validation thresholds
MIN_WIDTH = 100
MIN_HEIGHT = 100
MAX_FILE_SIZE_MB = 10


# ---------------------------------------------------------------------------
# Image Processor
# ---------------------------------------------------------------------------

class ImageProcessor:
    """
    Processes product images through validation, optimization, and variant generation.

    Pipeline per image:
    1. Download raw bytes
    2. Validate (dimensions, format, corruption, placeholder detection)
    3. Convert to RGB (handle RGBA/P/LA modes)
    4. Generate variants (hero, thumbnail, gallery, OG)
    5. Save as WebP (primary) + JPEG (fallback)
    6. Output to CDN-ready directory structure

    This complements the existing VisualValidator (which does AI-based
    product matching) by handling the mechanical optimization step.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(
            "frontend/public/data/processed_images"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._stats = {"processed": 0, "failed": 0, "skipped": 0}

    def process_image(
        self,
        image_url: str,
        product_id: str,
        presets: Optional[List[str]] = None,
    ) -> ImageProcessingResult:
        """
        Process a single image URL into optimized variants.

        Args:
            image_url: Source image URL
            product_id: Used to build output directory path
            presets: Which variants to generate (default: all)

        Returns:
            ImageProcessingResult with variants and validation info
        """
        try:
            from PIL import Image
        except ImportError:
            logger.error("Pillow is required: pip install Pillow")
            return ImageProcessingResult(
                original_url=image_url,
                success=False,
                error="Pillow not installed — run: pip install Pillow",
            )

        selected_presets = presets or list(IMAGE_PRESETS.keys())
        result = ImageProcessingResult(original_url=image_url, success=True)

        try:
            # 1. Download
            raw_bytes = self._download_image(image_url)
            result.content_hash = hashlib.md5(raw_bytes).hexdigest()

            # 2. Validate
            img = Image.open(io.BytesIO(raw_bytes))
            validation_issues = self._validate_image(img, len(raw_bytes))
            result.validation_issues = validation_issues

            # Blocking issues → reject
            if any("BLOCK" in issue for issue in validation_issues):
                result.is_valid = False
                result.success = False
                result.error = "; ".join(validation_issues)
                self._stats["failed"] += 1
                return result

            # 3. Convert to RGB for WebP/JPEG output
            img = self._ensure_rgb(img)

            # 4. Generate variants
            for preset_name in selected_presets:
                if preset_name not in IMAGE_PRESETS:
                    continue
                preset = IMAGE_PRESETS[preset_name]
                variant = self._create_variant(
                    img, product_id, preset_name, preset)
                if variant:
                    result.variants.append(variant)

            self._stats["processed"] += 1

        except Exception as e:
            logger.error(f"Image processing failed for {image_url}: {e}")
            result.success = False
            result.error = str(e)
            self._stats["failed"] += 1

        return result

    def process_product_images(
        self, product: dict, product_id: str
    ) -> Dict[str, any]:
        """
        Process ALL images for a product (hero + gallery).

        Args:
            product: Product dict with 'images' field
            product_id: Unique product identifier

        Returns:
            Dict with 'hero' and 'gallery' ImageProcessingResults
        """
        results: Dict[str, any] = {}
        images = product.get("images", {})

        # Process hero image → full variant set
        hero_url = images.get("hero") or images.get("hero_image")
        if hero_url:
            results["hero"] = self.process_image(
                hero_url, product_id, ["hero", "thumbnail", "og"]
            )

        # Process gallery images → gallery + thumbnail only
        gallery_urls = images.get("gallery", [])
        results["gallery"] = []
        for i, url in enumerate(gallery_urls[:10]):  # Cap at 10
            gallery_result = self.process_image(
                url, f"{product_id}/gallery_{i}", ["gallery", "thumbnail"]
            )
            results["gallery"].append(gallery_result)

        return results

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _download_image(self, url: str) -> bytes:
        """Download image bytes from URL with timeout."""
        import urllib.request

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "HalilitSupportCenter/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()

    def _validate_image(self, img, file_size: int) -> List[str]:
        """
        Validate image quality and detect problems.

        Checks:
        - Minimum dimensions (100x100)
        - Maximum file size (10MB)
        - Placeholder detection (solid color images)
        """
        issues: List[str] = []

        w, h = img.size

        if w < MIN_WIDTH or h < MIN_HEIGHT:
            issues.append(
                f"BLOCK: Image too small ({w}x{h}), "
                f"minimum {MIN_WIDTH}x{MIN_HEIGHT}"
            )

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            issues.append(
                f"WARNING: Image very large "
                f"({file_size / 1024 / 1024:.1f}MB)"
            )

        # Placeholder detection — mostly uniform color
        if w > 0 and h > 0:
            try:
                small = img.copy()
                small.thumbnail((10, 10))
                pixels = list(small.getdata())
                unique = len(set(str(p) for p in pixels))
                if unique <= 2:
                    issues.append(
                        "WARNING: Image appears to be a solid color "
                        "or placeholder"
                    )
            except Exception as exc:
                logger.debug("Placeholder detection skipped: %s", exc)

    def _ensure_rgb(self, img):
        """Convert image to RGB mode for WebP/JPEG output."""
        from PIL import Image

        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode in ("RGBA", "LA"):
                background.paste(img, mask=img.split()[-1])
                return background
            return img.convert("RGB")

        if img.mode != "RGB":
            return img.convert("RGB")

        return img

    def _create_variant(
        self,
        img,
        product_id: str,
        variant_name: str,
        preset: dict,
    ) -> Optional[ImageVariant]:
        """Create and save a single image variant."""
        from PIL import Image

        try:
            max_w = preset["max_width"]
            max_h = preset["max_height"]
            quality = preset["quality"]

            # Resize maintaining aspect ratio
            variant_img = img.copy()
            variant_img.thumbnail((max_w, max_h), Image.LANCZOS)

            # Output directory: /processed_images/{product_id}/
            product_dir = self.output_dir / product_id
            product_dir.mkdir(parents=True, exist_ok=True)

            # Save WebP (modern, smaller)
            webp_path = product_dir / f"{variant_name}.webp"
            variant_img.save(webp_path, "WEBP", quality=quality, method=4)

            # Save JPEG fallback
            jpg_path = product_dir / f"{variant_name}.jpg"
            variant_img.save(jpg_path, "JPEG", quality=quality, optimize=True)

            w, h = variant_img.size
            size_bytes = webp_path.stat().st_size

            # Build relative path for serving
            try:
                rel_path = str(
                    webp_path.relative_to(
                        Path("frontend/public")
                    )
                )
            except ValueError:
                rel_path = str(webp_path)

            return ImageVariant(
                path=rel_path,
                width=w,
                height=h,
                format="webp",
                size_bytes=size_bytes,
                variant_type=variant_name,
            )

        except Exception as e:
            logger.error(
                f"Failed to create {variant_name} variant "
                f"for {product_id}: {e}"
            )
            return None

    def get_stats(self) -> dict:
        """Return processing statistics."""
        return dict(self._stats)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_image_processor: Optional[ImageProcessor] = None


def get_image_processor() -> ImageProcessor:
    """Get or create the singleton ImageProcessor."""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor
