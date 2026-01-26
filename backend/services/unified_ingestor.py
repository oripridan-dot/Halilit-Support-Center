"""
Unified Ingestion Protocol - Split-Scrape Architecture

This module implements the "Unified Data Pipeline" that separates data sources:
1. Source A (Halilit): Commercial data (SKU, Price, Availability)
2. Source B (Brand Official): Knowledge & Media (Manuals, Images, Technical Specs)
3. Synthesis: Merge both into a single ProductBlueprint

Architecture:
Halilit (Commercial) + Official Brand Site (Knowledge/Media) → ProductBlueprint → Genesis Build → Frontend /public/data/
"""

import json
import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.category_consolidator import consolidate_category


# ============================================================================
# DATA MODELS - "OfficialMedia" Schema
# ============================================================================

class OfficialMedia(BaseModel):
    """
    Represents a single media asset from official brand sources.
    
    Fields:
    - url: Direct link to the asset (MUST be from official brand domain)
    - type: 'image', 'video', 'pdf', 'specification'
    - label: Human-readable label (e.g., "User Manual", "Quick Start Guide", "System Block Diagram")
    - source_domain: The official domain this was extracted from (e.g., "roland.com")
    - extracted_at: ISO timestamp when this asset was discovered
    """
    url: str
    type: str  # 'image', 'video', 'pdf', 'specification'
    label: str
    source_domain: str = ""
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://roland.com/assets/downloads/products/fantom/FantomOperatingManual.pdf",
                "type": "pdf",
                "label": "Operating Manual",
                "source_domain": "roland.com",
                "extracted_at": "2026-01-25T10:30:00"
            }
        }


class ProductBlueprint(BaseModel):
    """
    Unified product blueprint combining commercial and knowledge data.
    
    This is the atomic unit that flows through the pipeline:
    Halilit (SKU/Price) + Official Brand (Media/Specs) → ProductBlueprint → Frontend JSON
    
    Fields:
    - sku: Product Stock Keeping Unit (from Halilit)
    - brand: Brand name (e.g., "Roland", "Moog", "Nord")
    - model_name: Product model name/identifier
    - price: Retail price string (from Halilit)
    - availability: Stock availability status (from Halilit)
    - category: UI category ID after consolidation (keys, drums, guitars, etc.)
    - official_manuals: List of PDF/documentation assets from brand site
    - official_gallery: List of high-res image URLs from brand site
    - official_specs: Deep technical specifications from brand documentation
    - halilit_url: Source URL from Halilit for verification
    - description: Product description
    - id: Unique identifier in app
    """
    sku: str
    brand: str
    model_name: str
    price: str = ""
    availability: bool = True
    category: str = "general"
    official_manuals: List[OfficialMedia] = Field(default_factory=list)
    official_gallery: List[str] = Field(default_factory=list)
    official_specs: Dict = Field(default_factory=dict)
    halilit_url: str = ""
    description: str = ""
    id: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "sku": "ROLAND-FANTOM-06",
                "brand": "Roland",
                "model_name": "FANTOM-06",
                "price": "$1,499",
                "availability": True,
                "category": "keys",
                "official_manuals": [
                    {
                        "url": "https://roland.com/assets/downloads/fantom/manual.pdf",
                        "type": "pdf",
                        "label": "Operating Manual",
                        "source_domain": "roland.com"
                    }
                ],
                "official_gallery": [
                    "https://roland.com/assets/images/fantom/front-view.jpg",
                    "https://roland.com/assets/images/fantom/back-view.jpg"
                ],
                "official_specs": {
                    "polyphony": "128",
                    "sounds": "1000+"
                },
                "halilit_url": "https://halilit.com/products/roland-fantom-06",
                "description": "Professional synthesizer keyboard",
                "id": "roland_fantom_06"
            }
        }


# ============================================================================
# UNIFIED INGESTOR - The Main Pipeline Orchestrator
# ============================================================================

