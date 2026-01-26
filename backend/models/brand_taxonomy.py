"""
Brand Taxonomy - Official Category Structures from Each Brand's Website

This module defines the EXACT taxonomy used by each brand on their official website.
The UI must be 100% compatible with these official taxonomies.

Each brand has:
1. Main Categories (top-level navigation)
2. Subcategories (nested under main)
3. URL patterns for scraping
4. Mapping to UI display labels

IMPORTANT: These are scraped directly from brand websites and should be treated
as the SOURCE OF TRUTH for product categorization.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


@dataclass
class CategoryNode:
    """A single category in the brand's taxonomy tree"""
    id: str                          # URL slug: "drums_percussion"
    label: str                       # Display name: "Drums & Percussion"
    url_path: str                    # Full URL path: "/global/categories/drums_percussion/"
    parent_id: Optional[str] = None  # Parent category ID, None if root
    children: List[str] = field(default_factory=list)  # Child category IDs
    icon: Optional[str] = None       # Emoji or icon name
    description: Optional[str] = None


@dataclass
class BrandTaxonomy:
    """Complete taxonomy for a single brand"""
    brand_id: str
    brand_name: str
    base_url: str
    categories: Dict[str, CategoryNode]  # id -> CategoryNode
    
    def get_root_categories(self) -> List[CategoryNode]:
        """Return only top-level categories"""
        return [cat for cat in self.categories.values() if cat.parent_id is None]
    
    def get_children(self, parent_id: str) -> List[CategoryNode]:
        """Return all direct children of a category"""
        parent = self.categories.get(parent_id)
        if not parent:
            return []
        return [self.categories[child_id] for child_id in parent.children if child_id in self.categories]
    
    def get_full_path(self, category_id: str) -> List[str]:
        """Return the full path from root to this category"""
        path = []
        current = self.categories.get(category_id)
        while current:
            path.insert(0, current.label)
            current = self.categories.get(current.parent_id) if current.parent_id else None
        return path


# =============================================================================
# ROLAND OFFICIAL TAXONOMY
# Source: https://www.roland.com/global/categories/
# Last verified: January 2026
# =============================================================================

