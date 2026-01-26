# backend/services/local_blueprint_loader.py
"""
Local Blueprint Loader - Convert existing catalog data to blueprints.

Instead of scraping live websites, this loads your pre-existing product
catalogs from data/catalogs_brand/ and converts them to blueprint format
that GenesisBuilder can consume.

This is much faster and reliable since your data is already rich and validated.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class LocalBlueprintLoader:
    """
    Converts existing catalog JSON files to blueprint format.
    """
    
    def __init__(self):
        # Use absolute path to parent directory's catalogs
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.catalogs_dir = os.path.join(backend_dir, "..", "data", "catalogs_brand")
        os.makedirs("backend/data/blueprints", exist_ok=True)

    def load_catalog(self, brand_key: str) -> Optional[Dict]:
        """
        Load a catalog JSON file.
        
        Args:
            brand_key: Brand identifier (e.g., "roland")
            
        Returns:
            Catalog dict or None if not found
        """
        catalog_path = os.path.join(self.catalogs_dir, f"{brand_key}.json")
        
        if not os.path.exists(catalog_path):
            print(f"⚠️  Catalog not found: {catalog_path}")
            return None
        
        try:
            with open(catalog_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {catalog_path}: {e}")
            return None

    def convert_to_blueprint(self, brand_key: str) -> Optional[str]:
        """
        Convert catalog to blueprint format.
        
        Args:
            brand_key: Brand identifier
            
        Returns:
            Path to blueprint file, or None on failure
        """
        catalog = self.load_catalog(brand_key)
        if not catalog:
            return None
        
        print(f"📦 Converting {brand_key.upper()} catalog to blueprint...")
        
        products = catalog.get("products", [])
        blueprint = []
        
        for product in products:
            blueprint_item = {
                "id": product.get("id", "").lower(),
                "brand": brand_key,
                "name": product.get("name", "").strip(),
                "category": product.get("main_category", "General"),
                "short_description": product.get("short_description", ""),
                "remote_image": self._extract_image_url(product),
                "intelligence": self._extract_intelligence(product)
            }
            
            if blueprint_item["id"] and blueprint_item["name"]:
                blueprint.append(blueprint_item)
        
        # Save blueprint
        output_path = f"backend/data/blueprints/{brand_key}_blueprint.json"
        with open(output_path, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        print(f"   ✅ Converted {len(blueprint)} products")
        print(f"   📄 Saved to: {output_path}")
        
        return output_path

    def _extract_image_url(self, product: Dict) -> str:
        """
        Extract the main image URL from product data.
        
        Args:
            product: Product dict
            
        Returns:
            Image URL or empty string
        """
        # Try images array first
        images = product.get("images", [])
        if images:
            # Handle list of strings (blueprint format)
            if isinstance(images[0], str):
                return images[0]
            
            # Handle list of objects (catalog format)
            # Prefer main image, fall back to first image
            for img in images:
                if isinstance(img, dict) and img.get("type") == "main":
                    return img.get("url", "")
            
            # Fallback to first image object
            if isinstance(images[0], dict):
                return images[0].get("url", "")
        
        # Fallback to direct image field
        return product.get("image", "") or product.get("image_url", "")

    def _extract_intelligence(self, product: Dict) -> Dict:
        """
        Extract Halilit intelligence from product.
        
        Args:
            product: Product dict
            
        Returns:
            Intelligence dict
        """
        # Check if product has Halilit pricing
        price = product.get("price", 0)
        link = product.get("link", None)
        
        # If we have price and link, mark as Halilit sold
        is_sold = bool(price and price > 0)
        
        return {
            "is_sold": is_sold,
            "price": price if isinstance(price, (int, float)) else 0,
            "url": link,
            "status": "IN_STOCK" if is_sold else "NOT_SOLD"
        }

    def convert_all(self) -> Dict[str, str]:
        """
        Convert all available catalogs to blueprints.
        
        Returns:
            Dict mapping brand names to blueprint paths
        """
        results = {}
        
        if not os.path.exists(self.catalogs_dir):
            print(f"⚠️  Catalogs directory not found: {self.catalogs_dir}")
            return results
        
        # Find all catalog files
        catalog_files = [
            f.replace(".json", "") 
            for f in os.listdir(self.catalogs_dir) 
            if f.endswith(".json")
        ]
        
        print(f"🔄 Converting {len(catalog_files)} brand catalogs to blueprints...\n")
        
        for brand_key in sorted(catalog_files):
            blueprint_path = self.convert_to_blueprint(brand_key)
            if blueprint_path:
                results[brand_key] = blueprint_path
            print()
        
        return results


if __name__ == "__main__":
    loader = LocalBlueprintLoader()
    results = loader.convert_all()
    
    print(f"\n📊 Conversion Summary:")
    for brand, path in results.items():
        print(f"   ✓ {brand}: {path}")
