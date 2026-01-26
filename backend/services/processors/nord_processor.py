# backend/services/processors/nord_processor.py
from typing import Dict, Any, List
from models.product_hierarchy import (
    ProductCore, ProductSpecification, ProductImage, 
    SourceType, ProductStatus, ProductTier
)

class NordProcessor:
    def normalize(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms Raw Nord Data -> Standardized Product Blueprint
        """
        model_name = raw_payload.get('model', 'Unknown')
        name = raw_payload.get('name', model_name)
        brand = raw_payload.get('brand', 'Nord')
        
        specs = []
        raw_specs = raw_payload.get('specifications', [])
        
        if isinstance(raw_specs, list):
            for item in raw_specs:
                key = item.get('key', '').strip()
                val = item.get('value', '').strip()
                if not key or not val: continue
                
                spec_category = "General"
                # TODO: Add Nord-specific spec categorization logic
                
                specs.append({
                    "key": key,
                    "value": val,
                    "category": spec_category,
                    "source": "official"
                })
        
        features = [f.strip() for f in raw_payload.get('features', []) if f and f.strip()]

        images = []
        raw_images = raw_payload.get('images', [])
        seen_urls = set()
        for img in raw_images:
            url = img.get('url')
            if not url or url in seen_urls: continue
            seen_urls.add(url)
            images.append({
                "url": url,
                "type": img.get('type', 'main'),
                "alt_text": img.get('alt_text', '')
            })
            
        blueprint = {
            "id": f"nord-{model_name.lower().replace(' ', '_')}",
            "brand": brand,
            "name": name,
            "sku": raw_payload.get('sku'),
            "main_category": raw_payload.get('hierarchy', {}).get('category', 'Keys'), # Inference fallback
            "subcategory": raw_payload.get('hierarchy', {}).get('subcategory'),
            "description": raw_payload.get('description', ''),
            "features": features,
            "specifications": specs,
            "images": images,
            "video_urls": raw_payload.get('videos', []),
            "manual_urls": raw_payload.get('manuals', []),
            "support_url": raw_payload.get('support_url'),
            "source": SourceType.BRAND_OFFICIAL.value,
            "status": ProductStatus.IN_STOCK.value,
            "metadata": raw_payload.get('metadata', {})
        }

        return blueprint