ROLAND_TAXONOMY = BrandTaxonomy(
    brand_id="roland",
    brand_name="Roland",
    base_url="https://www.roland.com/global",
    categories={
        # Root categories
        "pianos": CategoryNode(
            id="pianos",
            label="Pianos",
            url_path="/global/categories/pianos/",
            icon="🎹",
            description="Digital Pianos, Stage Pianos, Grand Pianos",
            children=["grand_pianos", "portable_pianos", "stage_pianos", "upright_pianos", "pianos_accessories"]
        ),
        "synthesizers": CategoryNode(
            id="synthesizers",
            label="Synthesizers",
            url_path="/global/categories/synthesizers/",
            icon="🎛️",
            description="Analog Modeling, Performance Workstations",
            children=["analog_modeling", "performance_workstation", "sound_expansion_patches", "synths_accessories"]
        ),
        "keyboards": CategoryNode(
            id="keyboards",
            label="Keyboards",
            url_path="/global/categories/keyboards/",
            icon="⌨️",
            description="Arrangers, Controllers, Portable Keyboards"
        ),
        "organs": CategoryNode(
            id="organs",
            label="Organs",
            url_path="/global/categories/organs/",
            icon="🎹",
            description="Combo Organs, Organ Accessories"
        ),
        "drums_percussion": CategoryNode(
            id="drums_percussion",
            label="Drums & Percussion",
            url_path="/global/categories/drums_percussion/",
            icon="🥁",
            description="V-Drums, Electronic Percussion, Hybrid Drums",
            children=["v_drums", "electronic_percussion", "hybrid_drums", "drums_accessories"]
        ),
        "guitar_bass": CategoryNode(
            id="guitar_bass",
            label="Guitar & Bass",
            url_path="/global/categories/guitar_bass/",
            icon="🎸",
            description="Effects, Processors, Guitar Synths"
        ),
        "amplifiers": CategoryNode(
            id="amplifiers",
            label="Amplifiers",
            url_path="/global/categories/amplifiers/",
            icon="🔊",
            description="Guitar Amps, Keyboard Amps, Bass Amps",
            children=["keyboard_amplifiers", "guitar_amplifiers", "bass_amplifiers"]
        ),
        "production": CategoryNode(
            id="production",
            label="Production",
            url_path="/global/categories/production/",
            icon="🎚️",
            description="Audio Interfaces, Mixers, Video"
        ),
        "aira": CategoryNode(
            id="aira",
            label="AIRA",
            url_path="/global/categories/aira/",
            icon="🔮",
            description="TR, TB, System-1, AIRA Compact"
        ),
        "wind_instruments": CategoryNode(
            id="wind_instruments",
            label="Wind Instruments",
            url_path="/global/categories/wind_instruments/",
            icon="🎷",
            description="Aerophone, Digital Wind Instruments"
        ),
        "roland_cloud": CategoryNode(
            id="roland_cloud",
            label="Roland Cloud",
            url_path="/global/categories/roland_cloud/",
            icon="☁️",
            description="Software, Plugins, Sound Libraries"
        ),
        "accessories": CategoryNode(
            id="accessories",
            label="Accessories",
            url_path="/global/categories/accessories/",
            icon="🔧",
            description="Cables, Stands, Cases, Pedals",
            children=["cables", "instrument_cables", "microphone_cables", "interconnect_cables", 
                     "digital_cables", "midi_cables", "headphones", "stands", "cases_bags", "pedals"]
        ),
        "featured_products": CategoryNode(
            id="featured_products",
            label="Featured Products",
            url_path="/global/categories/featured_products/",
            icon="⭐",
            description="New & Featured"
        ),
        "apps": CategoryNode(
            id="apps",
            label="Apps",
            url_path="/global/categories/apps/",
            icon="📱",
            description="iOS & Android Apps"
        ),
        
        # Pianos subcategories
        "grand_pianos": CategoryNode(
            id="grand_pianos",
            label="Grand Pianos",
            url_path="/global/categories/pianos/grand_pianos/",
            parent_id="pianos"
        ),
        "portable_pianos": CategoryNode(
            id="portable_pianos",
            label="Portable Pianos",
            url_path="/global/categories/pianos/portable_pianos/",
            parent_id="pianos"
        ),
        "stage_pianos": CategoryNode(
            id="stage_pianos",
            label="Stage Pianos",
            url_path="/global/categories/pianos/stage_pianos/",
            parent_id="pianos"
        ),
        "upright_pianos": CategoryNode(
            id="upright_pianos",
            label="Upright Pianos",
            url_path="/global/categories/pianos/upright_pianos/",
            parent_id="pianos"
        ),
        "pianos_accessories": CategoryNode(
            id="pianos_accessories",
            label="Piano Accessories",
            url_path="/global/categories/pianos/accessories/",
            parent_id="pianos"
        ),
        
        # Synthesizer subcategories
        "analog_modeling": CategoryNode(
            id="analog_modeling",
            label="Analog Modeling",
            url_path="/global/categories/synthesizers/analog_modeling/",
            parent_id="synthesizers"
        ),
        "performance_workstation": CategoryNode(
            id="performance_workstation",
            label="Performance Workstation",
            url_path="/global/categories/synthesizers/performance_workstation/",
            parent_id="synthesizers"
        ),
        "sound_expansion_patches": CategoryNode(
            id="sound_expansion_patches",
            label="Sound Expansion & Patches",
            url_path="/global/categories/synthesizers/sound_expansion_patches/",
            parent_id="synthesizers"
        ),
        "synths_accessories": CategoryNode(
            id="synths_accessories",
            label="Synthesizer Accessories",
            url_path="/global/categories/synthesizers/accessories/",
            parent_id="synthesizers"
        ),
        
        # Drums subcategories
        "v_drums": CategoryNode(
            id="v_drums",
            label="V-Drums",
            url_path="/global/categories/drums_percussion/v_drums/",
            parent_id="drums_percussion"
        ),
        "electronic_percussion": CategoryNode(
            id="electronic_percussion",
            label="Electronic Percussion",
            url_path="/global/categories/drums_percussion/electronic_percussion/",
            parent_id="drums_percussion"
        ),
        "hybrid_drums": CategoryNode(
            id="hybrid_drums",
            label="Hybrid Drums",
            url_path="/global/categories/drums_percussion/hybrid_drums/",
            parent_id="drums_percussion"
        ),
        "drums_accessories": CategoryNode(
            id="drums_accessories",
            label="Drums Accessories",
            url_path="/global/categories/drums_percussion/accessories/",
            parent_id="drums_percussion"
        ),
        
        # Amplifier subcategories
        "keyboard_amplifiers": CategoryNode(
            id="keyboard_amplifiers",
            label="Keyboard Amplifiers",
            url_path="/global/categories/amplifiers/keyboard_amplifiers/",
            parent_id="amplifiers"
        ),
        "guitar_amplifiers": CategoryNode(
            id="guitar_amplifiers",
            label="Guitar Amplifiers",
            url_path="/global/categories/amplifiers/guitar_amplifiers/",
            parent_id="amplifiers"
        ),
        "bass_amplifiers": CategoryNode(
            id="bass_amplifiers",
            label="Bass Amplifiers",
            url_path="/global/categories/amplifiers/bass_amplifiers/",
            parent_id="amplifiers"
        ),
        
        # Accessories subcategories
        "cables": CategoryNode(
            id="cables",
            label="Cables",
            url_path="/global/categories/accessories/cables/",
            parent_id="accessories"
        ),
        "instrument_cables": CategoryNode(
            id="instrument_cables",
            label="Instrument Cables",
            url_path="/global/categories/accessories/instrument_cables/",
            parent_id="accessories"
        ),
        "microphone_cables": CategoryNode(
            id="microphone_cables",
            label="Microphone Cables",
            url_path="/global/categories/accessories/microphone_cables/",
            parent_id="accessories"
        ),
        "interconnect_cables": CategoryNode(
            id="interconnect_cables",
            label="Interconnect Cables",
            url_path="/global/categories/accessories/interconnect_cables/",
            parent_id="accessories"
        ),
        "digital_cables": CategoryNode(
            id="digital_cables",
            label="Digital Cables",
            url_path="/global/categories/accessories/digital_cables/",
            parent_id="accessories"
        ),
        "midi_cables": CategoryNode(
            id="midi_cables",
            label="MIDI Cables",
            url_path="/global/categories/accessories/midi_cables/",
            parent_id="accessories"
        ),
        "headphones": CategoryNode(
            id="headphones",
            label="Headphones",
            url_path="/global/categories/accessories/headphones/",
            parent_id="accessories"
        ),
        "stands": CategoryNode(
            id="stands",
            label="Stands",
            url_path="/global/categories/accessories/stands/",
            parent_id="accessories"
        ),
        "cases_bags": CategoryNode(
            id="cases_bags",
            label="Cases & Bags",
            url_path="/global/categories/accessories/cases_bags/",
            parent_id="accessories"
        ),
        "pedals": CategoryNode(
            id="pedals",
            label="Pedals",
            url_path="/global/categories/accessories/pedals/",
            parent_id="accessories"
        ),
    }
)


