# backend/services/processors/roland_processor.py
from typing import Dict, Any, List
from models.product_hierarchy import (
    ProductCore, ProductSpecification, ProductImage, 
    SourceType, ProductStatus, ProductTier
)
import re

class RolandProcessor:
    def normalize(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms Raw Roland Data -> Standardized Product Blueprint
        """
        # 1. Basic Info
        model_name = raw_payload.get('model', 'Unknown')
        name = raw_payload.get('name', model_name)
        brand = raw_payload.get('brand', 'Roland')
        
        # 2. Specifications Normalization
        specs = []
        raw_specs = raw_payload.get('specifications', [])
        
        # Handle table-based specs (list of dicts with key/value)
        if isinstance(raw_specs, list):
            for item in raw_specs:
                key = item.get('key', '').strip()
                val = item.get('value', '').strip()
                if not key or not val:
                    continue
                
                # Determine category (Logic extracted from original Scraper)
                spec_category = "General"
                key_lower = key.lower()
                if any(word in key_lower for word in ['dimension', 'size', 'width', 'height', 'depth']):
                    spec_category = "Dimensions"
                elif any(word in key_lower for word in ['weight', 'mass']):
                    spec_category = "Weight"
                elif any(word in key_lower for word in ['power', 'voltage', 'current']):
                    spec_category = "Power"
                elif any(word in key_lower for word in ['audio', 'frequency', 'output', 'input', 'sound']):
                    spec_category = "Audio"
                elif any(word in key_lower for word in ['interface', 'connectivity', 'port', 'usb', 'midi']):
                    spec_category = "Connectivity"

                specs.append({
                    "key": key,
                    "value": val,
                    "category": spec_category, # This field might need to be added to Blueprint or handled
                    "source": "official"
                })
        
        # 3. Features Cleaning
        features = [f.strip() for f in raw_payload.get('features', []) if f and f.strip()]

        # 4. Images Normalization
        images = []
        raw_images = raw_payload.get('images', [])
        seen_urls = set()
        
        for img in raw_images:
            url = img.get('url')
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            images.append({
                "url": url,
                "type": img.get('type', 'main'),
                "alt_text": img.get('alt_text', '')
            })
            
        # 5. Construct Blueprint Dictionary
        # This matches the structure expected by GenesisBuilder or ProductCore.model_dump()
        blueprint = {
            "id": f"roland-{model_name.lower().replace(' ', '_')}",
            "brand": brand,
            "name": name,
            "sku": raw_payload.get('sku'),
            "main_category": raw_payload.get('hierarchy', {}).get('category', 'Unknown'),
            "subcategory": raw_payload.get('hierarchy', {}).get('subcategory'),
            "description": raw_payload.get('description', ''),
            "features": features,
            "specifications": specs,
            "images": images,
            "video_urls": raw_payload.get('videos', []),
            "manual_urls": raw_payload.get('manuals', []),
            "support_url": raw_payload.get('support_url'),
            "source": SourceType.BRAND_OFFICIAL.value,
            "status": ProductStatus.IN_STOCK.value, # Default
             # Preserve raw metadata
            "metadata": raw_payload.get('metadata', {})
        }

        return blueprint

