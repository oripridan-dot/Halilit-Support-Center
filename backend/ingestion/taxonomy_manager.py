"""
TAXONOMY MANAGER v6.0

Manages universal product taxonomy, brand-specific mappings, and
validates products against the taxonomy system.

This is the single source of truth for "what categories exist and how to map to them".
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("TaxonomyManager")


@dataclass
class TaxonomyNode:
    """A node in the taxonomy hierarchy"""
    category: str  # Main category
    subcategory: str  # Subcategory
    # Keywords that map to this
    keywords: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)  # Alternative names
    description: str = ""
    display_order: int = 100  # For UI ordering


class TaxonomyManager:
    """
    Universal taxonomy system with multi-level categorization.

    Maps all product names → universal canonical taxonomy
    Supports brand-specific variations
    """

    def __init__(self):
        self.logger = logger

        # UNIVERSAL TAXONOMY: The single source of truth
        self.universal_taxonomy = self._build_universal_taxonomy()

        # BRAND MAPPINGS: How each brand's terminology maps to universal
        self.brand_taxonomy_mappings = self._build_brand_mappings()

        # KEYWORD INDEX: Fast lookup from any keyword to categories
        self.keyword_index = self._build_keyword_index()

    # ============================================================================
    # TAXONOMY DEFINITION
    # ============================================================================

    def _build_universal_taxonomy(self) -> Dict[str, Dict[str, TaxonomyNode]]:
        """Define the complete universal product taxonomy"""

        return {
            # KEYBOARDS & SYNTHESIZERS
            "Keyboards & Synthesizers": {
                "Synthesizer": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Synthesizer",
                    keywords=["synthesizer", "synth", "polysynth",
                              "monozsynth", "analog synth"],
                    aliases=["Synth", "Electronic Synthesizer",
                             "Sound Generator"],
                    description="Electronic sound generation instrument",
                    display_order=10,
                ),
                "Digital Keyboard": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Digital Keyboard",
                    keywords=["digital keyboard", "workstation",
                              "portable keyboard", "stage keyboard"],
                    aliases=["Keyboard", "Electronic Keyboard",
                             "Workstation", "Stage Piano"],
                    display_order=20,
                ),
                "Digital Piano": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Digital Piano",
                    keywords=["digital piano", "electric piano",
                              "portable piano", "stage piano", "weighted keys"],
                    aliases=["Piano", "Electronic Piano", "88-Key Keyboard"],
                    display_order=15,
                ),
                "Nord Keyboard": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Nord Keyboard",
                    keywords=["nord grand", "nord lead",
                              "nord stage", "nord clavia"],
                    aliases=["Nord", "Nord Synth"],
                    display_order=5,
                ),
                "Moog Synthesizer": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Moog Synthesizer",
                    keywords=["moog", "minimoog", "moog sub", "moog modular"],
                    aliases=["Moog", "Moog One", "Moog Sub"],
                    display_order=8,
                ),
                "Groovebox": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Groovebox",
                    keywords=["groovebox", "production center",
                              "beat maker", "sampler"],
                    aliases=["Beat Maker", "Production Station"],
                    display_order=25,
                ),
                "Organ": TaxonomyNode(
                    category="Keyboards & Synthesizers",
                    subcategory="Organ",
                    keywords=["organ", "electronic organ", "hammond organ"],
                    aliases=["Electronic Organ"],
                    display_order=30,
                ),
            },

            # DRUMS & PERCUSSION
            "Drums & Percussion": {
                "Electronic Drum": TaxonomyNode(
                    category="Drums & Percussion",
                    subcategory="Electronic Drum",
                    keywords=["electronic drum", "v-drum",
                              "digital drum", "e-drum"],
                    aliases=["E-Drum", "Electronic Drum Kit",
                             "Digital Drum Kit"],
                    display_order=10,
                ),
                "Drum Trigger": TaxonomyNode(
                    category="Drums & Percussion",
                    subcategory="Drum Trigger",
                    keywords=["drum trigger", "rim trigger", "pad trigger"],
                    aliases=["Trigger", "Drum Trigger Module"],
                    display_order=20,
                ),
                "Drum Pad": TaxonomyNode(
                    category="Drums & Percussion",
                    subcategory="Drum Pad",
                    keywords=["drum pad", "percussion pad", "sample pad"],
                    aliases=["Pad", "Sampler Pad"],
                    display_order=15,
                ),
                "Percussion": TaxonomyNode(
                    category="Drums & Percussion",
                    subcategory="Percussion",
                    keywords=["percussion", "timpani", "cymbal", "marimba"],
                    aliases=["Percussion Instrument"],
                    display_order=25,
                ),
                "Drum Kit": TaxonomyNode(
                    category="Drums & Percussion",
                    subcategory="Drum Kit",
                    keywords=["drum kit", "acoustic drum", "drum set"],
                    aliases=["Acoustic Drums", "Drum Set"],
                    display_order=5,
                ),
            },

            # AUDIO INTERFACES & MIXERS
            "Audio Interfaces & Mixers": {
                "Audio Interface": TaxonomyNode(
                    category="Audio Interfaces & Mixers",
                    subcategory="Audio Interface",
                    keywords=["audio interface", "usb interface",
                              "audio converter", "sound card"],
                    aliases=["Interface", "USB Audio Interface", "Sound Card"],
                    display_order=10,
                ),
                "Mixer": TaxonomyNode(
                    category="Audio Interfaces & Mixers",
                    subcategory="Mixer",
                    keywords=["mixer", "mixing console",
                              "analog mixer", "desk"],
                    aliases=["Mixing Console", "Audio Desk", "Mixer Console"],
                    display_order=15,
                ),
                "Preamp": TaxonomyNode(
                    category="Audio Interfaces & Mixers",
                    subcategory="Preamp",
                    keywords=["preamp", "microphone preamp", "preampilifier"],
                    aliases=["Preamplifier", "Mic Preamp"],
                    display_order=20,
                ),
            },

            # MICROPHONES & RECORDING
            "Microphones & Recording": {
                "Condenser Mic": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Condenser Mic",
                    keywords=["condenser microphone",
                              "condenser mic", "large diaphragm"],
                    aliases=["Condenser", "Large Diaphragm Mic"],
                    display_order=10,
                ),
                "Dynamic Mic": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Dynamic Mic",
                    keywords=["dynamic microphone",
                              "dynamic mic", "moving coil"],
                    aliases=["Dynamic", "Cardioid Mic"],
                    display_order=15,
                ),
                "Ribbon Mic": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Ribbon Mic",
                    keywords=["ribbon microphone",
                              "ribbon mic", "passive ribbon"],
                    aliases=["Ribbon", "Vintage Mic"],
                    display_order=20,
                ),
                "Wireless Mic": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Wireless Mic",
                    keywords=["wireless microphone",
                              "wireless mic", "rf wireless"],
                    aliases=["Wireless", "Radio Mic"],
                    display_order=25,
                ),
                "Microphone": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Microphone",
                    keywords=["microphone", "mic", "vocal mic"],
                    aliases=["Recording Mic"],
                    display_order=5,
                ),
                "Recording Equipment": TaxonomyNode(
                    category="Microphones & Recording",
                    subcategory="Recording Equipment",
                    keywords=["recording equipment",
                              "daw", "recording interface"],
                    aliases=["Recording Studio", "DAW"],
                    display_order=30,
                ),
            },

            # CABLES & CONNECTORS
            "Cables & Connectors": {
                "Cable": TaxonomyNode(
                    category="Cables & Connectors",
                    subcategory="Cable",
                    keywords=["cable", "xlr cable", "1/4\" cable",
                              "balanced cable", "usb cable"],
                    aliases=["Audio Cable", "Instrument Cable",
                             "Connection Cable"],
                    display_order=10,
                ),
                "Connector": TaxonomyNode(
                    category="Cables & Connectors",
                    subcategory="Connector",
                    keywords=["connector", "coupler", "panel mount"],
                    aliases=["Audio Connector", "Connection Hardware"],
                    display_order=15,
                ),
                "Jack": TaxonomyNode(
                    category="Cables & Connectors",
                    subcategory="Jack",
                    keywords=["jack", "xlr jack", "1/4\" jack"],
                    aliases=["Connection Jack"],
                    display_order=20,
                ),
            },

            # STUDIO MONITORS & SPEAKERS
            "Studio Monitors & Speakers": {
                "Studio Monitor": TaxonomyNode(
                    category="Studio Monitors & Speakers",
                    subcategory="Studio Monitor",
                    keywords=["studio monitor", "nearfield monitor",
                              "powered speaker", "active speaker"],
                    aliases=["Monitor", "Reference Speaker"],
                    display_order=10,
                ),
                "Powered Speaker": TaxonomyNode(
                    category="Studio Monitors & Speakers",
                    subcategory="Powered Speaker",
                    keywords=["powered speaker",
                              "active speaker", "amplified speaker"],
                    aliases=["Active Speaker", "Amplified Speaker"],
                    display_order=15,
                ),
                "Speaker": TaxonomyNode(
                    category="Studio Monitors & Speakers",
                    subcategory="Speaker",
                    keywords=["speaker", "speaker system"],
                    aliases=["Audio Speaker"],
                    display_order=20,
                ),
            },

            # HEADPHONES & EARPHONES
            "Headphones & Earphones": {
                "Headphones": TaxonomyNode(
                    category="Headphones & Earphones",
                    subcategory="Headphones",
                    keywords=["headphones", "over-ear", "closed-back"],
                    aliases=["Over-Ear Headphones", "Monitoring Headphones"],
                    display_order=10,
                ),
                "In-Ear Monitors": TaxonomyNode(
                    category="Headphones & Earphones",
                    subcategory="In-Ear Monitors",
                    keywords=["in-ear monitor", "iem", "earphones"],
                    aliases=["IEM", "Stage Monitoring"],
                    display_order=15,
                ),
                "Earbuds": TaxonomyNode(
                    category="Headphones & Earphones",
                    subcategory="Earbuds",
                    keywords=["earbuds", "true wireless", "wireless earphone"],
                    aliases=["Wireless Earbuds"],
                    display_order=20,
                ),
            },

            # AMPLIFIERS & EFFECTS
            "Amplifiers & Effects": {
                "Amplifier": TaxonomyNode(
                    category="Amplifiers & Effects",
                    subcategory="Amplifier",
                    keywords=["amplifier", "amp", "power amp", "combo amp"],
                    aliases=["Amp", "Guitar Amplifier"],
                    display_order=10,
                ),
                "Effects Processor": TaxonomyNode(
                    category="Amplifiers & Effects",
                    subcategory="Effects Processor",
                    keywords=["effects processor",
                              "effects unit", "reverb", "delay"],
                    aliases=["Effects Unit", "Multi-Effects"],
                    display_order=15,
                ),
                "Pedal": TaxonomyNode(
                    category="Amplifiers & Effects",
                    subcategory="Pedal",
                    keywords=["pedal", "foot pedal", "expression pedal"],
                    aliases=["Effects Pedal", "Control Pedal"],
                    display_order=20,
                ),
            },
        }

    def _build_brand_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Map brand-specific terminology to universal taxonomy.

        Format: {
            'brand': {
                'brand_specific_term': 'Universal Category > Subcategory'
            }
        }
        """
        return {
            'Nord': {
                'Nord Lead': 'Keyboards & Synthesizers > Synthesizer',
                'Nord Lead A1': 'Keyboards & Synthesizers > Synthesizer',
                'Nord Clavia': 'Keyboards & Synthesizers > Digital Keyboard',
                'Nord Grand': 'Keyboards & Synthesizers > Digital Piano',
                'Nord Stage': 'Keyboards & Synthesizers > Digital Keyboard',
            },
            'Moog': {
                'Minimoog': 'Keyboards & Synthesizers > Moog Synthesizer',
                'Moog Sub 37': 'Keyboards & Synthesizers > Moog Synthesizer',
                'Moog One': 'Keyboards & Synthesizers > Moog Synthesizer',
                'Moog Matriarch': 'Keyboards & Synthesizers > Moog Synthesizer',
            },
            'Roland': {
                # Drum products (V-Drums, TD, VAD series)
                'V-Drums': 'Drums & Percussion > Electronic Drum',
                'V-Cymbal': 'Drums & Percussion > Cymbal',
                'TD-': 'Drums & Percussion > Electronic Drum',
                'VAD': 'Drums & Percussion > Electronic Drum',
                'TR-': 'Drums & Percussion > Drum Pad',
                'TR-808': 'Drums & Percussion > Drum Pad',
                'TR-909': 'Drums & Percussion > Drum Pad',
                'SPD': 'Drums & Percussion > Drum Pad',
                'Handsonic': 'Drums & Percussion > Drum Pad',
                'VQD': 'Drums & Percussion > Electronic Drum',
                # Keyboard/Synth products (CRITICAL: Match piano codes first!)
                'RP': 'Keyboards & Synthesizers > Digital Piano',
                'RP-': 'Keyboards & Synthesizers > Digital Piano',
                'FP-': 'Keyboards & Synthesizers > Digital Piano',
                'RD-': 'Keyboards & Synthesizers > Digital Piano',
                'Juno': 'Keyboards & Synthesizers > Synthesizer',
                'Jupiter': 'Keyboards & Synthesizers > Synthesizer',
                'JD-': 'Keyboards & Synthesizers > Synthesizer',
                'JX-': 'Keyboards & Synthesizers > Synthesizer',
                'Fantom': 'Keyboards & Synthesizers > Digital Keyboard',
                'Fantom-': 'Keyboards & Synthesizers > Digital Keyboard',
                'FANTOM': 'Keyboards & Synthesizers > Digital Keyboard',
                'GW-': 'Keyboards & Synthesizers > Digital Keyboard',
                'LK-': 'Keyboards & Synthesizers > Digital Keyboard',
                'E-': 'Keyboards & Synthesizers > Digital Keyboard',
                'GO': 'Keyboards & Synthesizers > Groovebox',
                'MC-101': 'Keyboards & Synthesizers > Groovebox',
                'VP-': 'Keyboards & Synthesizers > Groovebox',
                'Verselab': 'Keyboards & Synthesizers > Groovebox',
                'Aira': 'Keyboards & Synthesizers > Groovebox',
                # Wind/Aerophone
                'Aerophone': 'Keyboards & Synthesizers > Electronic Wind',
                # Amplifiers
                'CUBE': 'Amplifiers & Effects > Amplifier',
                'Blues Cube': 'Amplifiers & Effects > Amplifier',
                'Bolt': 'Amplifiers & Effects > Amplifier',
                # Effects/Pedals
                'Boss': 'Amplifiers & Effects > Effect Pedal',
                'GT-': 'Amplifiers & Effects > Effect Pedal',
                'ME-': 'Amplifiers & Effects > Effect Pedal',
                'Tera Echo': 'Amplifiers & Effects > Effect Pedal',
                # Headphones
                'RH-': 'Headphones & Earphones > Headphones',
                # Video/Streaming equipment
                'VR-': 'Other > Accessories',
                # Accessories & Cables (must come last to avoid false matches)
                'RCC': 'Cables & Connectors > Cable',
                'RIC': 'Cables & Connectors > Cable',
                'RMC': 'Cables & Connectors > Cable',
                'RMI': 'Cables & Connectors > MIDI Cable',
                'CB-': 'Cases & Bags > Case',
                'KSC': 'Stands & Storage > Keyboard Stand',
                'ST-': 'Stands & Storage > Stand',
                'RPB': 'Stands & Storage > Stand',
                'RSC': 'Stands & Storage > Storage',
            },
            'Elektron': {
                'Analog Rytm': 'Drums & Percussion > Groovebox',
                'Analog Four': 'Keyboards & Synthesizers > Groovebox',
                'Digitakt': 'Keyboards & Synthesizers > Groovebox',
            },
            'Yamaha': {
                'Montage': 'Keyboards & Synthesizers > Digital Keyboard',
                'MOTIF': 'Keyboards & Synthesizers > Digital Keyboard',
                'P-125': 'Keyboards & Synthesizers > Digital Piano',
            },
            'Korg': {
                'Korg Volca': 'Keyboards & Synthesizers > Synthesizer',
                'Korg Minilogue': 'Keyboards & Synthesizers > Synthesizer',
                'Korg Prologue': 'Keyboards & Synthesizers > Synthesizer',
            },
        }

    def _build_keyword_index(self) -> Dict[str, Tuple[str, str]]:
        """Build fast lookup from any keyword to (category, subcategory)"""
        index = {}

        for category, subcats in self.universal_taxonomy.items():
            for subcat, node in subcats.items():
                # Index all keywords and aliases
                for keyword in node.keywords + node.aliases:
                    key = keyword.lower()
                    index[key] = (category, subcat)

        return index

    # ============================================================================
    # CLASSIFICATION OPERATIONS
    # ============================================================================

    def classify_product(
        self,
        product_name: str,
        brand: str,
        description: str = "",
        specifications: Dict = None,
    ) -> Tuple[str, str, float]:
        """
        Classify a product into the universal taxonomy.

        Returns: (category, subcategory, confidence_score)
        """
        if specifications is None:
            specifications = {}

        # Step 1: Try brand-specific mappings first (highest confidence)
        if brand in self.brand_taxonomy_mappings:
            for brand_term, mapping in self.brand_taxonomy_mappings[brand].items():
                if brand_term.lower() in product_name.lower():
                    cat, subcat = mapping.split(" > ")
                    self.logger.info(
                        f"✓ {product_name} → {cat} > {subcat} (brand mapping, conf=0.98)")
                    return cat, subcat, 0.98

        # Step 2: Look for keyword matches in product name + description
        combined_text = (product_name + " " + description + " " +
                         " ".join(str(v) for v in specifications.values())).lower()

        best_match = None
        best_confidence = 0.0

        for keyword, (category, subcategory) in self.keyword_index.items():
            if keyword in combined_text:
                # More specific keywords (longer) get higher confidence
                confidence = min(0.95, 0.7 + (len(keyword) / 50.0))

                if confidence > best_confidence:
                    best_match = (category, subcategory)
                    best_confidence = confidence

        if best_match:
            cat, subcat = best_match
            self.logger.info(
                f"✓ {product_name} → {cat} > {subcat} (keyword match, conf={best_confidence:.2f})")
            return cat, subcat, best_confidence

        # Step 3: Fallback - use "Other" category
        self.logger.warning(
            f"⚠ {product_name} → No category match (using fallback)")
        return "Other", "Uncategorized", 0.3

    def normalize_category(self, category: str, force_universal: bool = True) -> Optional[str]:
        """
        Normalize a category name to match universal taxonomy.

        If force_universal=True, returns None if not in universal taxonomy.
        """
        for cat_key in self.universal_taxonomy.keys():
            if cat_key.lower() == category.lower():
                return cat_key

        if force_universal:
            return None

        return category

    def get_category_description(self, category: str) -> str:
        """Get description of a category"""
        if category in self.universal_taxonomy:
            subcats = self.universal_taxonomy[category]
            descriptions = [node.description for node in subcats.values()]
            return f"{category}: " + "; ".join(descriptions)
        return ""

    def validate_category(self, category: str, subcategory: str) -> bool:
        """Check if a category/subcategory combination exists"""
        if category not in self.universal_taxonomy:
            return False

        if subcategory not in self.universal_taxonomy[category]:
            return False

        return True

    def get_all_categories(self) -> List[str]:
        """Get all category names"""
        return list(self.universal_taxonomy.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """Get all subcategories for a category"""
        if category not in self.universal_taxonomy:
            return []

        return list(self.universal_taxonomy[category].keys())

    def export_taxonomy_structure(self) -> Dict:
        """Export complete taxonomy for frontend/documentation"""
        result = {}

        for category, subcats in self.universal_taxonomy.items():
            result[category] = {}
            for subcat, node in subcats.items():
                result[category][subcat] = {
                    'description': node.description,
                    'display_order': node.display_order,
                    'aliases': node.aliases,
                    'example_keywords': node.keywords[:5],  # First 5 keywords
                }

        return result


# Global singleton
_taxonomy_manager = None


def get_taxonomy_manager() -> TaxonomyManager:
    """Get or create the global taxonomy manager"""
    global _taxonomy_manager
    if _taxonomy_manager is None:
        _taxonomy_manager = TaxonomyManager()
        logger.info("✅ Taxonomy Manager initialized")
    return _taxonomy_manager