# =============================================================================
# BOSS OFFICIAL TAXONOMY
# Source: https://www.boss.info/global/categories/
# Last verified: January 2026
# =============================================================================

BOSS_TAXONOMY = BrandTaxonomy(
    brand_id="boss",
    brand_name="BOSS",
    base_url="https://www.boss.info/global",
    categories={
        # Root categories
        "effects_pedals": CategoryNode(
            id="effects_pedals",
            label="Effects Pedals",
            url_path="/global/categories/effects_pedals/",
            icon="🎸",
            description="Stompboxes, Compact Pedals",
            children=["stompboxes", "wah_expression", "loopers"]
        ),
        "multi_effects": CategoryNode(
            id="multi_effects",
            label="Multi-Effects",
            url_path="/global/categories/multi-effects/",
            icon="🎛️",
            description="Floor Units, Desktop"
        ),
        "guitar_synthesizers": CategoryNode(
            id="guitar_synthesizers",
            label="Guitar Synthesizers",
            url_path="/global/categories/guitar_synthesizers/",
            icon="🎹",
            description="GK, SY Series"
        ),
        "amplifiers": CategoryNode(
            id="amplifiers",
            label="Amplifiers",
            url_path="/global/categories/amplifiers/",
            icon="🔊",
            description="Katana, Cube, Acoustic"
        ),
        "acoustic": CategoryNode(
            id="acoustic",
            label="Acoustic",
            url_path="/global/categories/acoustic/",
            icon="🪕",
            description="Acoustic Amps, Preamps"
        ),
        "loop_station": CategoryNode(
            id="loop_station",
            label="Loop Station",
            url_path="/global/categories/loop_station/",
            icon="🔁",
            description="RC Series, Loop Stations"
        ),
        "vocal_effects": CategoryNode(
            id="vocal_effects",
            label="Vocal Effects",
            url_path="/global/categories/vocal_effects/",
            icon="🎤",
            description="VE Series, Vocal Processors"
        ),
        "mixers_audio_solutions": CategoryNode(
            id="mixers_audio_solutions",
            label="Mixers & Audio Solutions",
            url_path="/global/categories/mixers_audio_solutions/",
            icon="🎚️",
            description="Personal Mixers, Audio Interfaces"
        ),
        "tuners_metronomes": CategoryNode(
            id="tuners_metronomes",
            label="Tuners & Metronomes",
            url_path="/global/categories/tuners_metronomes/",
            icon="🎵",
            description="TU Series, DB Series"
        ),
        "wireless": CategoryNode(
            id="wireless",
            label="Wireless",
            url_path="/global/categories/wireless/",
            icon="📡",
            description="WL Series"
        ),
        "accessories": CategoryNode(
            id="accessories",
            label="Accessories",
            url_path="/global/categories/accessories/",
            icon="🔧",
            description="Footswitches, Power Supplies, Cables"
        ),
        "apps": CategoryNode(
            id="apps",
            label="Apps",
            url_path="/global/categories/apps/",
            icon="📱",
            description="BOSS Tone Studio, BOSS Tuner"
        ),
        "featured_products": CategoryNode(
            id="featured_products",
            label="Featured Products",
            url_path="/global/categories/featured_products/",
            icon="⭐",
            description="New & Featured"
        ),
    }
)


