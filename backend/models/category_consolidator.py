"""
Category Consolidator - The "Logic Engine" (v3.0 - Galaxy/Spectrum)

This module implements the "Galaxy -> Spectrum" mapping logic.
It takes raw scraped data and routes it to specific Spectrum IDs.

Architecture:
1. Scraper gets "Raw Category" (e.g. "Solid Body Electric")
2. Consolidator maps it to "Tribe ID" (e.g. "guitars-bass")
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ConsolidatedCategory:
    id: str
    label: str
    icon: str
    color: str
    description: str
    sort_order: int

# Reference for the 6 Galaxies (Tribes) - Source of Truth is taxonomy.json
# IDs MUST match what SpectrumModule expects
CONSOLIDATED_CATEGORIES: List[ConsolidatedCategory] = [
    ConsolidatedCategory("guitars-bass", "Guitars & Bass", "guitar", "var(--galaxy-orange)", "The Plucked Universe", 1),
    ConsolidatedCategory("drums-percussion", "Drums & Percussion", "drum", "var(--galaxy-red)", "The Struck Universe", 2),
    ConsolidatedCategory("keys-production", "Keys & Synths", "piano", "var(--galaxy-purple)", "The Synthesis Universe", 3),
    ConsolidatedCategory("studio-recording", "Studio & Recording", "mic", "var(--galaxy-blue)", "The Engineer's Universe", 4),
    ConsolidatedCategory("live-dj", "Live Sound & DJ", "speaker", "var(--galaxy-green)", "The Stage Universe", 5),
    ConsolidatedCategory("accessories", "Accessories", "plug", "var(--galaxy-gray)", "The Connection Universe", 6),
]

# The Logic: Mapping "Raw Scraped Terms" -> "Tribe IDs"
SPECTRUM_MAP = {
    # --- GUITARS GALAXY ---
    "electric guitar": "guitars-bass",
    "solid body": "guitars-bass",
    "hollow body": "guitars-bass",
    "acoustic guitar": "guitars-bass",
    "classical guitar": "guitars-bass",
    "bass guitar": "guitars-bass",
    "4-string bass": "guitars-bass",
    "guitar amp": "guitars-bass",
    "cabinet": "guitars-bass",
    "pedal": "guitars-bass",
    "stompbox": "guitars-bass",
    "ukulele": "guitars-bass",
    "banjo": "guitars-bass",
    "guitar string": "guitars-bass", 
    "pick": "guitars-bass",
    "guitar strap": "guitars-bass",

    # --- DRUMS GALAXY ---
    "drum kit": "drums-percussion",
    "shell pack": "drums-percussion",
    "snare": "drums-percussion",
    "cymbal": "drums-percussion",
    "electronic drum": "drums-percussion",
    "v-drums": "drums-percussion",
    "drumstick": "drums-percussion",
    "drum head": "drums-percussion",
    "cajon": "drums-percussion",
    "bongo": "drums-percussion",
    "drum hardware": "drums-percussion",
    "cymbal stand": "drums-percussion",
    "pedal": "drums-percussion",
    "bass drum": "drums-percussion",

    # --- KEYS GALAXY ---
    "synthesizer": "keys-production",
    "eurorack": "keys-production",
    "stage piano": "keys-production",
    "digital piano": "keys-production",
    "midi controller": "keys-production",
    "keyboard": "keys-production", 
    "groovebox": "keys-production",
    "sampler": "keys-production",

    # --- STUDIO GALAXY ---
    "audio interface": "studio-recording",
    "studio monitor": "studio-recording",
    "condenser microphone": "studio-recording",
    "ribbon microphone": "studio-recording",
    "daw": "studio-recording",
    "plugin": "studio-recording",
    "preamp": "studio-recording",
    "compressor": "studio-recording",

    # --- LIVE GALAXY ---
    "pa speaker": "live-dj",
    "subwoofer": "live-dj",
    "live mixer": "live-dj",
    "dj controller": "live-dj",
    "turntable": "live-dj",
    "wireless microphone": "live-dj",
    "moving head": "live-dj",
    "par can": "live-dj",
}

def consolidate_category(raw_category_name: str, product_name: str = "") -> str:
    """
    The Router: Takes a raw string and sends it to the correct Tribe ID.
    Ignores brand inputs - pure logic routing.
    """
    if not raw_category_name:
        return "accessories"

    # 1. Normalize
    if not isinstance(raw_category_name, str):
         raw_category_name = str(raw_category_name)
    if not isinstance(product_name, str):
         product_name = str(product_name)

    search_term = f"{raw_category_name} {product_name}".lower()

    # 2. Iterate and Match
    for keyword, tribe_id in SPECTRUM_MAP.items():
        if keyword in search_term:
            return tribe_id
            
    # 3. Fallback
    if "cable" in search_term: return "accessories"
    if "stand" in search_term: return "accessories"
    if "case" in search_term or "bag" in search_term: return "accessories"
    if "power" in search_term: return "accessories"
    
    return "accessories" # The "Lost & Found" bin

# Legacy support / alias to match interface if needed
def get_consolidated_category(cat_id):
    for c in CONSOLIDATED_CATEGORIES:
        if c.id == cat_id:
            return c
    return None

if __name__ == "__main__":
    print("Testing Consolidator...")
    tests = [
        ("Solid Body Electric", "Fender Strat"),
        ("Bass Guitar", "P-Bass"),
        ("V-Drums", "TD-50"),
        ("Synthesizer", "Moog One"),
        ("Cables", "XLR Cable")
    ]
    for cat, prod in tests:
        print(f"{cat} -> {consolidate_category(cat, prod)}")
