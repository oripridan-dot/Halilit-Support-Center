"""
� HALILIT CATALOG SYSTEM
=========================

The "Halilit Catalog" architecture: Pre-calculate everything.
Scrapes → Raw Data → Refiner → Golden Record (Static JSON) → Frontend

This script runs offline to build verified, static catalog data that the frontend consumes instantly.
No runtime API calls. No database queries. Just pristine JSON.

Usage:
    python3 forge_backbone.py
    
Result:
    frontend/public/data/ is populated with:
    - index.json (The Spine - Master Catalog Index)
    - <brand>.json (Individual Brand Catalogs)
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging
import requests
import urllib.request
import urllib.error
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import base64
from services.visual_factory import VisualFactory
from models.taxonomy_registry import TaxonomyRegistry, get_registry
from services.catalog_verifier import CatalogVerifier

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
SOURCE_DIR = Path("data/blueprints")  # Where scraper outputs live (Data Vault)
PUBLIC_DATA_PATH = Path("../frontend/public/data")  # The "Live" destination
LOGOS_DIR = PUBLIC_DATA_PATH / "logos"  # Logo destination
CATALOG_VERSION = "3.9.0"

# Brand color themes (WCAG AA compliant)
BRAND_THEMES = {
    "roland": {
        "primary": "#f89a1c",  # Roland Orange
        "secondary": "#18181b",
        "accent": "#ffffff",
        "background": "#18181b",
        "text": "#ffffff"
    },
    "boss": {
        "primary": "#0055a4",  # Boss Blue
        "secondary": "#0f172a",
        "accent": "#bfdbfe",
        "background": "#020617",
        "text": "#ffffff"
    },
    "nord": {
        "primary": "#e31e24",  # Nord Red
        "secondary": "#450a0a",
        "accent": "#fbbf24",
        "background": "#450a0a",
        "text": "#ffffff"
    },
    "moog": {
        "primary": "#000000",
        "secondary": "#5c4033", # Wood
        "accent": "#22c55e",
        "background": "#1c1917",
        "text": "#e5e7eb"
    },
    "adam-audio": {
        "primary": "#000000",
        "secondary": "#1c1917",
        "accent": "#fee2e2", # Pale Red
        "background": "#000000",
        "text": "#ffffff"
    },
    "teenage-engineering": {
        "primary": "#e5e5e5",
        "secondary": "#ff4d00", # TE Orange
        "accent": "#000000",
        "background": "#f0f0f0",
        "text": "#000000"
    },
    "universal-audio": {
        "primary": "#1f2937",
        "secondary": "#111827",
        "accent": "#3b82f6",
        "background": "#000000",
        "text": "#f3f4f6"
    },
    "akai-professional": {
        "primary": "#ff0000", # Akai Red
        "secondary": "#000000",
        "accent": "#ffffff",
        "background": "#1a1a1a",
        "text": "#ffffff"
    },
    "warm-audio": {
        "primary": "#ea580c", # Warm Orange
        "secondary": "#431407",
        "accent": "#fb923c",
        "background": "#2a150d",
        "text": "#ffedd5"
    },
    "mackie": {
        "primary": "#00a651", # Mackie Green
        "secondary": "#000000",
        "accent": "#86efac",
        "background": "#101010",
        "text": "#ffffff"
    }
}


class HalilitCatalog:
    """The Halilit Catalog System - Transforms raw data into production-ready static JSON catalogs."""
    
    def __init__(self):
        self.source_dir = SOURCE_DIR
        self.output_dir = PUBLIC_DATA_PATH
        # Initialize Visual Factory
        self.visual_factory = VisualFactory()
        # Initialize Taxonomy Registry for category validation
        self.taxonomy_registry = get_registry()
        
        # Flat structure matching Frontend Interface (MasterIndex)
        self.master_index = {
            "version": CATALOG_VERSION,
            "build_timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "static_production",
            "total_products": 0,
            "total_verified": 0,
            "brands": [],
            "search_graph": []
        }
        self.stats = {
            "brands_processed": 0,
            "products_total": 0,
            "images_verified": 0,
            "errors": []
        }
        self.lock = threading.Lock()
    
    def _download_logo(self, logo_url: str, brand_slug: str) -> str:
        """
        Manage brand logos. 
        PRIORITY 1: Use local override file in /assets/logos/ (Manual VIP treatment)
        PRIORITY 2: Fetch from official brand website (config/brand_maps.py)
        PRIORITY 3: Download from provided URL
        """
        # PRIORITY 1: Check Manual Local Overrides
        # In Docker workspace, we map paths relative to frontend/public
        # Path relative to PUBLIC_DATA_PATH (which is frontend/public/data)
        
        # We look in frontend/public/assets/logos
        assets_logo_dir = self.output_dir.parent / "assets" / "logos"
        known_logo_files = [
            f"{brand_slug}_logo.svg",
            f"{brand_slug}.svg",
            f"{brand_slug}_logo.png",
            f"{brand_slug}_logo.jpg",
            f"{brand_slug}_logo.jpeg",
            f"{brand_slug}_logo.webp",
            f"{brand_slug}_logo.gif"
        ]
        
        for filename in known_logo_files:
            local_file = assets_logo_dir / filename
            if local_file.exists():
                logger.info(f"       ⭐ Using local VIP logo for {brand_slug}: {filename}")
                return f"/assets/logos/{filename}"
        
        # PRIORITY 2: Try to get official logo from BRAND_MAPS (official brand website)
        official_logo_url = None
        try:
            from config.brand_maps import BRAND_MAPS
            if brand_slug in BRAND_MAPS:
                official_logo_url = BRAND_MAPS[brand_slug].get('logo_url')
                if official_logo_url:
                    logger.info(f"       📍 Using official brand logo from BRAND_MAPS: {official_logo_url}")
                    logo_url = official_logo_url
        except Exception as e:
            logger.debug(f"      ℹ️ Could not load BRAND_MAPS: {e}")
        
        # PRIORITY 3: Download (if logo_url is available)
        if not logo_url or not logo_url.startswith('http'):
            return logo_url or f"/assets/logos/{brand_slug}_logo.png"
        
        try:
            # Create logos directory
            logos_dir = self.output_dir / "logos"
            logos_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension from URL
            ext = '.svg' if '.svg' in logo_url else '.png'
            local_path = logos_dir / f"{brand_slug}_logo{ext}"
            
            # Skip if already downloaded
            if local_path.exists():
                return f"/data/logos/{brand_slug}_logo{ext}"
            
            # Download with timeout (Standardized via requests)
            headers = {'User-Agent': 'Mozilla/5.0 (Halilit Catalog Builder)'}
            response = requests.get(logo_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"      ✓ Downloaded logo: {brand_slug} ({len(response.content)} bytes)")
                return f"/data/logos/{brand_slug}_logo{ext}"
            else:
                logger.info(f"      ⚪ Logo skipped (Status {response.status_code})")
                return logo_url
        
        except Exception as e:
            logger.info(f"      ⚪ Logo download failed: {e}")
            # Fallback: return original URL and let browser fetch it
            return logo_url or f"/assets/logos/{brand_slug}_logo.png"
    
    def _strip_hebrew(self, text: str) -> str:
        """Remove Hebrew characters from text."""
        if not text:
            return ""
        return ''.join(char for char in text if not ("\u0590" <= char <= "\u05FF"))

    def _enforce_naming_convention(self, name: str) -> str:
        """
        Enforce Halilit Naming Standards:
        1. Remove Hebrew text to standardize on English-only catalog
        2. Title Case (e.g. "GRAND PIANO" -> "Grand Piano")
        3. Clean unnecessary spaces
        4. Preserve known acronyms (optional expansion)
        """
        if not name:
            return ""
        
        # 0. Strip Hebrew Characters (Bilingual Cleanup)
        # Often Halilit has "תיק לגיטרה Boss CB-20" -> We want "Boss CB-20"
        name = self._strip_hebrew(name)
        
        # 1. Clean spaces
        clean_name = " ".join(name.split())
        
        # 2. Fix ALL CAPS (if length > 3 to avoid acronyms like 'RD-88')
        # We detect if the ratio of uppercase letters is high
        upper_ratio = sum(1 for c in clean_name if c.isupper()) / len(clean_name) if len(clean_name) > 0 else 0
        if upper_ratio > 0.8 and len(clean_name) > 4:
            # Convert to Title Case
            clean_name = clean_name.title()
            
            # Fix specific acronyms that get broken by .title()
            # e.g. "Tr-08" -> "TR-08"
            replacements = {
               "Tr-": "TR-",
               "Tb-": "TB-",
               "Juno-": "JUNO-",
               "Rd-": "RD-",
               "Fp-": "FP-",
               "Usb": "USB",
               "Midi": "MIDI",
               "Dj": "DJ"
            }
            for k, v in replacements.items():
                clean_name = clean_name.replace(k, v)
                
        return clean_name

    def build(self):
        """Main Catalog Build Process"""
        logger.info(f"📚 [CATALOG] Building Halilit Catalog v{CATALOG_VERSION}...")
        logger.info(f"   Source: {self.source_dir.absolute()}")
        logger.info(f"   Output: {self.output_dir.absolute()}")
        
        try:
            # 1. Prepare Workspace
            self._prepare_workspace()
            
            # 2. Export Taxonomy Registry (before processing brands)
            self._export_taxonomy()
            
            # 3. Process Each Brand
            self._forge_brands()
            
            # 4. Finalize Catalog
            self._finalize_catalog()
            
            # 5. Verification
            self._verify_output()
            
            # 6. Report
            self._report()
            
            logger.info("✅ [CATALOG] Complete. System ready at frontend/public/data/index.json")
            return True
            
        except Exception as e:
            logger.error(f"❌ [CATALOG] Critical failure: {e}")
            return False
    
    def _export_taxonomy(self):
        """Export taxonomy registry to frontend for category navigation."""
        logger.info("   [1.5/5] Exporting Taxonomy Registry...")
        taxonomy_path = self.output_dir / "taxonomy.json"
        self.taxonomy_registry.export_to_frontend(taxonomy_path)
        logger.info(f"      ✓ Taxonomy exported: {len(self.taxonomy_registry.get_all_brands())} brands")
    
    def _prepare_workspace(self):
        """Ensure output directory exists and is clean."""
        logger.info("   [1/4] Preparing catalog workspace...")
        
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)
            logger.info(f"      Created {self.output_dir}")
        
        logger.info(f"      ✓ Catalog workspace ready")
    
    def _forge_brands(self):
        """Process each brand catalog and generate static files."""
        logger.info("   [2/4] Building brand catalogs...")
        
        if not self.source_dir.exists():
            logger.warning(f"      Source directory {self.source_dir} does not exist")
            logger.info("      Checking for catalogs_unified instead...")
            alt_source = Path("./data/catalogs_unified")
            if alt_source.exists():
                self.source_dir = alt_source
            else:
                logger.warning("      No source data found. Using empty catalog.")
                return
        
        catalog_files = list(self.source_dir.glob("*.json"))
        
        if not catalog_files:
            logger.warning(f"      No JSON files found in {self.source_dir}")
            return
        
        # Filter out "-brand.json" and "_brand.json" files to avoid duplicates (only process catalogs)
        catalog_files = [f for f in catalog_files if not ('_brand.json' in f.name or '-brand.json' in f.name)]
        
        MAX_WORKERS = 8 # Parallel processing
        logger.info(f"      🚀 Accelerating with {MAX_WORKERS} concurrent workers...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {executor.submit(self._process_brand, cf): cf for cf in catalog_files}
            
            for future in as_completed(future_to_file):
                cf = future_to_file[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"      ❌ Failed: {cf.name} - {e}")
                    with self.lock:
                        self.stats["errors"].append(str(e))
    
    def _process_brand(self, catalog_file: Path):
        """Process a single brand catalog."""
        
        try:
            with open(catalog_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Extract Brand Info
            if isinstance(raw_data, list):
                # Blueprint Format (List of products)
                # Cleanup filename: "cordoba-guitars_blueprint" -> "Cordoba Guitars"
                brand_name = catalog_file.stem.replace('_blueprint', '').replace('-', ' ').replace('_', ' ').title()
                
                # FALLBACK: If blueprint is empty, try to load commercial data instead
                if len(raw_data) == 0:
                    base_slug = catalog_file.stem.replace('_blueprint', '')
                    commercial_file = self.source_dir / f"{base_slug}_commercial.json"
                    if commercial_file.exists():
                        logger.info(f"      🔄 Blueprint empty, using commercial data: {base_slug}")
                        with open(commercial_file, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                        if not isinstance(raw_data, list):
                            raw_data = raw_data.get('products', [])
                
                # NORMALIZE: Convert list to expected dictionary structure
                # This prevents "list indices must be integers" error later when doing raw_data['products'] = ...
                # or when passing to _refine_brand_data
                normalized_data = {
                    "brand_name": brand_name,
                    "products": raw_data,
                    "generated_at": datetime.utcnow().isoformat()
                }
                raw_data = normalized_data
                products = raw_data['products']
            else:
                # Legacy Format (Dict with products key)
                brand_name = raw_data.get('brand_name') or raw_data.get('name') or catalog_file.stem.replace('_', ' ').title()
                products = raw_data.get('products', [])

            # Remove "Catalog" or "Brand" suffix from brand name for slug
            brand_name_clean = brand_name.replace(' Catalog', '').replace(' Brand', '').strip()
            safe_slug = brand_name_clean.lower().replace(" ", "-").replace(".", "").replace("&", "and")

            # --- MERGE: Halilit (commercial) with Brand Website Data (global) ---
            # Strategy: Price & SKU from Halilit, description & specs from brand website
            raw_data = self._merge_with_global_data(raw_data, safe_slug, catalog_file.stem)
            products = raw_data.get('products', [])

            # --- SAMPLING LOGIC (Hybrid: 100% Halilit, 20% Real) ---
            commercial_products = []
            real_products = []
            
            # Helper to detect Hebrew content (indicative of Halilit data)
            def has_hebrew(text):
                if not text: return False
                return any("\u0590" <= char <= "\u05FF" for char in text)

            for p in products:
                # Data Repair: Ensure pricing object exists (Fixes "0 price" issue)
                if not p.get('pricing'):
                    p['pricing'] = {}
                
                # Map flat 'price' to pricing object if missing
                if p.get('price') and not p['pricing'].get('regular_price'):
                     try:
                         val = float(p['price'])
                         if val > 0:
                             p['pricing']['regular_price'] = val
                             p['pricing']['original_price'] = val
                             logger.info(f"Fixed price for {p.get('name')}: {val}")
                     except Exception as e:
                         logger.warning(f"Failed to fix price for {p.get('name')}: {e}")

                # 1. Commercial Validity: Has Price OR Halilit ID/URL
                is_commercial_valid = (
                    p.get('halilit_url') is not None or 
                    p.get('halilit_id') is not None or
                    (p.get('pricing') and p['pricing'].get('regular_price') is not None)
                )
                
                # 2. Content Source: Hebrew = Halilit (Commercial Source)
                is_hebrew_content = has_hebrew(p.get('name', '')) or has_hebrew(p.get('description', ''))
                
                if is_hebrew_content:
                    # STRICT FILTER: User requested NO Hebrew data in UI.
                    # We skip these products entirely.
                    continue
                else:
                    # It is English/International. Treat as "Real" (Brand Source).
                    # (Even if it has a price, if it's English, we treat it as high-quality Real data).
                    # Actually, we should probably keep price if it has it, but put it in Real bucket?
                    # The user wants "Real" data displayed.
                    real_products.append(p)

            # Include 100% of all data (Real + Commercial)
            # Real: English/Brand website data (full specs, descriptions)
            # Commercial: Hebrew/Halilit data (pricing, availability, SKU)
            # Merge with intelligent deduplication
            real_count = len(real_products)
            commercial_count = len(commercial_products)
            
            # Build product ID set from real products to detect duplicates
            real_ids = {p.get('id', p.get('name', '').lower().replace(' ', '-')) for p in real_products}
            
            # Include only commercial products that aren't already in real products
            unique_commercial = []
            for p in commercial_products:
                prod_id = p.get('id', p.get('name', '').lower().replace(' ', '-'))
                if prod_id not in real_ids:
                    unique_commercial.append(p)
            
            # Merge: Real First (Good content), then Unique Commercial (Pricing/Inventory)
            merged_products = real_products + unique_commercial
            raw_data['products'] = merged_products
            product_count = len(merged_products)
            
            logger.info(f"      📊 [100% FULL DATA] {brand_name}: {commercial_count} Halilit + {real_count} Brand Website - {len(commercial_products) - len(unique_commercial)} duplicates = {product_count} Total")
            
            logger.info(f"      🔨 {brand_name:20s} ({product_count:3d} products) → {safe_slug}.json")
            
            # --- REFINEMENT LAYER ---
            # Ensure data quality: IDs, images, structure
            refined_data = self._refine_brand_data(raw_data, brand_name, safe_slug)
            
            # --- BUILD SEARCH GRAPH ---
            # Build search index for instant search
            self._index_for_search(refined_data, safe_slug)
            
            # --- WRITE BRAND FILE ---
            # This is lazy-loaded when user clicks the brand
            output_file = self.output_dir / f"{safe_slug}.json"
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(refined_data, out, indent=2, ensure_ascii=False)
            
            # --- UPDATE MASTER INDEX ---
            brand_identity = refined_data.get('brand_identity', {})
            brand_colors = brand_identity.get('brand_colors', {})
            
            with self.lock:
                self.master_index["brands"].append({
                    "id": safe_slug,
                    "name": brand_name,
                    "slug": safe_slug,
                    "count": product_count,
                    # Frontend expects:
                    "brand_color": brand_colors.get('primary'),
                    "logo_url": brand_identity.get('logo_url'),
                    "file": f"{safe_slug}.json",
                    "data_file": f"{safe_slug}.json",
                    "product_count": product_count,
                    "verified_count": product_count,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                })
                
                # --- UPDATE STATS ---
                self.stats["brands_processed"] += 1
                self.stats["products_total"] += product_count
            
        except json.JSONDecodeError as e:
            logger.error(f"      ❌ Invalid JSON in {catalog_file.name}: {e}")
            self.stats["errors"].append(f"JSON error in {catalog_file.name}")
        except Exception as e:
            logger.error(f"      ❌ Error processing {catalog_file.name}: {e}")
            self.stats["errors"].append(str(e))
    
    def _merge_with_global_data(self, commercial_data: Dict, slug: str, stem: str) -> Dict:
        """
        Merges Halilit data (commercial) with brand website data (global).
        
        Strategy:
        - Halilit is source for: price, SKU, halilit_id, halilit_url, availability
        - Brand website is source for: description, specs, category, images, logo
        - Product matching: fuzzy name matching (>0.6 similarity threshold)
        - Language handling: prefer English content from brand site over Hebrew from Halilit
        
        Args:
            commercial_data: Dict with products from Halilit blueprint
            slug: Brand slug (e.g., "cordoba-guitars")
            stem: Original filename stem (e.g., "cordoba-guitars_blueprint")
            
        Returns:
            Merged data dict with enhanced product information
        """
        if 'products' not in commercial_data:
            return commercial_data
        
        # Try to load global/brand website data if it exists
        global_data = []
        
        # Patterns to check for global/brand data files
        patterns = [
            f"data/blueprints/{slug}_brand.json",
            f"data/blueprints/{slug}-brand.json",
            f"data/blueprints/{stem}_brand.json",  # If stem is different
            f"data/blueprints/{stem}_commercial.json",  # Alternative source
            f"data/blueprints/{slug}_commercial.json",  # Alternative source
        ]
        
        for pattern in patterns:
            try:
                if Path(pattern).exists():
                    with open(pattern, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            global_data = data
                        elif isinstance(data, dict) and 'products' in data:
                            global_data = data['products']
                        logger.info(f"      📖 Loaded global data: {len(global_data)} products from {pattern}")
                        break
            except Exception as e:
                logger.debug(f"      ℹ️ Global data not found at {pattern}: {e}")
        
        if not global_data:
            logger.debug(f"      ℹ️ No brand website data found for {slug}, using Halilit-only")
            return commercial_data
        
        # Merge: Use fuzzy matching on product names
        from difflib import SequenceMatcher
        
        def has_hebrew(text):
            """Check if text contains Hebrew characters"""
            if not text:
                return False
            return any("\u0590" <= char <= "\u05FF" for char in text)
        
        merged_products = []
        matched_global_indices = set()
        
        for comm_idx, comm_item in enumerate(commercial_data.get('products', [])):
            final_item = comm_item.copy()
            
            # Find best match in global data (preferring products not yet matched)
            best_match = None
            best_score = 0.0
            best_match_idx = -1
            comm_name = comm_item.get('name', '').lower().strip()
            
            # Extract English part of name if Hebrew+English mixed
            if comm_name and has_hebrew(comm_name):
                # Try to extract English part
                english_part = ''.join(char for char in comm_name if ord(char) < 128)
                if english_part:
                    comm_name = english_part.lower().strip()
            
            if comm_name:
                for glob_idx, glob_item in enumerate(global_data):
                    # Skip if already matched to avoid duplicates
                    if glob_idx in matched_global_indices:
                        continue
                    
                    glob_name = glob_item.get('name', '').lower().strip()
                    if glob_name:
                        ratio = SequenceMatcher(None, comm_name, glob_name).ratio()
                        if ratio > best_score:
                            best_score = ratio
                            best_match = glob_item
                            best_match_idx = glob_idx
            
            # If we found a good match (>0.6 similarity), overlay global content
            if best_match and best_score > 0.6:
                matched_global_indices.add(best_match_idx)
                
                # PRIORITY 1: BRAND WEBSITE DATA (preferred for content)
                # PRIORITY 2: HALILIT DATA (for commerce)
                
                # === ENGLISH CONTENT (Brand Site Priority) ===
                
                # Name: Use brand site name if it's English and not Hebrew
                if best_match.get('name') and not has_hebrew(best_match.get('name', '')):
                    final_item['name'] = best_match['name']
                
                # Description: Always prefer brand site (usually English, detailed)
                brand_desc = best_match.get('description', '').strip()
                halilit_desc = final_item.get('description', '').strip()
                
                if brand_desc and (not halilit_desc or has_hebrew(halilit_desc) or len(brand_desc) > len(halilit_desc)):
                    final_item['description'] = brand_desc
                
                # Specs: Always prefer brand site
                if best_match.get('specs') and not final_item.get('specs'):
                    final_item['specs'] = best_match['specs']
                
                # SKU - If brand website has it and Halilit doesn't, use brand website's
                if best_match.get('sku') and not final_item.get('sku'):
                    final_item['sku'] = best_match['sku']
                
                # Category: Prefer brand site taxonomy (usually in English)
                brand_cat = best_match.get('category', '').lower()
                if best_match.get('category') and brand_cat not in ['general', 'other', 'uncategorized']:
                    if not final_item.get('category') or final_item.get('category').lower() in ['general', 'other', 'uncategorized']:
                        final_item['category'] = best_match['category']
                
                # Image: Always prefer brand site images (higher quality, no watermark)
                if best_match.get('image_url') and "placeholder" not in best_match.get('image_url', ''):
                    final_item['remote_image'] = best_match['image_url']
                
                # Model number
                if best_match.get('model_number') and not final_item.get('model_number'):
                    final_item['model_number'] = best_match['model_number']
            
            # === HALILIT DATA (Commerce - Always Kept) ===
            # These fields are preserved from Halilit (commerce data)
            # - halilit_id, halilit_url, price, pricing, status, is_sold, product_url
            
            # Ensure pricing structure is correct
            if not final_item.get('pricing'):
                final_item['pricing'] = {}
            
            # If we have a flat price field, move it to pricing object
            if final_item.get('price') and not final_item['pricing'].get('regular_price'):
                try:
                    price_val = float(final_item['price'])
                    if price_val > 0:
                        final_item['pricing']['regular_price'] = price_val
                        final_item['pricing']['original_price'] = price_val
                except (ValueError, TypeError):
                    pass
            
            merged_products.append(final_item)
        
        commercial_data['products'] = merged_products
        return commercial_data
    
    def _refine_brand_data(self, raw_data: Dict, brand_name: str, slug: str) -> Dict:
        """
        Refinement Layer: Ensure data quality AND build hierarchy
        - Ensure all products have IDs
        - Validate image structure
        - Add missing fields
        - Build hierarchical category structure (main → sub → products)
        - Enrich brand_identity with theme colors
        - Download brand logos locally
        """
        
        refined = raw_data.copy()
        refined['brand_name'] = brand_name
        refined['brand_slug'] = slug
        refined['refined_at'] = datetime.now(timezone.utc).isoformat()
        
        # Enrich brand_identity with theme colors and download logo
        if 'brand_identity' not in refined:
            refined['brand_identity'] = {}

        # Critical: Ensure ID and Name exist for Schema Validation
        if 'id' not in refined['brand_identity']:
            refined['brand_identity']['id'] = slug
        if 'name' not in refined['brand_identity']:
            refined['brand_identity']['name'] = brand_name
        
        # Always set brand_colors from BRAND_THEMES
        # Try exact match first, then base brand name (e.g., 'roland-comprehensive' -> 'roland')
        base_slug = slug.replace('-comprehensive', '').replace('-catalog', '')
        refined['brand_identity']['brand_colors'] = BRAND_THEMES.get(slug) or BRAND_THEMES.get(base_slug, {})
        
        # Inherit logo from base brand if missing
        if not refined['brand_identity'].get('logo_url'):
             # Standard fallback logos
             known_logos = {
                 'roland': 'https://static.roland.com/assets/images/logo_roland.svg',
                 'boss': 'https://www.boss.info/static/boss_logo.svg',
                 'nord': 'https://www.nordkeyboards.com/sites/default/files/files/nord-logo.svg',
                 'moog': 'https://www.moogmusic.com/sites/default/files/moog_logo.svg',
                 'yamaha': 'https://jp.yamaha.com/sp/common/images/yamaha_logo.png'
             }
             if base_slug in known_logos:
                 refined['brand_identity']['logo_url'] = known_logos[base_slug]

        # Download logo and update path
        # Always attempt resolution to catch local overrides (assets/logos/*.svg)
        current_logo_url = refined['brand_identity'].get('logo_url')
        resolved_logo = self._download_logo(current_logo_url, slug)
        if resolved_logo:
            refined['brand_identity']['logo_url'] = resolved_logo
        
        # First pass: Ensure product quality and TAXONOMY VALIDATION
        taxonomy_stats = {"validated": 0, "normalized": 0, "uncategorized": 0}
        
        if 'products' in refined:
            # Get brand logo URL for all products
            brand_logo_url = refined['brand_identity'].get('logo_url')
            
            for idx, product in enumerate(refined['products']):
                # Ensure ID
                if not product.get('id'):
                    product['id'] = f"{slug}-product-{idx}"

                # --- FIX: Ensure Brand Name is present (Required by Schema) ---
                if not product.get('brand'):
                    product['brand'] = brand_name
                
                # Add brand logo to every product (for TierBar and SpectrumModule rendering)
                if brand_logo_url and not product.get('logo_url'):
                    product['logo_url'] = brand_logo_url
                
                # --- NAMING STANDARDIZATION ---
                # Apply Title Case and Cleanup before any other processing
                original_name = product.get('name', '')
                standardized_name = self._enforce_naming_convention(original_name)
                if standardized_name != original_name:
                    # logger.info(f"      ✨ Renamed: {original_name} -> {standardized_name}")
                    product['name'] = standardized_name

                # --- DESCRIPTION CLEANUP ---
                # Remove Hebrew from description as well
                original_desc = product.get('description', '')
                if original_desc:
                    cleaned_desc = self._strip_hebrew(original_desc)
                    # Clean spaces
                    cleaned_desc = " ".join(cleaned_desc.split())
                    if cleaned_desc != original_desc:
                         product['description'] = cleaned_desc

                # --- TAXONOMY VALIDATION CHECKPOINT ---
                raw_category = product.get('main_category') or product.get('category')
                raw_subcategory = product.get('subcategory')
                
                # Normalize main category using taxonomy registry
                normalized_category = self.taxonomy_registry.normalize_category(slug, raw_category)
                
                if normalized_category:
                    product['main_category'] = normalized_category
                    product['category'] = normalized_category
                    taxonomy_stats["validated"] += 1
                elif raw_category:
                    # Category exists but not in taxonomy - keep but mark
                    product['main_category'] = raw_category
                    product['category'] = raw_category
                    product['_taxonomy_warning'] = f"Category '{raw_category}' not in official taxonomy"
                    taxonomy_stats["normalized"] += 1
                else:
                    product['main_category'] = 'Uncategorized'
                    product['category'] = 'Uncategorized'
                    taxonomy_stats["uncategorized"] += 1
                
                # Normalize subcategory if present
                if raw_subcategory:
                    normalized_sub = self.taxonomy_registry.normalize_category(slug, raw_subcategory)
                    if normalized_sub:
                        product['subcategory'] = normalized_sub

                # Ensure images are lists
                if 'images' in product and isinstance(product['images'], dict):
                    product['images'] = [product['images']]
                elif 'images' not in product:
                    product['images'] = []
                
                # Ensure category_hierarchy
                if 'category_hierarchy' not in product:
                    product['category_hierarchy'] = [product.get('category', 'Uncategorized')]
                    if product.get('subcategory'):
                        product['category_hierarchy'].append(product['subcategory'])
                
                # --- NEW: VISUAL FACTORY INTEGRATION ---
                # Process Main Image into Thumbnail + Inspection Asset
                main_img_url = product.get('image_url') or product.get('image')
                if not main_img_url and product.get('images') and len(product['images']) > 0:
                    first_img = product['images'][0]
                    main_img_url = first_img.get('url') if isinstance(first_img, dict) else first_img

                # Handle pre-seeded local paths (Mock Data)
                if main_img_url and main_img_url.startswith('/data/'):
                     product['images'] = {
                        "main": main_img_url,
                        "thumbnail": main_img_url,
                        "high_res": main_img_url.replace('_thumb', '_main'),
                        "original": main_img_url
                    }
                     logger.info(f"      ⏩ Skipping visuals for local seed path: {main_img_url}")

                elif main_img_url and not main_img_url.startswith('http://localhost'): # Skip if already local (unlikely in forge)
                    # Prepare Output Path
                    # frontend/public/data/product_images/<brand>/<product_id>
                    img_output_dir = self.output_dir / "product_images" / slug
                    img_output_dir.mkdir(parents=True, exist_ok=True)
                    
                    img_base_path = str(img_output_dir / f"{product['id']}")
                    
                    # Run Visual Factory (This is heavy, but yields "System Ready" assets)
                    logger.info(f"      🎨 Processing visuals for {product.get('name')}... Path: {img_base_path}")
                    
                    try:
                        visual_assets = self.visual_factory.process_product_asset(main_img_url, img_base_path)
                    
                        if visual_assets:
                            # Update product with new optimized local assets
                            # Convert absolute path to relative URL for frontend
                            # frontend/public/data/... -> /data/...
                            thumb_rel = f"/data/product_images/{slug}/{product['id']}_thumb.webp"
                            inspect_rel = f"/data/product_images/{slug}/{product['id']}_inspect.webp"
                            
                            # Transform srcset paths to relative URLs
                            srcset_rel = {}
                            if 'srcset' in visual_assets:
                                for key, path in visual_assets['srcset'].items():
                                    # path is absolute local path, extract filename
                                    filename = Path(path).name
                                    srcset_rel[key] = f"/data/product_images/{slug}/{filename}"

                            product['images'] = {
                                "main": thumb_rel,          # Used by TierBar and default view
                                "thumbnail": thumb_rel,     # Explicit thumbnail
                                "high_res": inspect_rel,    # Used by InspectionLens through 'main' or separate field
                                "original": main_img_url,   # Keep reference
                                "srcset": srcset_rel        # WebP SrcSet
                            }
                            
                            if 'dimensions' in visual_assets:
                                product['images']['dimensions'] = visual_assets['dimensions']

                            # Set primary image for legacy compatibility
                            product['image'] = thumb_rel
                            product['image_url'] = thumb_rel
                            
                            self.stats['images_verified'] += 1
                    except Exception as e:
                         logger.warning(f"      ⚠️ Visual Factory failed for {product.get('name')}: {e}")
                    
                    # Fallback to remote URL if no local processing
                    if main_img_url:
                        product['image'] = main_img_url
                        product['image_url'] = main_img_url

                # --- NEW: DOWNLOAD INNER LOGOS (series_logo) ---
                if product.get('series_logo'):
                    # Create a unique name: roland-fantom-06-series.png
                    logo_name = f"{slug}-{product.get('id', idx)}-series"
                    local_path = self._download_logo(product['series_logo'], logo_name)
                    product['series_logo'] = local_path
                    logger.info(f"      ⬇️  Downloaded inner logo for {product.get('name')}")
                
                # Data quality ensured - no unused AI layers
        
        # Log taxonomy validation stats
        logger.info(f"      📊 Taxonomy: {taxonomy_stats['validated']} validated, {taxonomy_stats['normalized']} normalized, {taxonomy_stats['uncategorized']} uncategorized")
        
        # Add taxonomy stats to brand_identity for frontend reference
        refined['brand_identity']['taxonomy_stats'] = taxonomy_stats
        
        # Add available categories from taxonomy registry for this brand
        brand_taxonomy = self.taxonomy_registry.get_brand(slug)
        if brand_taxonomy:
            refined['brand_identity']['categories'] = [
                {
                    "id": cat.id,
                    "label": cat.label,
                    "icon": cat.icon,
                    "description": cat.description,
                    "children": cat.children,
                }
                for cat in brand_taxonomy.get_root_categories()
            ]
        
        # Second pass: Build hierarchical category tree
        refined['hierarchy'] = self._build_category_hierarchy(refined.get('products', []))
        
        return refined
    
    def _build_category_hierarchy(self, products: List[Dict]) -> Dict:
        """
        Build a tree structure: Category → Subcategory → Products
        
        Structure:
        {
          "Electronics": {
            "Keyboards": [product1, product2],
            "Drums": [product3]
          },
          "Accessories": {
            "Cables": [product4]
          }
        }
        """
        hierarchy = {}
        
        for product in products:
            main_cat = product.get('main_category', 'Uncategorized')
            sub_cat = product.get('subcategory', 'General')
            
            # Ensure category exists
            if main_cat not in hierarchy:
                hierarchy[main_cat] = {}
            
            # Ensure subcategory exists
            if sub_cat not in hierarchy[main_cat]:
                hierarchy[main_cat][sub_cat] = []
            
            # Add product to subcategory (include full product data)
            hierarchy[main_cat][sub_cat].append({
                "id": product.get('id'),
                "name": product.get('name'),
                "description": product.get('short_description', product.get('description', '')),
                "images": product.get('images', []),
                "model_number": product.get('model_number'),
                "sku": product.get('sku')
            })
        
        return hierarchy
    
    def _index_for_search(self, brand_data: Dict, slug: str):
        """
        Build lightweight search graph entry for Halilit Catalog.
        This is what the navigator uses for instant suggestions.
        """
        
        brand_name = brand_data.get('brand_name', slug)
        
        for product in brand_data.get('products', []):
            entry = {
                "id": product.get('id'),
                "label": product.get('name', ''),
                "brand": slug,
                "brand_name": brand_name,
                "category": product.get('main_category', 'Uncategorized'),
                "subcategory": product.get('subcategory', 'General'),
                "keywords": product.get('features', [])[:5] if product.get('features') else [],
                "description": product.get('description', '')[:100] if product.get('description') else '',
                "image_url": product.get('image_url') or product.get('thumbnail_url')
            }
            self.master_index["search_graph"].append(entry)
    
    def _finalize_catalog(self):
        """Write the master index (The Spine of the Halilit Catalog)."""
        logger.info("   [3/4] Finalizing catalog structure...")
        
        # Update metadata
        self.master_index["total_brands"] = len(self.master_index["brands"])
        self.master_index["total_products"] = self.stats["products_total"]
        self.master_index["total_verified"] = self.stats["products_total"] # Assuming all generated items are verified
        
        # EXTRACT SEARCH GRAPH to separate file for scalability
        # We pop it from master_index so index.json remains lightweight
        search_graph = self.master_index.pop("search_graph")
        
        # Write search_index.json
        search_file = self.output_dir / "search_index.json"
        with open(search_file, 'w', encoding='utf-8') as f:
             json.dump(search_graph, f, indent=2, ensure_ascii=False)
        logger.info(f"      ✓ Search Index decoupled: {search_file.name} ({len(search_graph)} entries)")
        
        # Write index.json (The Master Catalog File)
        index_file = self.output_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.master_index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"      ✓ Master Catalog Index: {index_file.name}")
        logger.info(f"      ✓ {len(self.master_index['brands'])} brands")
        logger.info(f"      ✓ {self.master_index['total_products']} products")
        # logger.info(f"      ✓ {len(self.master_index['search_graph'])} search entries") # search_graph popped by previous step
    
    def _verify_output(self):
        """Run post-generation verification"""
        logger.info("   [4.5/5] Verifying catalog integrity...")
        verifier = CatalogVerifier(self.output_dir)
        report = verifier.verify()
        
        # Merge verifier stats into build stats
        self.stats["verification"] = report["stats"]
        if report["status"] == "FAIL":
            self.stats["errors"].append(f"Verification FAILED with {report['stats']['errors']} errors")
        
        # Log Top Issues
        for issue in report["issues"][:5]: # Show top 5
             logger.warning(f"      ⚠️  [{issue['level']}] {issue['context']}: {issue['message']}")
        
        if len(report['issues']) > 5:
             logger.warning(f"      ... and {len(report['issues']) - 5} more issues.")

    def _report(self):
        """Print final catalog build report."""
        logger.info("   [4/4] Catalog Build Report")
        logger.info(f"      📊 Brands Processed:   {self.stats['brands_processed']}")
        logger.info(f"      📊 Total Products:     {self.stats['products_total']}")
        # logger.info(f"      📊 Search Entries:     {len(self.master_index['search_graph'])}") # Moved to search_index.json
        
        if self.stats['errors']:
            logger.warning(f"      ⚠️  Errors Encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:3]:
                logger.warning(f"         - {error}")
        else:
            logger.info(f"      ✅ Zero Errors")
        
        logger.info("")
        logger.info("🎯 HALILIT CATALOG IS READY")
        logger.info(f"   Frontend can now fetch /data/index.json")
        logger.info(f"   Each brand lazy-loads from /data/<slug>.json")


if __name__ == "__main__":
    catalog = HalilitCatalog()
    success = catalog.build()
    exit(0 if success else 1)