# =============================================================================
# NORD OFFICIAL TAXONOMY
# Source: https://www.nordkeyboards.com/products
# Last verified: January 2026
# =============================================================================

NORD_TAXONOMY = BrandTaxonomy(
    brand_id="nord",
    brand_name="Nord",
    base_url="https://www.nordkeyboards.com",
    categories={
        "stage": CategoryNode(
            id="stage",
            label="Stage",
            url_path="/products/nord-stage",
            icon="🎹",
            description="Flagship Stage Keyboards"
        ),
        "piano": CategoryNode(
            id="piano",
            label="Piano",
            url_path="/products/nord-piano",
            icon="🎹",
            description="Stage Piano Series"
        ),
        "electro": CategoryNode(
            id="electro",
            label="Electro",
            url_path="/products/nord-electro",
            icon="🎹",
            description="Electro-Mechanical Keyboards"
        ),
        "lead": CategoryNode(
            id="lead",
            label="Lead",
            url_path="/products/nord-lead",
            icon="🎛️",
            description="Virtual Analog Synths"
        ),
        "wave": CategoryNode(
            id="wave",
            label="Wave",
            url_path="/products/nord-wave",
            icon="🌊",
            description="Wavetable Synthesizers"
        ),
        "drum": CategoryNode(
            id="drum",
            label="Drum",
            url_path="/products/nord-drum",
            icon="🥁",
            description="Virtual Analog Drum Machines"
        ),
        "c_organ": CategoryNode(
            id="c_organ",
            label="C2D Organ",
            url_path="/products/nord-c2d",
            icon="🎹",
            description="Combo Organ"
        ),
        "accessories": CategoryNode(
            id="accessories",
            label="Accessories",
            url_path="/products/accessories",
            icon="🔧",
            description="Pedals, Cases, Stands"
        ),
        "software": CategoryNode(
            id="software",
            label="Software",
            url_path="/software",
            icon="💻",
            description="Sound Manager, Sample Editor"
        ),
    }
)


