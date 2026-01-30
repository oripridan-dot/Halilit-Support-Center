import json
import asyncio
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Import the official parser
try:
    from backend.processing.official_parser import parse_official_page
    from backend.processing.media_optimizer import optimize_image
except ImportError:
    # Handle case where run from root
    import sys
    sys.path.append(".")
    from backend.processing.official_parser import parse_official_page
    from backend.processing.media_optimizer import optimize_image

# Base paths
RAW_DATA_DIR = Path("backend/data/raw")
PROCESSED_DATA_DIR = Path("backend/data/processed")
PROJECT_ROOT = Path("/workspaces/Halilit-Support-Center")
ASSETS_MANUALS_DIR = Path("frontend/public/assets/manuals")
ASSETS_IMAGES_DIR = Path("frontend/public/assets/images")
ASSETS_LOGOS_DIR = Path("frontend/public/assets/logos")


class IngestionProcessor:
    def __init__(self):
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        ASSETS_LOGOS_DIR.mkdir(parents=True, exist_ok=True)
        # Load manifest once
        self.manifest = {}
        manifest_path = Path("backend/ingestion/manifest.json")
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                self.manifest = json.load(f)

    def get_brand_name(self, brand_id: str) -> str:
        if not self.manifest:
            return brand_id.replace("-", " ").title()
        return next((b["name"] for b in self.manifest.get("brands", []) if b["id"] == brand_id), brand_id.replace("-", " ").title())

    def _load_brand_info(self, brand_id: str):
        path = Path(f"backend/data/brands/{brand_id}.json")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle Logo Coping
            if data.get("logo_local_path"):
                src = Path(data["logo_local_path"])
                if src.exists():
                    dst_filename = src.name
                    dst = ASSETS_LOGOS_DIR / dst_filename
                    shutil.copy2(src, dst)
                    # Update paths for frontend consumption
                    data["logo_url"] = f"/assets/logos/{dst_filename}"
                    del data["logo_local_path"]

            return data
        return None

    async def process_brand(self, brand_id: str):
        """
        Processes all raw content for a specific brand.
        """
        print(f"Processing brand: {brand_id}")
        brand_name = self.get_brand_name(brand_id)

        # Load Brand Info/Metadata
        brand_info = self._load_brand_info(brand_id)

        halilit_dir = RAW_DATA_DIR / "halilit" / brand_id

        products = []

        # 1. Process Halilit Data (Commercial Source of Truth)
        if halilit_dir.exists():
            for html_file in halilit_dir.glob("*.html"):
                if html_file.name == "brand_listing.html":
                    continue

                try:
                    product_data = self._parse_halilit_product(
                        html_file, brand_name, brand_id)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    print(f"Error parsing {html_file.name}: {e}")

        # 2. Process Official Data (Technical Source of Truth)
        # Enrich products with official manuals found in raw/official/{brand_id}/{halilit_id}
        official_base = RAW_DATA_DIR / "official" / brand_id

        for product in products:
            hid = product.get("halilit_id")
            if not hid:
                continue

            prod_official_dir = official_base / hid
            if prod_official_dir.exists():
                # --- Step A: Parse Official Page Metadata ---
                official_html = prod_official_dir / "official_page.html"
                if official_html.exists():
                    try:
                        print(f"  > Parsing official data for {hid}...")
                        official_data = parse_official_page(official_html)

                        # OVERWRITE with Official Data ("Knowledge Source of Truth")
                        if official_data.get("name"):
                            product["name"] = official_data["name"]

                        if official_data.get("description"):
                            product["description"] = official_data["description"]
                            # Clean up short description too as it might be Hebrew
                            # Using first 100 chars of official desc
                            desc_text = BeautifulSoup(
                                official_data["description"], "lxml").get_text()
                            product["short_description"] = desc_text[:150] + \
                                "..." if len(desc_text) > 150 else desc_text

                        if official_data.get("specs"):
                            product["specs"] = official_data["specs"]
                            # Also update features list from specs or description?
                            # For now, let's trust specs as the primary feature list

                        # Enrich with new fields
                        if official_data.get("box_contents"):
                            product["box_contents"] = official_data["box_contents"]

                        if official_data.get("related_products"):
                            product["related_products"] = official_data["related_products"]

                        if official_data.get("category"):
                            product["category"] = official_data["category"]

                        if official_data.get("sub_category"):
                            product["sub_category"] = official_data["sub_category"]

                    except Exception as e:
                        print(
                            f"  ! Error parsing official page for {hid}: {e}")

                # --- Step B: Handle Assets (PDFs & Images) ---
                manuals = []
                official_images = []

                target_manual_dir = ASSETS_MANUALS_DIR / brand_id / hid
                target_manual_dir.mkdir(parents=True, exist_ok=True)

                target_image_dir = ASSETS_IMAGES_DIR / brand_id / hid
                target_image_dir.mkdir(parents=True, exist_ok=True)

                for asset_file in prod_official_dir.iterdir():
                    if asset_file.is_dir():
                        continue

                    ext = asset_file.suffix.lower()

                    # Handle Manuals
                    if ext == ".pdf":
                        try:
                            shutil.copy2(
                                asset_file, target_manual_dir / asset_file.name)
                            label = asset_file.stem.replace(
                                "-", " ").replace("_", " ").title()
                            manuals.append({
                                "url": f"/assets/manuals/{brand_id}/{hid}/{asset_file.name}",
                                "type": "pdf",
                                "label": label,
                                "source_domain": "brand_official",
                                "extracted_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            print(f"Error copying manual {asset_file}: {e}")

                    # Handle HTML Manuals (Captured)
                    elif asset_file.name.startswith("doc_") and ext == ".html":
                        label = asset_file.stem.replace(
                            "doc_", "").replace("_", " ").title()
                        # We don't host the HTML usually, but we can indicate we have it.
                        # Or we can treat it as a "Knowledge Base Article" type.
                        # For now, let's just log it as a type "html_snapshot" but not copy it to public assets
                        # unless we want to serve static HTML snapshots (which might be broken without CSS/Images).
                        # Better: Store the existence.

                        manuals.append({
                            "url": None,  # No public URL for the raw HTML snapshot yet
                            "type": "html_snapshot",
                            "label": label,
                            "source_domain": "brand_official",
                            "extracted_at": datetime.now().isoformat()
                        })

                    # Handle Images (JPG, PNG, WEBP)
                    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        try:
                            # Use Image Optimizer instead of shutil.copy2
                            new_filename = optimize_image(
                                asset_file, target_image_dir, max_width=1200, quality=80)
                            if new_filename:
                                official_images.append(
                                    f"/assets/images/{brand_id}/{hid}/{new_filename}")
                            else:
                                # Fallback if optimization failed (very rare) logic could go here
                                pass
                        except Exception as e:
                            print(f"Error processing image {asset_file}: {e}")

                    # Handle Media (MP4, ZIP)
                    # Just copy them raw for now
                    elif ext in [".mp4", ".mov", ".webm", ".zip"]:
                        try:
                            # We might need a separate folder structure for 3d/video if we want organization,
                            # but for now, dump them in 'images' (assets) or a 'media' folder?
                            # Let's put them in 'assets/media' to be clean.
                            target_media_dir = PROCESSED_DATA_DIR.parent.parent.parent / \
                                "frontend/public/assets/media" / brand_id / hid
                            target_media_dir.mkdir(parents=True, exist_ok=True)

                            shutil.copy2(
                                asset_file, target_media_dir / asset_file.name)

                            # Add to a new field "media_files"
                            if "media_files" not in product:
                                product["media_files"] = []

                            product["media_files"].append({
                                "url": f"/assets/media/{brand_id}/{hid}/{asset_file.name}",
                                "type": ext.replace(".", "")
                            })
                        except Exception as e:
                            print(f"Error copying media {asset_file}: {e}")

                if manuals:
                    product["official_manuals"] = manuals
                    # print(f"  > Enriched {hid} with {len(manuals)} manuals.")

                if official_images:
                    # Sort for consistency
                    sorted_imgs = sorted(official_images)
                    if len(sorted_imgs) > 0:
                        product["images"] = {
                            "main": sorted_imgs[0],
                            "thumbnail": sorted_imgs[0],
                            "gallery": sorted_imgs
                        }
                        product["image_url"] = sorted_imgs[0]
                        print(
                            f"  > Replaced images for {hid} with {len(official_images)} official assets.")

        # 3. Save Consolidated Catalog Fragment
        self._save_catalog_fragment(brand_id, brand_name, products, brand_info)
        print(f"Completed {brand_id}: {len(products)} products processed.")

    def _parse_halilit_product(self, html_path: Path, brand_name: str, brand_id: str) -> dict:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "lxml")

        # Determine Slug / ID
        slug = html_path.stem

        # Extract ID (from input Value if possible, or filename)
        halilit_id_el = soup.select_one("input#item_id")
        halilit_id = halilit_id_el["value"] if halilit_id_el else slug.split(
            "-")[0]

        # Unified ID format
        unified_id = f"{brand_id}_{halilit_id}"

        # Extract Title
        title_el = soup.select_one(
            "#item_current_title h1 span[itemprop='name']")
        title = title_el.get_text(
            strip=True) if title_el else "Unknown Product"

        # Extract Subtitle (Short Description)
        subtitle_el = soup.select_one("#item_current_sub_title span")
        subtitle = subtitle_el.get_text(strip=True) if subtitle_el else ""

        # Extract Price
        price_el = soup.select_one(".price_value")
        price_raw = price_el.get_text(strip=True) if price_el else "0"
        price = float(price_raw.replace("₪", "").replace(
            ",", "").strip()) if price_raw else 0.0

        # Extract Images
        images_list = []
        og_image = soup.select_one("meta[property='og:image']")
        if og_image and og_image.get("content"):
            images_list.append(og_image["content"])

        # Construct Images Object
        images_obj = {
            "main": images_list[0] if images_list else "",
            "thumbnail": images_list[0] if images_list else "",
            "gallery": images_list
        }

        # Extract Description (Main Content)
        desc_el = soup.select_one("#item_content .desc")
        description_html = str(desc_el) if desc_el else ""

        # Extract Features (Bullets)
        features = []
        features_el = soup.select("#item_features .specifications li")
        for ft in features_el:
            features.append(ft.get_text(strip=True))

        return {
            "id": unified_id,
            "halilit_id": halilit_id,  # Keep original ID reference
            "name": title,
            "brand": brand_name,
            "description": description_html,
            "short_description": subtitle,
            "category": "uncategorized",
            "price": price,
            "pricing": {
                "regular_price": price,
                "currency": "ILS",
                "source": "halilit"
            },
            "status": "IN_STOCK",
            "images": images_obj,
            "image_url": images_obj["main"],
            "features": features,
            "specs": [],
            "source_url": f"https://www.halilit.com/items/{slug}",
            "generated_at": datetime.now().isoformat()
        }

    def _save_catalog_fragment(self, brand_id: str, brand_name: str, products: list, brand_info: dict = None):
        output_file = PROCESSED_DATA_DIR / f"{brand_id}.json"

        data = {
            "brand_id": brand_id,
            "brand_name": brand_name,
            "brand_info": brand_info,
            "products": products,
            "metadata": {
                "count": len(products),
                "processed_at": datetime.now().isoformat()
            }
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    processor = IngestionProcessor()

    if len(sys.argv) > 1:
        target_brand = sys.argv[1]
        asyncio.run(processor.process_brand(target_brand))
    else:
        print("Usage: python backend/processing/processor.py <brand_id>")
