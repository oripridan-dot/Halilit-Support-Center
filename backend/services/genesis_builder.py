# backend/services/genesis_builder.py
"""
Genesis Builder - The App Constructor

Reads "blueprint" JSON files created by SuperExplorer and constructs
the complete app file structure:
  - Product JSON files in frontend/public/data
  - Thumbnail images in frontend/public/data/images
  - Updated index.json with all products

The resulting "Skeleton" app is fully browseable with all products visible,
waiting for heavy scrapers to fill in detailed specs in the background.
"""

import json
import os
import requests
import shutil
from typing import Dict, List, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.category_consolidator import consolidate_category
except ImportError:
    # Fallback if imports fail (e.g. running script directly)
    def consolidate_category(brand, cat): return "general"

try:
    from services.relationship_engine import ProductRelationshipEngine
except ImportError:
    ProductRelationshipEngine = None

class GenesisBuilder:

    """
    Constructs the app structure from blueprint JSON files.
    
    Manages product files, images, and the master index.
    """
    
    # Relative paths from backend directory
    # FRONTEND_DATA = "../frontend/public/data"
    # FRONTEND_IMAGES = "../frontend/public/data/images"
    
    # Use absolute paths based on file location to be safe
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # hsc-jit-v3/backend
    
    # OUTPUT DESTINATION: Data Vault (Intermediate Storage)
    # We scrape to Vault, then Forge Backbone refines it to Frontend
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "vault", "catalogs_brand")
    
    # LEGACY / REFERENCE:
    # FRONTEND_DATA = os.path.join(os.path.dirname(BASE_DIR), "frontend/public/data")
    # FRONTEND_IMAGES = os.path.join(os.path.dirname(BASE_DIR), "frontend/public/data/images")

    def __init__(self, brand_key: str):
        """
        Initialize builder for a specific brand.
        
        Args:
            brand_key: Brand identifier (e.g., "roland")
        """
        self.brand = brand_key
        self.blueprint_file = f"backend/data/blueprints/{brand_key}_blueprint.json"
        self.products_built = []

    def construct(self) -> bool:
        """
        Read blueprints (Global + Commercial) and construct app structure.
        Merges Halilit commercial data with Brand global content.
        
        Returns:
            True if successful, False otherwise
        """
        # 1. Load Data Sources
        global_path = f"backend/data/blueprints/{self.brand}_blueprint.json"
        commercial_path = f"backend/data/blueprints/{self.brand}_commercial.json"
        
        global_data = []
        if os.path.exists(global_path):
            try:
                with open(global_path, 'r') as f:
                    global_data = json.load(f)
            except Exception as e:
                print(f"   ⚠️ Bad Global Blueprint: {e}")

        commercial_data = []
        if os.path.exists(commercial_path):
            try:
                 with open(commercial_path, 'r') as f:
                    commercial_data = json.load(f)
            except Exception as e:
                print(f"   ⚠️ Bad Commercial Blueprint: {e}")

        if not global_data and not commercial_data:
            print(f"⚠️  No data found for {self.brand} (checked both sources)")
            return False

        print(f"🏗️  Initiating Genesis for {self.brand.upper()}...")
        print(f"   Sources: Global={len(global_data)}, Commercial={len(commercial_data)}")

        # 2. Merge Logic (The "Split Source" Implementation)
        blueprint = self._merge_catalogs(commercial_data, global_data)
        
        print(f"   Processing {len(blueprint)} merged products...")
        
        for idx, item in enumerate(blueprint, 1):
            success = self._build_node(item)
            if success:
                self.products_built.append(item['id'])
            
            if idx % 10 == 0:
                print(f"   └─ {idx}/{len(blueprint)} products constructed")
        
        # 3. Discover Product Relationships (Optional)
        # If we have the relationship engine, analyze all products for connections
        if ProductRelationshipEngine and len(blueprint) > 5:
            print(f"   🔗 Analyzing product relationships...")
            try:
                engine = ProductRelationshipEngine()
                blueprint = list(engine.analyze_all_blueprints(blueprint).values())
                print(f"   ✅ Relationship analysis complete")
            except Exception as e:
                print(f"   ⚠️ Relationship analysis skipped: {e}")
            
        self._update_catalog_index(blueprint)
        print(f"✨ Genesis Complete for {self.brand}: {len(self.products_built)} products.")
        return True

    def _merge_catalogs(self, commercial: List[Dict], global_data: List[Dict]) -> List[Dict]:
        """
        Merges the Commercial Catalog (Halilit) with the Global Catalog (Brand).
        
        IMPLEMENTS 'CHURCH AND STATE' SEPARATION:
        - official_knowledge: Strictly from Manufacturer (Global)
        - commercial_offer: Strictly from Retailer (Commercial)
        """
        merged = []
        from difflib import SequenceMatcher
        
        print("   🔄 Merging Commercial & Global data (Twin-Pipe Strategy)...")
        
        # Determine Master List
        # If commercial data exists, it drives the product list (Sales-Driven).
        # If not, we fall back to Global data (Catalog-Driven) for preview/dev.
        master_list = commercial if commercial else global_data
        is_sale_driven = bool(commercial)

        for item in master_list:
            
            # 1. Establish Commercial Identity & Offer
            if is_sale_driven:
                comm_item = item
                product_id = comm_item.get('id', comm_item.get('sku'))
                commercial_offer = {
                    "price": comm_item.get('price'),
                    "in_stock": comm_item.get('in_stock', False),
                    "sku": comm_item.get('sku'),
                    "buy_url": comm_item.get('url'),
                    "status": comm_item.get('status', 'scratch') # status tracking
                }
                match_target_name = comm_item.get('name', '').lower()
            else:
                # No commercial data
                product_id = item.get('id', item.get('sku'))
                commercial_offer = {}
                match_target_name = item.get('name', '').lower()

            # 2. Retrieve Official Knowledge (The "Vault")
            official_knowledge = {}
            
            if not is_sale_driven:
                # If we are iterating global items, the item IS the official knowledge
                official_knowledge = item
            else:
                # We need to find the matching global item
                best_match = None
                best_score = 0.0
                
                for glob_item in global_data:
                    glob_name = glob_item.get('name', '').lower()
                    if match_target_name and glob_name:
                         ratio = SequenceMatcher(None, match_target_name, glob_name).ratio()
                         if ratio > 0.6 and ratio > best_score:
                             best_score = ratio
                             best_match = glob_item
                
                if best_match:
                    official_knowledge = best_match

            # 3. Construct "Church and State" Object
            final_item = {
                "id": product_id,
                "official_knowledge": official_knowledge,
                "commercial_offer": commercial_offer
            }
            
            merged.append(final_item)
            
        return merged

    def _update_catalog_index(self, blueprint: List[Dict]):
        """
        Update the brand catalog file (e.g. roland.json) with new image URLs.
        Preserves existing brand identity if file exists.
        """
        # Ensure Vault directory exists
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
            
        catalog_path = os.path.join(self.OUTPUT_DIR, f"{self.brand}.json")
        catalog_data = {}
        
        if os.path.exists(catalog_path):
            try:
                with open(catalog_path, 'r') as f:
                    catalog_data = json.load(f)
            except:
                pass
        
        if "brand_identity" not in catalog_data:
            catalog_data["brand_identity"] = {
                "id": self.brand,
                "name": self.brand.upper()
            }
            
        # Rebuild Products List
        new_products = []
        for item in blueprint:
            safe_id = item['id']
            
            # ACCESS DATA STREAMS
            official = item.get('official_knowledge', {}) or {}
            commercial = item.get('commercial_offer', {}) or {}
            
            # 1. Resolve Image URL (STRICT: Official Only)
            # We explicitly reject commercial images here.
            public_url = "/assets/placeholder_gear.png"
            
            if official.get('image_url') and "placeholder" not in official['image_url']:
                public_url = official['image_url']
            elif official.get('remote_image'):
                 public_url = official['remote_image']
                
            # 2. Resolve Name (Prefer Official)
            product_name = official.get('name') or commercial.get('name') or "Unknown Model"

            # 3. Smart Categorization
            raw_cat = official.get('category', 'general')
            final_cat = self._smart_categorize(product_name, raw_cat)
            
            product_entry = {
                "id": safe_id,
                "name": product_name,
                "brand": self.brand,
                "category": final_cat,
                "image_url": public_url,
                "description": official.get('description', ''),
                
                # Extended Commerce Data (Halilit Integration)
                "pricing": {"price": commercial.get('price')},
                "stock_status": commercial.get('in_stock'),
                "sku": commercial.get('sku'),
                "halilit_url": commercial.get('buy_url'),
                
                # Official Media Assets (From brand official sites)
                "official_manuals": official.get('official_manuals', []),
                "official_gallery": official.get('official_gallery', []),
            }
            
            new_products.append(product_entry)
            
        catalog_data["products"] = new_products
        
        with open(catalog_path, 'w') as f:
            json.dump(catalog_data, f, indent=2)

    def _build_node(self, item: Dict) -> bool:
        """
        Construct a single product's file structure and assets.
        
        Args:
            item: Product dict from blueprint (Church & State Structured)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Prepare Paths
            safe_id = item['id']
            product_folder = os.path.join(self.OUTPUT_DIR, self.brand)
            image_folder = os.path.join(self.OUTPUT_DIR, "images", self.brand)
            
            os.makedirs(product_folder, exist_ok=True)
            os.makedirs(image_folder, exist_ok=True)

            # Unpack Streams
            official = item.get('official_knowledge', {}) or {}
            commercial = item.get('commercial_offer', {}) or {}

            # 2. Acquire Asset (Download Thumbnail)
            # STRICT RULE: Only Official Images
            local_image_name = f"{safe_id}_thumb.jpg"
            local_image_full_path = os.path.join(image_folder, local_image_name)
            
            public_url = "/assets/placeholder_gear.png"
            if official.get('image_url') and "placeholder" not in official['image_url']:
                 public_url = official['image_url']
            elif official.get('remote_image'):
                 public_url = official['remote_image']

            # 3. Construct JSON State
            
            # Determine Badge
            badges = []
            if commercial.get('buy_url'):
                badges.append("HALILIT_CERTIFIED")
            else:
                badges.append("GLOBAL_CATALOG")

            description = official.get('description') or official.get('short_description') or ''
            product_name = official.get('name') or commercial.get('name') or "Unknown"
            
            # Smart Categorization
            raw_cat = official.get('category', 'general')
            final_cat = self._smart_categorize(product_name, raw_cat)

            product_data = {
                "id": safe_id,
                "name": product_name,
                "brand": self.brand,
                "category": final_cat,
                "description": description,
                "media": {
                    "thumbnail": public_url,
                    "gallery": official.get('official_gallery', []),
                    "videos": []
                },
                "commercial": {
                    "price": commercial.get('price'),
                    "link": commercial.get('buy_url'),
                    "status": commercial.get('status', 'unknown')
                },
                "official_knowledge": official, # Persist the Vault data
                "specs": official.get('specs', {}),
                "official_manuals": official.get('official_manuals', []),
                "official_specs": official.get('official_specs', {}),
                
                "badges": badges,
                "meta": {
                    "completeness": "SKELETON",
                    "last_scan": self._get_timestamp()
                }
            }

            # 4. Write to Disk
            product_file_path = os.path.join(product_folder, f"{safe_id}.json")
            with open(product_file_path, 'w') as f:
                json.dump(product_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  Failed to build {item.get('id', 'unknown')}: {e}")
            return False

    def _download_image(self, url: str, save_path: str) -> bool:
        """
        Download an image from URL and save locally.
        
        Args:
            url: Image URL
            save_path: Local file path to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(url, timeout=5, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception:
            pass
        return False

    def _smart_categorize(self, name: str, current_cat: str) -> str:
        """
        Determines the best UI category ID.
        1. Tries to consolidate existing category.
        2. If 'general', uses heuristics on Product Name.
        """
        # 1. Try strict consolidation first
        if current_cat and current_cat.lower() != 'general':
            consolidated = consolidate_category(self.brand, current_cat)
            if consolidated != 'general':
                return consolidated

        # 2. Heuristic fallback (Keyword Matching)
        name_lower = name.lower()
        
        # KEYWORDS MAPPING (Simple & Effective)
        keywords = {
            'keys': ['piano', 'synth', 'key', 'organ', 'mellotron', 'grand', 'upright', 'clavinova', 'keyboard', 'eurorack', 'modular', 'moog', 'nord', 'roland fantom', 'juno'],
            'drums': ['drum', 'cymbal', 'snare', 'kick', 'hi-hat', 'percussion', 'cajon', 'pad', 'vdrum', 'v-drum', 'td-', 'head'],
            'guitars': ['guitar', 'bass', 'strat', 'tele', 'les paul', 'pedal', 'amp', 'cabinet', 'fender', 'gibson', 'ibanez', 'boss', 'stompbox', 'multi-effect'],
            'studio': ['interface', 'monitor', 'speak', 'mic', 'preamp', 'audio', 'scarlett', 'apollo', 'neumann', 'shure', 'recording', 'isolator'],
            'live': ['mixer', 'pa system', 'wireless', 'loudspeaker', 'column', 'stage', 'allen'],
            'dj': ['controller', 'dj', 'sampler', 'turntable', 'numark', 'denon', 'serato', 'traktor', 'mpc', 'push', 'maschine'],
            'accessories': ['stand', 'case', 'cable', 'cover', 'bench', 'pedalboard', 'strap', 'pick', 'string', 'adapter', 'mount']
        }

        # Priority Check (Longer keywords first to avoid 'amp' matching 'sample')
        for cat_id, terms in keywords.items():
            for term in terms:
                if term in name_lower:
                    return cat_id

        # 3. Brand Specific Defaults
        if self.brand in ['roland', 'nord', 'moog', 'yamaha', 'korg', 'casio', 'asm', 'oberheim', 'sequential']:
            return 'keys'
                 
        if self.brand in ['pearl', 'dw', 'tama', 'mapex', 'paiste', 'zildjian', 'sabian', 'vic firth', 'remo', 'sonor', 'gretsch drums']:
            return 'drums'
            
        if self.brand in ['fender', 'gibson', 'ibanez', 'epiphone', 'esp', 'jackson', 'taylor', 'martin', 'prs', 'schecter', 'charvel', 'kramer', 'washburn', 'cort', 'godin', 'hagstrom', 'guild', 'gretsch guitars', 'supro', 'danelectro', 'rickenbacker', 'music man', 'g&l', 'squier', 'stagg', 'tokai', 'univox', 'aria', 'fernandes', 'hofner', 'jay turser', 'kay', 'mosrite', 'ovation', 'parker', 'peavey', 'samick', 'silvertone', 'teisco', 'vox', 'yamaha guitars']:
            return 'guitars'

        # Default fallback
        return 'general'

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def construct_all_brands(self) -> Dict[str, bool]:
        """
        Construct all brand catalogs.
        
        Returns:
            Dict mapping brand names to success status
        """
        blueprints_dir = "backend/data/blueprints"
        
        if not os.path.exists(blueprints_dir):
            print(f"⚠️  Blueprints directory not found: {blueprints_dir}")
            return {}
        
        blueprint_files = [f for f in os.listdir(blueprints_dir) if f.endswith('_blueprint.json')]
        results = {}
        
        print(f"🌍 Constructing Genesis for {len(blueprint_files)} brands...\n")
        
        for blueprint_file in blueprint_files:
            brand_key = blueprint_file.replace('_blueprint.json', '')
            builder = GenesisBuilder(brand_key)
            success = builder.construct()
            results[brand_key] = success
            print()
        
        return results


if __name__ == "__main__":
    # Example: Build a single brand
    # builder = GenesisBuilder("roland")
    # builder.construct()
    
    # Or build all brands
    builder = GenesisBuilder("")  # Dummy instance
    results = builder.construct_all_brands()
    
    print(f"\n📊 Genesis Summary:")
    for brand, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {brand}")
