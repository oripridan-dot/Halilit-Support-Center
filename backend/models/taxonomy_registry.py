"""
Minimal Taxonomy Registry for Halilit Catalog
"""
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timezone


class Category:
    def __init__(self, id: str, label: str, icon: str = "", description: str = "", children: List = None):
        self.id = id
        self.label = label
        self.icon = icon
        self.description = description
        self.children = children or []


class BrandTaxonomy:
    def __init__(self, brand_id: str, categories: List[Category] = None):
        self.brand_id = brand_id
        self.categories = categories or []
    
    def get_root_categories(self):
        return self.categories


class TaxonomyRegistry:
    """Manages universal and brand-specific product categories"""
    
    # Universal categories - consistent across all brands
    UNIVERSAL_CATEGORIES = {
        "keys": Category("keys", "Keys & Pianos", "🎹", "Keyboards and pianos"),
        "drums": Category("drums", "Drums & Percussion", "🥁", "Drums and percussion"),
        "guitars": Category("guitars", "Guitars & Amps", "🎸", "Guitars and amplifiers"),
        "studio": Category("studio", "Studio & Recording", "🎙️", "Studio and recording gear"),
        "live": Category("live", "Live Sound", "🔊", "Live sound equipment"),
        "dj": Category("dj", "DJ & Production", "🎧", "DJ and production gear"),
        "software": Category("software", "Software & Cloud", "💻", "Software and cloud services"),
        "accessories": Category("accessories", "Accessories", "🔧", "Accessories and add-ons"),
    }
    
    # Manufacturer specific mappings
    BRAND_TAXONOMIES = {
        "roland": {
            "Production": "studio",
            "Drums": "drums",
            "Keys": "keys",
            "Keyboards": "keys",
            "Synthesizers": "keys",
            "Pianos": "keys",
            "Controllers": "accessories",
            "Interfaces": "studio",
            "Software": "software",
            "Effects": "studio",
            "Amplifiers": "live",
            "Speakers": "live",
            "Uncategorized": "accessories",
        },
        "nord": {
            "Keyboards": "keys",
            "Synthesizers": "keys",
            "Controllers": "keys",
            "Pedals": "accessories",
            "Accessories": "accessories",
            "Software": "software",
            "Uncategorized": "accessories",
        },
        "boss": {
            "Effects": "studio",
            "Guitars": "guitars",
            "Drums": "drums",
            "Keyboards": "keys",
            "Controllers": "accessories",
            "Interfaces": "studio",
            "Uncategorized": "accessories",
        },
        "moog": {
            "Synthesizers": "keys",
            "Controllers": "keys",
            "Effects": "studio",
            "Accessories": "accessories",
            "Software": "software",
            "Uncategorized": "accessories",
        },
        "universal-audio": {
            "Plugins": "software",
            "Hardware": "studio",
            "Interfaces": "studio",
            "Accessories": "accessories",
            "Software": "software",
            "Uncategorized": "accessories",
        },
        "bespeco": {
             "Stands": "accessories",
             "Cables": "accessories",
             "Connectors": "accessories",
             "Bags": "accessories",
             "Accessories": "accessories",
             "keys": "accessories", # Bespeco keys are usually stands
             "Keys": "accessories"
        },
        # Explicit Fix for Foxgear
        "foxgear-guitar-effects-and-pedals": {
            "general": "guitars",  # Foxgear makes pedals, "general" implies their main line
            "pedals": "guitars",
            "effects": "guitars"
        }
    }

    # Global Keyword Matcher (Fallback system)
    # Maps common terms in category names to Universal IDs
    GLOBAL_KEYWORD_RULES = {
        # Guitars
        "guitar": "guitars", "bass": "guitars", "amp": "guitars", 
        "pedal": "guitars", "fuzz": "guitars", "distortion": "guitars", "overdrive": "guitars",
        "ukulele": "guitars", "mandolin": "guitars", "banjo": "guitars",
        
        # Drums
        "drum": "drums", "percussion": "drums", "cajon": "drums", "cymbal": "drums", 
        "snare": "drums", "tom": "drums", "stick": "drums", "hardware": "drums",
        
        # Keys
        "piano": "keys", "synth": "keys", "keyboard": "keys", "organ": "keys", "accordion": "keys",
        
        # Studio
        "studio": "studio", "recording": "studio", "monitor": "studio", 
        "microphone": "studio", "mic": "studio", "interface": "studio", "preamp": "studio",
        
        # Live
        "live": "live", "wireless": "live", "mixer": "live", "pa system": "live", 
        "speaker": "live", "subwoofer": "live", "loudspeaker": "live",
        
        # DJ
        "dj": "dj", "controller": "dj", "turntable": "dj",
        
        # Software
        "software": "software", "plugin": "software", "cloud": "software", "app": "software",
        
        # Accessories
        "accessory": "accessories", "accessories": "accessories", "case": "accessories", 
        "bag": "accessories", "cable": "accessories", "stand": "accessories", "tuner": "accessories",
        "stool": "accessories", "bench": "accessories", "metronome": "accessories", "general": "accessories"
    }
    
    def __init__(self):
        self.brands = {}
        self._initialize_brands()
    
    def _initialize_brands(self):
        """Initialize brand taxonomies"""
        for brand_id in list(self.BRAND_TAXONOMIES.keys()):
            self.brands[brand_id] = BrandTaxonomy(brand_id, list(self.UNIVERSAL_CATEGORIES.values()))
    
    def normalize_category(self, brand_id: str, raw_category: str) -> Optional[str]:
        """Map brand-specific category to universal category"""
        if not raw_category:
            return None
        
        raw_lower = raw_category.lower().strip()
        
        # 0. Pre-Validation: Is it already a Universal Category?
        # This handles cases where the scraper already found a perfect match (e.g. "keys", "drums")
        if raw_lower in self.UNIVERSAL_CATEGORIES:
            return raw_lower

        # 1. Brand-Specific Mapping (Highest Priority)
        brand_map = self.BRAND_TAXONOMIES.get(brand_id, {})
        
        # Try exact match
        if raw_category in brand_map:
            return brand_map[raw_category]
        
        # Try case-insensitive match
        for key, value in brand_map.items():
            if key.lower() == raw_lower:
                return value
        
        # Try substring in brand map
        for key, value in brand_map.items():
            if key.lower() in raw_lower or raw_lower in key.lower():
                return value
        
        # 2. Global Keyword Fallback (Systemic Standardization)
        # This catches "Electric Guitars" -> "guitars", "Snare Drums" -> "drums", etc.
        for keyword, universal_id in self.GLOBAL_KEYWORD_RULES.items():
             if keyword in raw_lower:
                 return universal_id

        # No match found
        return None
    
    def get_brand(self, brand_id: str) -> Optional[BrandTaxonomy]:
        """Get taxonomy for a specific brand"""
        return self.brands.get(brand_id)
    
    def get_all_brands(self) -> List[str]:
        """Get all registered brands"""
        return list(self.brands.keys())
    
    def export_to_frontend(self, output_path: Path):
        """Export taxonomy to frontend JSON"""
        taxonomy_data = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "universal_categories": [
                {
                    "id": cat.id,
                    "label": cat.label,
                    "icon": cat.icon,
                    "description": cat.description,
                }
                for cat in self.UNIVERSAL_CATEGORIES.values()
            ],
            "brand_mappings": self.BRAND_TAXONOMIES,
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(taxonomy_data, f, indent=2)


# Global registry instance
_registry = None


def get_registry() -> TaxonomyRegistry:
    """Get the global taxonomy registry"""
    global _registry
    if _registry is None:
        _registry = TaxonomyRegistry()
    return _registry