# =============================================================================
# MOOG OFFICIAL TAXONOMY
# Source: https://www.moogmusic.com/products
# Last verified: January 2026
# =============================================================================

MOOG_TAXONOMY = BrandTaxonomy(
    brand_id="moog",
    brand_name="Moog",
    base_url="https://www.moogmusic.com",
    categories={
        "synthesizers": CategoryNode(
            id="synthesizers",
            label="Synthesizers",
            url_path="/products/synthesizers",
            icon="🎛️",
            description="Analog Synthesizers",
            children=["semi_modular", "polyphonic", "monophonic", "modular"]
        ),
        "semi_modular": CategoryNode(
            id="semi_modular",
            label="Semi-Modular",
            url_path="/products/semi-modular",
            parent_id="synthesizers",
            description="Mother-32, DFAM, Subharmonicon"
        ),
        "polyphonic": CategoryNode(
            id="polyphonic",
            label="Polyphonic",
            url_path="/products/polyphonic",
            parent_id="synthesizers",
            description="One, Matriarch, Grandmother"
        ),
        "monophonic": CategoryNode(
            id="monophonic",
            label="Monophonic",
            url_path="/products/monophonic",
            parent_id="synthesizers",
            description="Minimoog, Sub, Voyager"
        ),
        "modular": CategoryNode(
            id="modular",
            label="Modular",
            url_path="/products/modular",
            parent_id="synthesizers",
            description="Eurorack Modules"
        ),
        "effects": CategoryNode(
            id="effects",
            label="Effects",
            url_path="/products/effects",
            icon="🎸",
            description="Moogerfooger, Minifooger"
        ),
        "keyboards": CategoryNode(
            id="keyboards",
            label="Keyboards",
            url_path="/products/keyboards",
            icon="⌨️",
            description="Controllers"
        ),
        "accessories": CategoryNode(
            id="accessories",
            label="Accessories",
            url_path="/products/accessories",
            icon="🔧",
            description="Cables, Cases, Patch Cables"
        ),
        "apps": CategoryNode(
            id="apps",
            label="Apps",
            url_path="/products/apps",
            icon="📱",
            description="Animoog, Model D"
        ),
    }
)


# =============================================================================
# MASTER REGISTRY
# =============================================================================

BRAND_TAXONOMIES: Dict[str, BrandTaxonomy] = {
    "roland": ROLAND_TAXONOMY,
    "boss": BOSS_TAXONOMY,
    "nord": NORD_TAXONOMY,
    "moog": MOOG_TAXONOMY,
}


def get_brand_taxonomy(brand_id: str) -> Optional[BrandTaxonomy]:
    """Get the taxonomy for a specific brand"""
    return BRAND_TAXONOMIES.get(brand_id.lower())


def get_all_brand_categories(brand_id: str) -> List[str]:
    """Get all category labels for a brand"""
    taxonomy = get_brand_taxonomy(brand_id)
    if not taxonomy:
        return []
    return [cat.label for cat in taxonomy.categories.values()]


def validate_category(brand_id: str, category: str) -> bool:
    """Check if a category is valid for a brand"""
    taxonomy = get_brand_taxonomy(brand_id)
    if not taxonomy:
        return False
    # Check both ID and label
    return any(
        cat.id == category.lower().replace(" ", "_") or 
        cat.label.lower() == category.lower()
        for cat in taxonomy.categories.values()
    )


