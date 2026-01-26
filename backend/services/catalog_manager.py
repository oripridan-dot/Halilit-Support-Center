import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from models.product_hierarchy import ProductCore, ProductCatalog

logger = logging.getLogger(__name__)

class MasterCatalogManager:
    """
    Manages the lifecycle of Brand Master Files.
    Ensures scraping is ADDITIVE (Update/Merge) rather than destructive.
    """
    
    def __init__(self, brand_id: str):
        self.brand_id = brand_id.lower()
        self.file_path = Path(f"backend/data/vault/catalogs_brand/{self.brand_id}.json")
        self.backup_path = Path(f"backend/data/vault/catalogs_brand/backups/{self.brand_id}_{datetime.now().strftime('%Y%m%d')}.json")
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)

    def load_master(self) -> ProductCatalog:
        """Loads the existing master file or returns a skeleton if none exists."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle legacy/schema variations here if needed
                    return ProductCatalog(**data)
            except Exception as e:
                logger.error(f"⚠️ Corrupt Master File for {self.brand_id}: {e}")
        
        # Return empty skeleton
        return ProductCatalog(
            brand_identity={"id": self.brand_id, "name": self.brand_id.title()},
            products=[],
            total_products=0,
            last_updated=datetime.utcnow()
        )

    def merge_and_save(self, new_products: List[ProductCore]):
        """
        Smart Merge:
        1. Loads existing Master.
        2. Updates existing products (by ID) with fresh data.
        3. Adds new products.
        4. Preserves 'frozen' or 'manual' fields if we add that flag later.
        """
        current_catalog = self.load_master()
        
        # Create a lookup map of existing products
        product_map = {p.id: p for p in current_catalog.products}
        new_count = 0
        update_count = 0

        for new_p in new_products:
            if new_p.id in product_map:
                # UPDATE: Merge logic goes here
                # For now, we trust the fresh scrape, BUT we could preserve specific fields
                # like 'manual_tags' or 'custom_images' if they existed in 'existing_p'
                existing_p = product_map[new_p.id]
                
                # Example: Preserve pre-calculated visual assets if new ones aren't provided
                if not new_p.images and existing_p.images:
                    new_p.images = existing_p.images
                
                product_map[new_p.id] = new_p
                update_count += 1
            else:
                # INSERT
                product_map[new_p.id] = new_p
                new_count += 1

        # Reconstruct List
        merged_products = list(product_map.values())
        
        # Update Metadata
        current_catalog.products = merged_products
        current_catalog.total_products = len(merged_products)
        current_catalog.last_updated = datetime.utcnow()
        
        # Save Backup first
        if self.file_path.exists():
            import shutil
            shutil.copy(self.file_path, self.backup_path)

        # Write Master
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(current_catalog.model_dump(mode='json'), f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Master File Saved: {self.brand_id}")
        logger.info(f"   ➕ Added: {new_count} | 🔄 Updated: {update_count} | 📦 Total: {len(merged_products)}")
