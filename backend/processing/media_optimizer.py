from PIL import Image
from pathlib import Path
import logging
import os

logger = logging.getLogger("MediaOptimizer")


def optimize_image(src_path: Path, dest_folder: Path, filename: str = None, max_width: int = 1200, quality: int = 80) -> str:
    """
    Reads an image from src_path, converts it to WebP, resizes it if necessary, 
    and saves it to dest_folder.

    Returns:
        The relative filename of the optimized image (e.g., 'image.webp')
    """
    try:
        if not src_path.exists():
            return None

        # Determine output filename
        original_stem = src_path.stem
        if filename:
            original_stem = Path(filename).stem

        new_filename = f"{original_stem}.webp"
        dest_path = dest_folder / new_filename

        # Skip if already exists (cache)
        if dest_path.exists():
            return new_filename

        with Image.open(src_path) as img:
            # Handle Orientation tag (EXIF) if present, to prevent rotation
            # (Basic PIL usage usually handles this or strips it, but explicitly:
            # For simplicity in this script we trust PIL default loading which strips/ignores unless rotated)

            # Convert modes like P or CMYK to RGB/RGBA
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')

            # Resize Logic
            w, h = img.size
            if w > max_width:
                scale_factor = max_width / w
                new_h = int(h * scale_factor)
                img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
                # logger.info(f"Resized {src_path.name}: {w}x{h} -> {max_width}x{new_h}")

            # Save as WebP
            img.save(dest_path, 'WEBP', quality=quality, optimize=True)

            # Stats (optional logging)
            # original_size = os.path.getsize(src_path)
            # new_size = os.path.getsize(dest_path)
            # reduction = (1 - new_size/original_size) * 100
            # logger.info(f"Optimized {new_filename}: {reduction:.1f}% reduction")

            return new_filename

    except Exception as e:
        logger.error(f"Failed to optimize {src_path}: {e}")
        # Fallback: Copy original if optimization fails?
        # For now, return None so we don't serve broken assets
        return None