def normalize_category(brand_id: str, raw_category: str) -> Optional[str]:
    """
    Normalize a raw category string to the official brand taxonomy.
    Returns the official label or None if no match found.
    
    Matching priority:
    1. Exact ID match (slug)
    2. Exact label match (case-insensitive)
    3. Significant word overlap (must match >50% of words)
    
    Known non-taxonomy categories like "Musical Instruments" return None.
    """
    taxonomy = get_brand_taxonomy(brand_id)
    if not taxonomy:
        return None
    
    if not raw_category:
        return None
    
    raw_lower = raw_category.lower().strip()
    raw_slug = raw_lower.replace("-", "_").replace(" ", "_")
    
    # Special case: Generic categories that are NOT in any brand's taxonomy
    # These should return None so the scraper knows to look deeper
    GENERIC_NON_TAXONOMY = {
        "musical instruments",
        "music",
        "products",
        "all products",
        "all",
        "home",
        "categories",
    }
    if raw_lower in GENERIC_NON_TAXONOMY:
        return None
    
    # 1. Direct match on ID (slug)
    if raw_slug in taxonomy.categories:
        return taxonomy.categories[raw_slug].label
    
    # 2. Exact match on label (case-insensitive)
    for cat in taxonomy.categories.values():
        if cat.label.lower() == raw_lower:
            return cat.label
    
    # 3. Check for significant word overlap
    # Both "Pianos" and "Digital Pianos" should map to "Pianos"
    # But "Digital Pianos" should NOT map to "Digital Cables"
    # Stop words to ignore in matching
    STOP_WORDS = {"the", "and", "&", "a", "an", "for", "of", "in", "on", "to", "instruments"}
    
    raw_words = set(w.lower() for w in raw_lower.split() if len(w) > 2 and w.lower() not in STOP_WORDS)
    
    best_match = None
    best_score = 0
    
    for cat in taxonomy.categories.values():
        cat_words = set(w.lower() for w in cat.label.split() if len(w) > 2 and w.lower() not in STOP_WORDS)
        
        if not cat_words or not raw_words:
            continue
            
        # Calculate overlap
        overlap = raw_words & cat_words
        
        if overlap:
            # Score based on how much of the category matches
            # Prefer categories where the raw string contains ALL category words
            cat_coverage = len(overlap) / len(cat_words)
            raw_coverage = len(overlap) / len(raw_words)
            
            # Must have at least 50% coverage of both
            if cat_coverage >= 0.5 and raw_coverage >= 0.5:
                score = cat_coverage + raw_coverage
                
                # Bonus for root categories (no parent)
                if cat.parent_id is None:
                    score += 0.5
                    
                if score > best_score:
                    best_score = score
                    best_match = cat.label
    
    return best_match


# =============================================================================
# EXPORT FOR FRONTEND (JSON-serializable)
# =============================================================================

def export_taxonomy_to_json(brand_id: str) -> dict:
    """Export a brand's taxonomy as JSON-serializable dict"""
    taxonomy = get_brand_taxonomy(brand_id)
    if not taxonomy:
        return {}
    
    return {
        "brand_id": taxonomy.brand_id,
        "brand_name": taxonomy.brand_name,
        "categories": [
            {
                "id": cat.id,
                "label": cat.label,
                "parent_id": cat.parent_id,
                "icon": cat.icon,
                "description": cat.description,
                "children": cat.children,
            }
            for cat in taxonomy.categories.values()
        ]
    }


def export_all_taxonomies_to_json() -> dict:
    """Export all brand taxonomies for frontend consumption"""
    return {
        brand_id: export_taxonomy_to_json(brand_id)
        for brand_id in BRAND_TAXONOMIES.keys()
    }


if __name__ == "__main__":
    # Test output
    import json
    
    print("=== Brand Taxonomies ===\n")
    
    for brand_id, taxonomy in BRAND_TAXONOMIES.items():
        print(f"📦 {taxonomy.brand_name} ({len(taxonomy.categories)} categories)")
        for cat in taxonomy.get_root_categories():
            print(f"   {cat.icon or '•'} {cat.label}")
            children = taxonomy.get_children(cat.id)
            for child in children[:3]:
                print(f"      └─ {child.label}")
            if len(children) > 3:
                print(f"      └─ ... ({len(children) - 3} more)")
        print()
    
    # Export JSON
    print("\n=== JSON Export ===\n")
    print(json.dumps(export_taxonomy_to_json("roland"), indent=2)[:500] + "...")