class MassIngestProtocol:
    """
    Main orchestrator for the unified data pipeline.
    
    Strategy:
    1. Fetch commercial data from Halilit (SKU, Price, Stock)
    2. For each item, map to Official Brand Scraper
    3. Pull Knowledge/Media from brand's official website ONLY
    4. Merge both sources into ProductBlueprint
    5. Save blueprints to vault for downstream processing
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the ingestor.
        
        Args:
            output_dir: Where to save ProductBlueprints (default: backend/data/vault/blueprints)
        """
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = output_dir or os.path.join(self.base_dir, "data", "vault", "blueprints")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.processed_count = 0
        self.error_count = 0
        self.blueprints: List[ProductBlueprint] = []
    
    def process_brand(self, brand_name: str, 
                     halilit_data: List[Dict],
                     official_scraper) -> List[ProductBlueprint]:
        """
        Process a complete brand using Split-Scrape logic.
        
        Args:
            brand_name: Brand identifier (e.g., "roland", "moog")
            halilit_data: Commercial data from Halilit (SKU, Price, Stock)
            official_scraper: Instance of OfficialBrandBase for this brand
            
        Returns:
            List of ProductBlueprint objects ready for Genesis Build
        """
        print(f"\n🔄 Processing brand: {brand_name}")
        print(f"   📊 Halilit items: {len(halilit_data)}")
        
        blueprints = []
        
        for idx, item in enumerate(halilit_data, 1):
            try:
                # Step 1: Start with commercial data
                sku = item.get('sku', '')
                model_name = item.get('model_name', item.get('name', ''))
                
                # Step 2: Fetch knowledge/media from official brand scraper
                official_data = official_scraper.scrape_product(model_name, sku)
                
                # Step 3: Merge into blueprint
                blueprint = self._merge_sources(
                    commercial_item=item,
                    official_data=official_data,
                    brand_name=brand_name
                )
                
                blueprints.append(blueprint)
                self.processed_count += 1
                
                if idx % 10 == 0:
                    print(f"   ✓ {idx}/{len(halilit_data)} blueprints created")
                    
            except Exception as e:
                print(f"   ⚠️  Error processing {item.get('name', 'Unknown')}: {str(e)}")
                self.error_count += 1
                continue
        
        # Save all blueprints for this brand
        self._save_brand_blueprints(brand_name, blueprints)
        self.blueprints.extend(blueprints)
        
        print(f"✨ Brand {brand_name} processed: {len(blueprints)} blueprints")
        return blueprints
    
    def _merge_sources(self, commercial_item: Dict, official_data: Dict, 
                      brand_name: str) -> ProductBlueprint:
        """
        Merge Halilit (commercial) and Official Brand (knowledge) data.
        
        Merge Strategy:
        - Halilit is AUTHORITATIVE for: SKU, Price, Availability
        - Official Brand is AUTHORITATIVE for: Manuals, Images, Specs
        - Consolidate category using categoryConsolidator
        """
        model_name = commercial_item.get('name', commercial_item.get('model_name', 'Unknown'))
        
        # Extract media from official data
        official_manuals = [
            OfficialMedia(
                url=doc['url'],
                type=doc.get('type', 'pdf'),
                label=doc.get('label', 'Documentation'),
                source_domain=doc.get('source_domain', '')
            )
            for doc in official_data.get('manuals', [])
        ]
        
        official_gallery = official_data.get('gallery', [])
        official_specs = official_data.get('specs', {})
        
        # Consolidate category from brand taxonomy to UI taxonomy
        raw_category = commercial_item.get('category', 'general')
        consolidated_category = consolidate_category(brand_name.lower(), raw_category)
        
        # Generate unique ID
        product_id = f"{brand_name.lower()}_{model_name.lower().replace(' ', '_')}"
        
        # Create blueprint
        blueprint = ProductBlueprint(
            sku=commercial_item.get('sku', ''),
            brand=brand_name,
            model_name=model_name,
            price=commercial_item.get('price', ''),
            availability=commercial_item.get('in_stock', True),
            category=consolidated_category,
            official_manuals=official_manuals,
            official_gallery=official_gallery,
            official_specs=official_specs,
            halilit_url=commercial_item.get('url', ''),
            description=commercial_item.get('description', ''),
            id=product_id
        )
        
        return blueprint
    
    def _save_brand_blueprints(self, brand_name: str, blueprints: List[ProductBlueprint]):
        """
        Save blueprints to disk as JSON for downstream processing.
        
        Output: backend/data/vault/blueprints/{brand_name}_blueprints.json
        """
        output_file = os.path.join(self.output_dir, f"{brand_name.lower()}_blueprints.json")
        
        blueprints_dict = [bp.model_dump() for bp in blueprints]
        
        with open(output_file, 'w') as f:
            json.dump(blueprints_dict, f, indent=2, default=str)
        
        print(f"   💾 Saved to: {output_file}")
    
    def validate_blueprints(self) -> Tuple[int, int]:
        """
        Validate all blueprints before passing to GenesisBuilder.
        
        Validation Rules:
        1. Every blueprint must have SKU and model_name
        2. Every blueprint should have at least 1 official manual (if available)
        3. Price should not be empty
        4. Category must be one of the 8 consolidated categories
        
        Returns:
            (valid_count, invalid_count)
        """
        valid_count = 0
        invalid_count = 0
        
        for bp in self.blueprints:
            is_valid = True
            
            if not bp.sku or not bp.model_name:
                print(f"   ❌ Missing SKU or model_name: {bp.model_name}")
                is_valid = False
            
            if not bp.price:
                print(f"   ⚠️  Missing price for: {bp.model_name}")
                # Not critical, but log it
            
            if not bp.official_manuals and not bp.official_gallery:
                print(f"   ⚠️  No official media for: {bp.model_name}")
                # Warn but not fail
            
            if bp.category not in ["keys", "drums", "guitars", "studio", "live", "dj", "software", "accessories"]:
                print(f"   ❌ Invalid category '{bp.category}' for {bp.model_name}")
                is_valid = False
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        print(f"\n✅ Validation: {valid_count} valid, {invalid_count} invalid")
        return valid_count, invalid_count
    
    def export_for_genesis(self, output_file: str = None) -> str:
        """
        Export all blueprints as a single JSON for GenesisBuilder consumption.
        
        Output: backend/data/vault/unified_blueprints.json
        """
        if not output_file:
            output_file = os.path.join(self.base_dir, "data", "vault", "unified_blueprints.json")
        
        blueprints_dict = [bp.model_dump() for bp in self.blueprints]
        
        with open(output_file, 'w') as f:
            json.dump(blueprints_dict, f, indent=2, default=str)
        
        print(f"\n📦 Exported {len(blueprints_dict)} blueprints to: {output_file}")
        return output_file


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_blueprints_from_disk(file_path: str) -> List[ProductBlueprint]:
    """
    Load previously saved blueprints from JSON.
    
    Used by GenesisBuilder to consume unified pipeline output.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    blueprints = [ProductBlueprint(**item) for item in data]
    return blueprints


def blueprint_to_product_dict(blueprint: ProductBlueprint) -> Dict:
    """
    Convert ProductBlueprint to product JSON format for frontend.
    
    This is used by GenesisBuilder to create the final JSON files.
    Includes the new 'official_manuals' array for the MediaBar UI.
    """
    return {
        "id": blueprint.id,
        "sku": blueprint.sku,
        "name": blueprint.model_name,
        "brand": blueprint.brand,
        "category": blueprint.category,
        "description": blueprint.description,
        "price": blueprint.price,
        "in_stock": blueprint.availability,
        "official_manuals": [
            {
                "url": manual.url,
                "type": manual.type,
                "label": manual.label,
                "source_domain": manual.source_domain
            }
            for manual in blueprint.official_manuals
        ],
        "official_gallery": blueprint.official_gallery,
        "specs": blueprint.official_specs,
        "source_url": blueprint.halilit_url
    }


if __name__ == "__main__":
    print("Unified Ingestion Protocol - v1.0")
    print("Status: Core modules loaded. Use in conjunction with scrapers and GenesisBuilder.")
