"""
Product Normalizer v8.5 — Single Source of Truth

ALL products served to the frontend pass through normalize_product().
This guarantees a clean, flat, predictable shape that maps DIRECTLY
to the frontend's 3-screen architecture (Galaxy → Spectrum → ProductPage).

Key changes from v8:
  - Pre-computes galaxy_id & spectrum_id (no frontend translation needed)
  - Relaxed quality gates: products without price show "Price on request"
  - Products without images get branded placeholders
  - Single flat shape — no nested objects the frontend must decode
  - Pre-computed search text for instant search
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.catalog_validator import validate_product as _validate_product

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# GALAXY / SPECTRUM TAXONOMY — Matches frontend exactly
# ═══════════════════════════════════════════════════════════════════════════

GALAXIES = [
    {
        "id": "guitars-bass",
        "label": "Guitars & Bass",
        "spectrums": [
            {"id": "electric-guitars", "label": "Electric Guitars"},
            {"id": "acoustic-guitars", "label": "Acoustic Guitars"},
            {"id": "bass-guitars", "label": "Bass Guitars"},
            {"id": "guitar-amps", "label": "Amps & Cabinets"},
            {"id": "guitar-pedals", "label": "Pedals & Effects"},
            {"id": "folk-instruments", "label": "Ukulele & Folk"},
            {"id": "guitar-accessories", "label": "Strings, Cables & Care"},
        ],
    },
    {
        "id": "drums-percussion",
        "label": "Drums & Percussion",
        "spectrums": [
            {"id": "acoustic-drums", "label": "Acoustic Kits"},
            {"id": "electronic-drums", "label": "Electronic Drums"},
            {"id": "cymbals", "label": "Cymbals"},
            {"id": "snares", "label": "Snare Drums"},
            {"id": "sticks-heads", "label": "Sticks & Heads"},
            {"id": "percussion", "label": "World Percussion"},
            {"id": "drum-hardware", "label": "Stands & Pedals"},
        ],
    },
    {
        "id": "keys-production",
        "label": "Keys & Production",
        "spectrums": [
            {"id": "synthesizers", "label": "Synthesizers"},
            {"id": "stage-pianos", "label": "Stage Pianos"},
            {"id": "midi-controllers", "label": "MIDI Controllers"},
            {"id": "grooveboxes", "label": "Grooveboxes & Samplers"},
            {"id": "eurorack", "label": "Eurorack & Modular"},
            {"id": "keys-accessories", "label": "Stands & Pedals"},
        ],
    },
    {
        "id": "studio-recording",
        "label": "Studio & Recording",
        "spectrums": [
            {"id": "audio-interfaces", "label": "Audio Interfaces"},
            {"id": "studio-monitors", "label": "Studio Monitors"},
            {"id": "studio-microphones", "label": "Microphones"},
            {"id": "outboard-gear", "label": "Pre-amps & Outboard"},
            {"id": "software-plugins", "label": "Software & Plugins"},
            {"id": "studio-accessories", "label": "Acoustic Treatment & Cables"},
        ],
    },
    {
        "id": "live-dj",
        "label": "Live & DJ",
        "spectrums": [
            {"id": "pa-systems", "label": "PA Speakers"},
            {"id": "live-mixers", "label": "Live Mixers"},
            {"id": "dj-equipment", "label": "DJ Gear"},
            {"id": "lighting", "label": "Stage Lighting"},
            {"id": "live-mics", "label": "Wireless Systems"},
            {"id": "live-accessories", "label": "Stands & Cases"},
        ],
    },
    {
        "id": "accessories-utility",
        "label": "Accessories & Utility",
        "spectrums": [
            {"id": "cables", "label": "All Cables"},
            {"id": "stands", "label": "All Stands"},
            {"id": "cases-bags", "label": "Cases & Bags"},
            {"id": "power-supplies", "label": "Power & Batteries"},
            {"id": "general-accessories", "label": "General Accessories"},
        ],
    },
]

# Build lookup: spectrum_id → galaxy_id
_SPECTRUM_TO_GALAXY: Dict[str, str] = {}
for _g in GALAXIES:
    for _s in _g["spectrums"]:
        _SPECTRUM_TO_GALAXY[_s["id"]] = _g["id"]


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION ENGINE — Maps product → spectrum_id
# ═══════════════════════════════════════════════════════════════════════════

# Backend canonical_category → default spectrum_id
_CATEGORY_TO_SPECTRUM: Dict[str, str] = {
    "keyboards & synthesizers": "synthesizers",
    "drums & percussion": "electronic-drums",
    "audio interfaces & mixers": "audio-interfaces",
    "microphones & recording": "studio-microphones",
    "studio monitors & speakers": "studio-monitors",
    "amplifiers & effects": "guitar-amps",
    "headphones & earphones": "studio-accessories",
    "cables & connectors": "cables",
    "accessories & utility": "general-accessories",
}

# Brand-specific classification patterns (longest match wins)
_BRAND_PATTERNS: Dict[str, List[Tuple[str, str]]] = {
    "roland": [
        ("vad", "electronic-drums"), ("td-",
                                      "electronic-drums"), ("v-drum", "electronic-drums"),
        ("spd", "electronic-drums"), ("handsonic", "electronic-drums"),
        ("juno", "synthesizers"), ("jupiter",
                                   "synthesizers"), ("jd-", "synthesizers"),
        ("jx-", "synthesizers"), ("sh-", "synthesizers"), ("system-", "synthesizers"),
        ("fantom", "synthesizers"), ("fp-",
                                     "stage-pianos"), ("rd-", "stage-pianos"),
        ("rp-", "stage-pianos"), ("rp", "stage-pianos"), ("hp-", "stage-pianos"),
        ("go:piano", "stage-pianos"), ("go:keys", "synthesizers"),
        ("mc-101", "grooveboxes"), ("mc-707",
                                    "grooveboxes"), ("verselab", "grooveboxes"),
        ("tr-", "grooveboxes"), ("sp-", "grooveboxes"), ("aira", "grooveboxes"),
        ("aerophone", "synthesizers"),
        ("cube", "guitar-amps"), ("blues cube",
                                  "guitar-amps"), ("katana", "guitar-amps"),
        ("boss", "guitar-pedals"), ("gt-",
                                    "guitar-pedals"), ("me-", "guitar-pedals"),
        ("rh-", "studio-accessories"),
        ("rcc", "cables"), ("ric", "cables"), ("rmc", "cables"),
        ("cb-", "cases-bags"), ("ksc", "stands"), ("st-", "stands"),
        ("piano", "stage-pianos"), ("keyboard", "synthesizers"),
        ("drum", "electronic-drums"), ("synth", "synthesizers"),
    ],
    "nord": [
        ("grand", "stage-pianos"), ("piano",
                                    "stage-pianos"), ("electro", "stage-pianos"),
        ("stage", "stage-pianos"), ("lead",
                                    "synthesizers"), ("wave", "synthesizers"),
        ("drum", "electronic-drums"),
        ("keyboard", "synthesizers"),
    ],
    "moog": [
        ("mavis", "synthesizers"), ("grandmother",
                                    "synthesizers"), ("matriarch", "synthesizers"),
        ("sub", "synthesizers"), ("minimoog",
                                  "synthesizers"), ("one", "synthesizers"),
        ("voyager", "synthesizers"), ("subsequent",
                                      "synthesizers"), ("dfam", "electronic-drums"),
        ("mother", "synthesizers"), ("minitaur",
                                     "synthesizers"), ("sirin", "synthesizers"),
        ("synth", "synthesizers"),
    ],
    "rode": [
        ("nt", "studio-microphones"), ("ntg",
                                       "studio-microphones"), ("podcaster", "studio-microphones"),
        ("procaster", "studio-microphones"), ("wireless",
                                              "live-mics"), ("ai-1", "audio-interfaces"),
        ("rodecaster", "audio-interfaces"), ("videomic", "studio-microphones"),
        ("lavalier", "live-mics"), ("reporter", "live-mics"),
        ("mic", "studio-microphones"), ("cable", "cables"), ("stand", "stands"),
        ("psa", "stands"), ("windshield", "studio-accessories"),
    ],
    "shure": [
        ("sm7", "studio-microphones"), ("sm57",
                                        "studio-microphones"), ("sm58", "live-mics"),
        ("sm86", "live-mics"), ("beta", "live-mics"), ("ksm", "studio-microphones"),
        ("mv7", "studio-microphones"), ("mv88", "studio-microphones"),
        ("blx", "live-mics"), ("slx", "live-mics"), ("qlx", "live-mics"),
        ("ulx", "live-mics"), ("glx", "live-mics"), ("wireless", "live-mics"),
        ("srh", "studio-accessories"), ("aonic", "studio-accessories"),
        ("se", "studio-accessories"),
        ("mic", "live-mics"),
    ],
    "universal audio": [
        ("apollo", "audio-interfaces"), ("volt",
                                         "audio-interfaces"), ("arrow", "audio-interfaces"),
        ("ox", "guitar-amps"), ("uafx", "guitar-pedals"), ("dream", "guitar-pedals"),
        ("starlight", "guitar-pedals"), ("ruby", "guitar-pedals"),
        ("interface", "audio-interfaces"),
    ],
    "drumdots": [
        ("drum", "acoustic-drums"), ("cymbal",
                                     "cymbals"), ("dot", "acoustic-drums"),
    ],
    "adam audio": [
        ("t5v", "studio-monitors"), ("t7v",
                                     "studio-monitors"), ("t8v", "studio-monitors"),
        ("a7", "studio-monitors"), ("a8",
                                    "studio-monitors"), ("a77", "studio-monitors"),
        ("s2v", "studio-monitors"), ("s3v",
                                     "studio-monitors"), ("s5v", "studio-monitors"),
        ("sub", "studio-monitors"), ("monitor", "studio-monitors"),
    ],
    "akai": [
        ("mpc", "grooveboxes"), ("mpk",
                                 "midi-controllers"), ("mpd", "midi-controllers"),
        ("apc", "dj-equipment"), ("force", "grooveboxes"),
        ("keyboard", "midi-controllers"), ("pad", "midi-controllers"),
    ],
    "alesis": [
        ("surge", "electronic-drums"), ("nitro",
                                        "electronic-drums"), ("crimson", "electronic-drums"),
        ("strike", "electronic-drums"), ("turbo", "electronic-drums"),
        ("recital", "stage-pianos"), ("virtue",
                                      "stage-pianos"), ("concert", "stage-pianos"),
        ("multimix", "audio-interfaces"), ("io", "audio-interfaces"),
        ("elevate", "studio-monitors"), ("m1", "studio-monitors"),
        ("v25", "midi-controllers"), ("vi",
                                      "midi-controllers"), ("q49", "midi-controllers"),
        ("drum", "electronic-drums"), ("piano",
                                       "stage-pianos"), ("keyboard", "midi-controllers"),
    ],
    "arturia": [
        ("minilab", "midi-controllers"), ("keylab",
                                          "midi-controllers"), ("keystep", "midi-controllers"),
        ("minibrute", "synthesizers"), ("microbrute",
                                        "synthesizers"), ("matrixbrute", "synthesizers"),
        ("polybrute", "synthesizers"), ("minifreak",
                                        "synthesizers"), ("microfreak", "synthesizers"),
        ("audiofuse", "audio-interfaces"), ("drumbrute", "grooveboxes"),
        ("synth", "synthesizers"), ("controller", "midi-controllers"),
    ],
}

# Generic keyword → spectrum_id (fallback for unknown brands)
_KEYWORD_SPECTRUM: List[Tuple[str, str]] = [
    ("audio interface", "audio-interfaces"), ("interface", "audio-interfaces"),
    ("studio monitor", "studio-monitors"), ("monitor speaker", "studio-monitors"),
    ("condenser mic", "studio-microphones"), ("ribbon mic", "studio-microphones"),
    ("dynamic mic", "studio-microphones"), ("microphone", "studio-microphones"),
    ("wireless mic", "live-mics"), ("wireless system", "live-mics"),
    ("pa speaker", "pa-systems"), ("powered speaker", "pa-systems"),
    ("live mixer", "live-mixers"), ("mixing console", "live-mixers"),
    ("dj controller", "dj-equipment"), ("turntable", "dj-equipment"),
    ("electric guitar", "electric-guitars"), ("acoustic guitar", "acoustic-guitars"),
    ("bass guitar", "bass-guitars"), ("ukulele", "folk-instruments"),
    ("guitar amp", "guitar-amps"), ("amplifier", "guitar-amps"),
    ("pedal", "guitar-pedals"), ("stompbox",
                                 "guitar-pedals"), ("effect", "guitar-pedals"),
    ("electronic drum", "electronic-drums"), ("e-drum", "electronic-drums"),
    ("v-drum", "electronic-drums"), ("drum kit", "acoustic-drums"),
    ("drum machine", "grooveboxes"), ("groovebox", "grooveboxes"),
    ("sampler", "grooveboxes"), ("sequencer", "grooveboxes"),
    ("synthesizer", "synthesizers"), ("synth", "synthesizers"),
    ("digital piano", "stage-pianos"), ("stage piano", "stage-pianos"),
    ("keyboard", "synthesizers"), ("midi controller", "midi-controllers"),
    ("eurorack", "eurorack"), ("modular", "eurorack"),
    ("cymbal", "cymbals"), ("snare", "snares"), ("drum head", "sticks-heads"),
    ("drumstick", "sticks-heads"), ("cajon",
                                    "percussion"), ("bongo", "percussion"),
    ("headphone", "studio-accessories"), ("earphone", "studio-accessories"),
    ("cable", "cables"), ("connector", "cables"), ("jack", "cables"),
    ("stand", "stands"), ("case", "cases-bags"), ("bag", "cases-bags"),
    ("power supply", "power-supplies"),
    ("piano", "stage-pianos"), ("organ", "synthesizers"),
    ("drum", "electronic-drums"), ("mic", "studio-microphones"),
    ("speaker", "studio-monitors"), ("monitor", "studio-monitors"),
    ("mixer", "live-mixers"), ("preamp", "outboard-gear"),
]

# Brand default spectrum (last resort)
_BRAND_DEFAULT_SPECTRUM: Dict[str, str] = {
    "roland": "synthesizers", "boss": "guitar-pedals", "moog": "synthesizers",
    "nord": "synthesizers", "shure": "live-mics", "rode": "studio-microphones",
    "neumann": "studio-microphones", "focal": "studio-monitors",
    "universal audio": "audio-interfaces", "drumdots": "acoustic-drums",
    "adam audio": "studio-monitors", "akai": "midi-controllers",
    "akai professional": "midi-controllers", "alesis": "electronic-drums",
    "arturia": "midi-controllers", "elektron": "grooveboxes",
    "yamaha": "synthesizers", "korg": "synthesizers",
    "allen heath": "live-mixers", "ampeg": "guitar-amps",
    "amphion": "studio-monitors", "antigua": "folk-instruments",
    "ashdown engineering": "guitar-amps", "asm": "synthesizers",
    # Additional brands from data
    "austrian audio": "studio-microphones", "bespeco": "stands",
    "dynaudio": "studio-monitors", "eve audio": "studio-monitors",
    "encore": "electric-guitars", "eden": "guitar-amps",
    "dixon": "acoustic-drums", "esp": "electric-guitars",
    "dod": "guitar-pedals", "adams": "percussion",
    "bach": "folk-instruments", "cordoba": "acoustic-guitars",
    "dv mark": "guitar-amps", "ebs": "guitar-pedals",
    "egnater": "guitar-amps", "elixir": "guitar-accessories",
    "ernie ball": "guitar-accessories", "eventide": "guitar-pedals",
    "fender": "electric-guitars", "fishman": "guitar-pedals",
    "genelec": "studio-monitors", "gretsch": "electric-guitars",
    "gibson": "electric-guitars", "ibanez": "electric-guitars",
    "jackson": "electric-guitars", "jbl": "pa-systems",
    "kemper": "guitar-amps", "line 6": "guitar-amps",
    "mackie": "live-mixers", "marshall": "guitar-amps",
    "martin": "acoustic-guitars", "mesa boogie": "guitar-amps",
    "motu": "audio-interfaces", "native instruments": "midi-controllers",
    "novation": "midi-controllers", "orange": "guitar-amps",
    "pearl": "acoustic-drums", "pioneer dj": "dj-equipment",
    "presonus": "audio-interfaces", "prs": "electric-guitars",
    "rane": "dj-equipment", "rme": "audio-interfaces",
    "sennheiser": "studio-microphones", "sterling": "electric-guitars",
    "taylor": "acoustic-guitars", "tama": "acoustic-drums",
    "tc electronic": "guitar-pedals", "tc helicon": "live-mics",
    "zildjian": "cymbals", "sabian": "cymbals",
    "zoom": "audio-interfaces", "walrus audio": "guitar-pedals",
    "warm audio": "studio-microphones", "vicfirth": "sticks-heads",
    "vic firth": "sticks-heads", "dw": "acoustic-drums",
    "blackstar": "guitar-amps", "vox": "guitar-amps",
    # Second wave — data-driven additions
    "guild": "acoustic-guitars", "medeli": "stage-pianos",
    "rcf": "pa-systems", "hiwatt": "guitar-amps",
    "spector": "bass-guitars", "heritage audio": "outboard-gear",
    "montarbo": "pa-systems", "xotic": "guitar-pedals",
    "vintage": "electric-guitars", "lynx": "audio-interfaces",
    "topp pro": "pa-systems", "washburn": "acoustic-guitars",
    "remo": "sticks-heads", "xvive": "guitar-pedals",
    "fusion": "cases-bags", "fzone": "guitar-accessories",
    "steinberg": "audio-interfaces", "magma": "cases-bags",
    "show": "lighting", "ultimate support": "stands",
    # Third wave — final stragglers
    "on stage": "stands", "on-stage": "stands",
    "rhythm tech": "folk-instruments", "expressive e": "midi-controllers",
    "tombo": "folk-instruments", "oberheim": "synthesizers",
    "rogers": "acoustic-drums", "sonarworks": "studio-monitors",
    "turkish": "cymbals",
    # Fourth wave — canonical brand name variants
    "allen & heath": "live-mixers",
    "innovative percussion": "sticks-heads",
    "jasmine": "acoustic-guitars",
    "m audio": "audio-interfaces", "m-audio": "audio-interfaces",
    "marimba one": "percussion",
    "maybach": "electric-guitars",
    "mjc ironworks": "snares",
    "playdifferently": "dj-equipment",
    "santos martinez": "acoustic-guitars",
    "sequential": "synthesizers",
}


# Hebrew keyword → spectrum_id mapping (common Hebrew product type prefixes)
_HEBREW_KEYWORD_SPECTRUM: List[Tuple[str, str]] = [
    ("מוניטור אולפני", "studio-monitors"), ("זוג מוניטורים", "studio-monitors"),
    ("סאבוופר אולפני", "studio-monitors"), ("סאבוופר", "studio-monitors"),
    ("מיקרופון", "studio-microphones"), ("מיקרופון אלחוטי", "live-mics"),
    ("אוזניות", "studio-accessories"),
    ("ממשק שמע", "audio-interfaces"), ("כרטיס קול", "audio-interfaces"),
    ("מיקסר", "live-mixers"), ("מיקסר דיגיטלי", "live-mixers"),
    ("סינתיסייזר", "synthesizers"), ("סינת'", "synthesizers"),
    ("פסנתר דיגיטלי", "stage-pianos"), ("פסנתר במה", "stage-pianos"),
    ("פסנתר", "stage-pianos"),
    ("קונטרולר מידי", "midi-controllers"), ("קונטרולר", "midi-controllers"),
    ("סט תופים אלקטרוניים", "electronic-drums"), ("תופים אלקטרוניים", "electronic-drums"),
    ("מכונת תופים", "grooveboxes"), ("סמפלר", "grooveboxes"),
    ("גיטרה חשמלית", "electric-guitars"), ("גיטרה אקוסטית", "acoustic-guitars"),
    ("גיטרה בס", "bass-guitars"), ("בס חשמלי", "bass-guitars"),
    ("מגבר גיטרה", "guitar-amps"), ("מגבר בס", "guitar-amps"),
    ("מגבר", "guitar-amps"),
    ("אפקט", "guitar-pedals"), ("פדל", "guitar-pedals"),
    ("רמקול מוגבר", "pa-systems"), ("רמקול", "pa-systems"),
    ("מצילה", "cymbals"), ("מצילות", "cymbals"),
    ("סנר", "snares"), ("מקלות", "sticks-heads"),
    ("כבל", "cables"), ("מעמד", "stands"), ("סטנד", "stands"),
    ("נרתיק", "cases-bags"), ("תיק", "cases-bags"),
    ("תאורה", "lighting"), ("תאורת במה", "lighting"),
    ("יוקולילי", "folk-instruments"), ("אוקלילי", "folk-instruments"),
]


# ═══════════════════════════════════════════════════════════════════════════
# BRAND NAME NORMALIZATION — Consistent casing & dedup
# ═══════════════════════════════════════════════════════════════════════════

# Canonical display names for brands (lowercase key → proper display name)
_BRAND_CANONICAL_NAMES: Dict[str, str] = {
    "adam audio": "ADAM Audio", "adam-audio": "ADAM Audio",
    "akai": "Akai Professional", "akai professional": "Akai Professional",
    "allen heath": "Allen & Heath", "allen & heath": "Allen & Heath",
    "allen  heath": "Allen & Heath",
    "ampeg": "Ampeg", "amphion": "Amphion", "antigua": "Antigua",
    "arturia": "Arturia", "asm": "ASM", "adams": "Adams",
    "alesis": "Alesis",
    "ashdown engineering": "Ashdown Engineering",
    "audio-technica": "Audio-Technica", "audio technica": "Audio-Technica",
    "austrian audio": "Austrian Audio", "avid": "Avid",
    "behringer": "Behringer", "bespeco": "Bespeco",
    "blackstar": "Blackstar", "boss": "Boss",
    "bohemian ukuleles guitars basses": "Bohemian",
    "breedlove guitars": "Breedlove", "breedlove": "Breedlove",
    "casio": "Casio", "clavia": "Clavia",
    "cordoba guitars": "Cordoba", "cordoba": "Cordoba",
    "denon dj": "Denon DJ", "denon-dj": "Denon DJ",
    "dixon": "Dixon", "drumdots": "DrumDots", "dw": "DW",
    "dynaudio": "Dynaudio",
    "eaw eastern acoustic works": "EAW", "eaw": "EAW",
    "eden": "Eden", "electro-harmonix": "Electro-Harmonix",
    "electro harmonix": "Electro-Harmonix",
    "encore": "Encore", "esp": "ESP",
    "eve audio": "EVE Audio", "eventide": "Eventide",
    "expressive e": "Expressive E",
    "fender": "Fender", "fender studio": "Fender",
    "focusrite": "Focusrite",
    "foxgear guitar effects and pedals": "FoxGear", "foxgear": "FoxGear",
    "fusion": "Fusion", "fzone": "FZone",
    "genelec": "Genelec", "gibson": "Gibson",
    "gon bops percussion": "Gon Bops", "gon bops": "Gon Bops",
    "guild": "Guild",
    "headliner la equipment stands": "Headliner", "headliner": "Headliner",
    "headrush fx": "HeadRush", "headrush": "HeadRush",
    "heritage audio": "Heritage Audio", "hiwatt": "Hiwatt",
    "innovative percussion": "Innovative Percussion",
    "jasmine guitars": "Jasmine", "jasmine": "Jasmine",
    "keith mcmillen instruments kmi": "Keith McMillen", "keith mcmillen": "Keith McMillen",
    "krk systems": "KRK", "krk": "KRK",
    "lag guitars": "LAG Guitars", "lag": "LAG Guitars",
    "lynx": "Lynx",
    "m audio": "M-Audio", "m-audio": "M-Audio",
    "mackie": "Mackie", "magma": "Magma",
    "maestro guitar pedals and effects": "Maestro", "maestro": "Maestro",
    "marimba one": "Marimba One",
    "maton guitars": "Maton", "maton": "Maton",
    "maybach": "Maybach", "medeli": "Medeli",
    "mjc ironworks": "MJC Ironworks",
    "montarbo": "Montarbo", "moog": "Moog",
    "nord": "Nord", "oberheim": "Oberheim",
    "on stage": "On-Stage", "on-stage": "On-Stage",
    "oscar schmidt acoustic guitars": "Oscar Schmidt", "oscar schmidt": "Oscar Schmidt",
    "paiste cymbals": "Paiste", "paiste": "Paiste",
    "pearl": "Pearl",
    "perri s leathers": "Perri's", "perris": "Perri's",
    "playdifferently": "PLAYdifferently",
    "presonus": "PreSonus",
    "rapier 33 electric guitars": "Rapier", "rapier": "Rapier",
    "rcf": "RCF", "regal tip": "Regal Tip",
    "remo": "Remo", "rhythm tech": "Rhythm Tech",
    "rode": "Rode", "rogers": "Rogers", "roland": "Roland",
    "santos martinez": "Santos Martinez",
    "sequential": "Sequential", "show": "Show",
    "shure": "Shure",
    "solar guitars": "Solar Guitars", "solar": "Solar Guitars",
    "sonarworks": "Sonarworks", "spector": "Spector",
    "steinberg": "Steinberg",
    "studio logic": "Studiologic", "studiologic": "Studiologic",
    "tombo": "Tombo", "topp pro": "Topp Pro",
    "turkish": "Turkish",
    "ultimate support": "Ultimate Support",
    "universal audio": "Universal Audio", "universal-audio": "Universal Audio",
    "v moda": "V-MODA", "v-moda": "V-MODA",
    "vintage": "Vintage", "warm audio": "Warm Audio",
    "washburn": "Washburn", "xotic": "Xotic", "xvive": "Xvive",
}


def _normalize_brand_name(raw_brand: str) -> str:
    """Normalize brand name to canonical display form.

    Resolves case inconsistencies, hyphen/space variants, and verbose
    file-name-style brand names (e.g., 'foxgear guitar effects and pedals' → 'FoxGear').
    """
    if not raw_brand:
        return "Unknown"
    key = raw_brand.lower().strip().replace("-", " ").replace("  ", " ")
    # Direct lookup
    if key in _BRAND_CANONICAL_NAMES:
        return _BRAND_CANONICAL_NAMES[key]
    # Try with hyphens replaced
    if raw_brand.lower().strip() in _BRAND_CANONICAL_NAMES:
        return _BRAND_CANONICAL_NAMES[raw_brand.lower().strip()]
    # Fallback: title-case the raw string
    return raw_brand.strip().title() if raw_brand.strip() else "Unknown"


def _brand_dedup_key(brand: str) -> str:
    """Create a dedup key from a brand name (lowercase, no hyphens/spaces)."""
    return brand.lower().strip().replace("-", "").replace(" ", "").replace("&", "")


def _extract_english_name(name: str) -> str:
    """Extract English portion from a Hebrew+English product name."""
    import re
    match = re.search(r'[A-Za-z][\w\s\-\.\/]+', name)
    if match:
        return match.group(0).strip()
    return ""


def classify_product(name: str, brand: str, category: str = "",
                     specs: dict = None) -> Tuple[str, str]:
    """
    Classify product into (spectrum_id, galaxy_id).
    Uses a 5-tier priority system for maximum accuracy.

    Handles Hebrew product names by:
    1. Checking Hebrew keyword prefixes first
    2. Extracting English model name for brand pattern matching
    """
    name_lower = name.lower()
    brand_lower = brand.lower().strip().replace("-", " ")

    # Extract English model name for pattern matching
    english_name = _extract_english_name(name).lower()

    # TIER 0: Hebrew keyword matching (handles "מוניטור אולפני ADAM Audio T5V")
    for hebrew_kw, spectrum_id in _HEBREW_KEYWORD_SPECTRUM:
        if hebrew_kw in name_lower:
            galaxy_id = _SPECTRUM_TO_GALAXY.get(
                spectrum_id, "accessories-utility")
            return spectrum_id, galaxy_id

    # TIER 1: Brand-specific patterns (highest accuracy)
    for brand_key, patterns in _BRAND_PATTERNS.items():
        if brand_key in brand_lower or brand_lower in brand_key:
            # Check both full name and English-only name
            for check_name in [name_lower, english_name]:
                for pattern, spectrum_id in patterns:
                    if pattern in check_name:
                        galaxy_id = _SPECTRUM_TO_GALAXY.get(
                            spectrum_id, "accessories-utility")
                        return spectrum_id, galaxy_id

    # TIER 2: Backend canonical category
    if category and category.lower() not in ("other", "uncategorized", "none", ""):
        spectrum_id = _CATEGORY_TO_SPECTRUM.get(category.lower(), "")
        if spectrum_id:
            galaxy_id = _SPECTRUM_TO_GALAXY.get(
                spectrum_id, "accessories-utility")
            return spectrum_id, galaxy_id

    # TIER 3: Keyword matching on product name + specs
    search_text = f" {name_lower} {english_name} "
    if specs:
        search_text += " ".join(str(v).lower() for v in specs.values()) + " "

    for keyword, spectrum_id in _KEYWORD_SPECTRUM:
        if " " in keyword:
            if keyword in search_text:
                galaxy_id = _SPECTRUM_TO_GALAXY.get(
                    spectrum_id, "accessories-utility")
                return spectrum_id, galaxy_id
        else:
            if f" {keyword} " in search_text or f" {keyword}s " in search_text:
                galaxy_id = _SPECTRUM_TO_GALAXY.get(
                    spectrum_id, "accessories-utility")
                return spectrum_id, galaxy_id

    # TIER 4: Brand default
    default = _BRAND_DEFAULT_SPECTRUM.get(brand_lower, "")
    if not default:
        for bk, sid in _BRAND_DEFAULT_SPECTRUM.items():
            if bk in brand_lower or brand_lower in bk:
                default = sid
                break

    if default:
        galaxy_id = _SPECTRUM_TO_GALAXY.get(default, "accessories-utility")
        return default, galaxy_id

    return "general-accessories", "accessories-utility"


# ═══════════════════════════════════════════════════════════════════════════
# IMAGE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

_PLACEHOLDER_MARKERS = ("placeholder", "brand.com", "example.com", "no-image")


def _is_valid_image(url: Any) -> bool:
    if not url or not isinstance(url, str):
        return False
    return not any(m in url.lower() for m in _PLACEHOLDER_MARKERS)


def _extract_hero_image(p: dict) -> str:
    """Extract best hero image URL from product data."""
    if _is_valid_image(p.get("image_url")):
        return p["image_url"]

    hero = p.get("image_hero")
    if isinstance(hero, dict) and _is_valid_image(hero.get("url")):
        return hero["url"]
    if _is_valid_image(hero):
        return hero

    disp = p.get("display") or {}
    dh = disp.get("hero_image")
    if isinstance(dh, dict) and _is_valid_image(dh.get("url")):
        return dh["url"]
    if _is_valid_image(dh):
        return dh

    for img in (p.get("official_images") or []):
        if isinstance(img, dict) and img.get("display_purpose") == "hero":
            if _is_valid_image(img.get("url")):
                return img["url"]
    for img in (p.get("official_images") or []):
        url = img.get("url") if isinstance(img, dict) else img
        if _is_valid_image(url):
            return url

    for img in (p.get("image_gallery") or []):
        url = img.get("url") if isinstance(img, dict) else img
        if _is_valid_image(url):
            return url

    src = p.get("primary_source") or {}
    if isinstance(src, dict) and _is_valid_image(src.get("image")):
        return src["image"]

    # Skeleton sync / inventory shape uses "thumbnail"
    if _is_valid_image(p.get("thumbnail")):
        return p["thumbnail"]

    return ""


def _collect_gallery(p: dict, hero_url: str) -> List[str]:
    """Collect all valid gallery image URLs, hero first."""
    seen: set = set()
    gallery: List[str] = []

    if hero_url:
        gallery.append(hero_url)
        seen.add(hero_url)

    # Include thumbnail (skeleton/inventory) if not already in gallery
    thumb = p.get("thumbnail")
    if _is_valid_image(thumb) and thumb not in seen:
        gallery.append(thumb)
        seen.add(thumb)

    for src_key in ("image_gallery", "official_images", "gallery_images"):
        for img in (p.get(src_key) or []):
            url = img.get("url") if isinstance(img, dict) else img
            if _is_valid_image(url) and url not in seen:
                gallery.append(url)
                seen.add(url)

    return gallery[:20]


# ═══════════════════════════════════════════════════════════════════════════
# PRICE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

def _extract_price(p: dict) -> float:
    """Extract price from any product shape. Returns 0 if none found."""
    for key in ("price", "price_il"):
        v = p.get(key)
        if v is not None:
            try:
                val = float(v)
                if val > 0:
                    return val
            except (TypeError, ValueError):
                pass

    pricing = p.get("pricing")
    if isinstance(pricing, dict):
        v = pricing.get("price_il")
        if v is not None:
            try:
                val = float(v)
                if val > 0:
                    return val
            except (TypeError, ValueError):
                pass

    return 0.0


def _compute_tier(price: float) -> str:
    if price <= 0:
        return "entry"
    if price < 500:
        return "entry"
    if price < 1500:
        return "mid"
    if price < 4000:
        return "pro"
    return "flagship"


# ═══════════════════════════════════════════════════════════════════════════
# CORE NORMALIZER — Single function, single shape
# ═══════════════════════════════════════════════════════════════════════════

def normalize_product(p: dict, fallback_brand: str = "") -> Optional[dict]:
    """
    Transform any raw product dict into the canonical frontend shape.

    Quality gates (relaxed):
    - Must have an ID
    - Must have a name (non-empty)
    - Price = 0 is OK (shown as "Price on request")
    - No image is OK (gets empty string, frontend handles fallback)
    """
    pid = p.get("id") or p.get("halilit_id") or p.get("sku")
    if not pid:
        return None

    name = (
        p.get("name")
        or p.get("product_name")
        or p.get("official_name")
        or ""
    ).strip()
    if not name:
        return None

    raw_brand = (p.get("brand") or fallback_brand or "Unknown").strip()
    brand = _normalize_brand_name(raw_brand)

    raw_category = (
        p.get("category")
        or (p.get("taxonomy") or {}).get("canonical_category", "")
        or ""
    )
    raw_subcategory = (p.get("taxonomy") or {}).get(
        "canonical_subcategory", "")

    # Specs — merge from multiple sources
    specs: dict = {}
    _META_KEYS = {"specs", "features", "short_description", "long_description",
                  "specs_dict", "specs_source", "specs_completeness", "specs_markdown",
                  "note", "extracted_name"}

    if p.get("official_specs") and isinstance(p["official_specs"], dict):
        for k, v in p["official_specs"].items():
            if k not in _META_KEYS and v:
                specs[k] = v
    if p.get("specifications") and isinstance(p["specifications"], dict):
        for k, v in p["specifications"].items():
            if k not in _META_KEYS and v:
                specs.setdefault(k, v)
    if not specs and isinstance(p.get("specifications"), dict):
        sd = p["specifications"].get("specs_dict")
        if isinstance(sd, dict):
            specs.update(sd)
    # SKU from page scraper
    if p.get("sku") and "sku" not in specs:
        specs["sku"] = p["sku"]
    # Features from page scraper (additionalProperty in JSON-LD)
    page_features = p.get("features")
    if isinstance(page_features, list):
        for feat in page_features:
            if isinstance(feat, dict) and feat.get("name") and feat.get("value"):
                fname = feat["name"].strip()
                fval = feat["value"].strip()
                # Skip "Main Feature" entries — those go into features list, not specs
                if fname.lower() in ("main feature", "feature"):
                    continue
                # Handle duplicate keys by appending index
                if fname in specs:
                    i = 2
                    while f"{fname} {i}" in specs:
                        i += 1
                    specs[f"{fname} {i}"] = fval
                else:
                    specs[fname] = fval

    # Classification
    spectrum_id, galaxy_id = classify_product(name, brand, raw_category, specs)

    # Price
    price = _extract_price(p)
    price_eilat = 0.0
    pe = p.get("price_eilat") or (p.get("pricing") or {}).get("price_eilat", 0)
    try:
        price_eilat = float(pe) if pe else 0.0
    except (TypeError, ValueError):
        price_eilat = 0.0
    if price > 0 and price_eilat <= 0:
        price_eilat = round(price / 1.17, 2)

    tier = _compute_tier(price)

    # Image
    image_url = _extract_hero_image(p)
    image_gallery = _collect_gallery(p, image_url)

    # Description — filter out placeholder descriptions
    _PLACEHOLDER_DESCRIPTIONS = (
        "the ultimate stage piano for professionals",
        "no description available",
    )

    def _is_real_desc(d: str) -> bool:
        if not d or len(d.strip()) < 10:
            return False
        return d.strip().lower() not in _PLACEHOLDER_DESCRIPTIONS

    raw_desc = p.get("official_description") or ""
    if not _is_real_desc(raw_desc):
        raw_desc = p.get("description_long") or ""
    if not _is_real_desc(raw_desc):
        raw_desc = p.get("description") or ""
    if not _is_real_desc(raw_desc):
        raw_desc = p.get("page_description") or ""
    if not _is_real_desc(raw_desc):
        raw_desc = p.get("description_short") or ""
    if not _is_real_desc(raw_desc):
        raw_desc = ""
    description = raw_desc.strip()

    raw_short = p.get("description_short") or ""
    if not _is_real_desc(raw_short):
        raw_short = ""
    description_short = (
        raw_short
        or (description[:200] + "..." if len(description) > 200 else description)
        or ""
    )

    # Features — merge from multiple sources
    features = []
    raw_features = p.get("feature_list") or []
    if not raw_features:
        spec_features = (p.get("specifications") or {}).get("features")
        if isinstance(spec_features, list):
            raw_features = spec_features
    # Also extract from page scraper JSON-LD features (these are name:value pairs)
    if not raw_features and isinstance(p.get("features"), list):
        for feat in p["features"]:
            if isinstance(feat, str):
                raw_features.append(feat)
            elif isinstance(feat, dict) and feat.get("name"):
                raw_features.append(f"{feat['name']}: {feat.get('value', '')}")
    features = [f for f in raw_features if isinstance(
        f, str) and f.strip()][:20]

    # FAQ from page scraper
    faq = p.get("faq") or []
    if isinstance(faq, list) and faq:
        faq = [q for q in faq if isinstance(
            q, dict) and q.get("question")][:10]
    else:
        faq = []

    # Reviews — combine from review_data, top-level contextual fields, and contextual_data blob
    review_data = p.get("review_data") or {}
    rating = review_data.get("aggregate_rating") or p.get(
        "average_rating") or 0
    review_count = review_data.get(
        "total_reviews") or len(p.get("reviews") or [])
    pros = list(review_data.get("pros_and_cons", {}).get("pros") or [])
    cons = list(review_data.get("pros_and_cons", {}).get("cons") or [])
    # Merge contextual pillar fields (review_pros, review_cons) so all sources are combined
    for x in (p.get("review_pros") or []):
        if isinstance(x, str) and x.strip() and x.strip() not in pros:
            pros.append(x.strip())
    for x in (p.get("review_cons") or []):
        if isinstance(x, str) and x.strip() and x.strip() not in cons:
            cons.append(x.strip())
    ctx_data = p.get("contextual_data") or {}
    if isinstance(ctx_data, dict):
        for x in (ctx_data.get("review_pros") or []):
            if isinstance(x, str) and x.strip() and x.strip() not in pros:
                pros.append(x.strip())
        for x in (ctx_data.get("review_cons") or []):
            if isinstance(x, str) and x.strip() and x.strip() not in cons:
                cons.append(x.strip())
        if not rating and ctx_data.get("average_rating"):
            try:
                rating = float(ctx_data["average_rating"])
            except (TypeError, ValueError):
                pass
        if not review_count and (ctx_data.get("reviews") or ctx_data.get("review_sources")):
            review_count = len(ctx_data.get("reviews") or []) or len(ctx_data.get("review_sources") or [])

    # Quality score — use smart validator that scores on what the UI renders
    # (computed after the full dict is built, see below)

    # Brand logo
    brand_slug = brand.lower().replace(" ", "-")
    brand_logo = f"/assets/logos/{brand_slug}_logo.png"

    # Halilit URL
    halilit_url = p.get("halilit_url") or p.get("source_url") or ""

    # Official manufacturer URL
    official_url = p.get("official_url") or ""

    # Audiences (from Halilit page JSON-LD)
    audiences = p.get("audiences") or []
    if isinstance(audiences, list):
        audiences = [a for a in audiences if isinstance(
            a, str) and a.strip()][:5]
    else:
        audiences = []

    # Contextual data — third data pillar (reviews, community insights)
    contextual_data = p.get("contextual_data") or {}
    if not isinstance(contextual_data, dict):
        contextual_data = {}
    # Merge in any review synthesis available (dict or string)
    if p.get("review_synthesis"):
        rs = p["review_synthesis"]
        if isinstance(rs, dict) and "review_synthesis" not in contextual_data:
            contextual_data.setdefault("review_synthesis", rs)
        elif isinstance(rs, str) and rs.strip():
            contextual_data.setdefault("review_synthesis", {"summary": rs})
    # Flatten for UI: summary text, real-world insights, review sources
    review_synthesis_summary = ""
    if isinstance(contextual_data.get("review_synthesis"), dict):
        rs = contextual_data["review_synthesis"]
        review_synthesis_summary = (rs.get("summary") or rs.get("text") or "").strip() if isinstance(rs, dict) else ""
    elif isinstance(contextual_data.get("review_synthesis"), str):
        review_synthesis_summary = (contextual_data["review_synthesis"] or "").strip()
    real_world_insights = list(p.get("real_world_insights") or [])
    if isinstance(contextual_data.get("real_world_insights"), list):
        for i in contextual_data["real_world_insights"]:
            if isinstance(i, str) and i.strip() and i.strip() not in real_world_insights:
                real_world_insights.append(i.strip())
    review_sources = list(p.get("review_sources") or [])
    if isinstance(contextual_data.get("review_sources"), list):
        for s in contextual_data["review_sources"]:
            if isinstance(s, str) and s.strip() and s.strip() not in review_sources:
                review_sources.append(s.strip())

    # Per source_rules: official only when we have real official-scout data
    has_official_specs = bool(
        p.get("official_specs")
        and isinstance(p["official_specs"], dict)
        and any(v for v in (p["official_specs"] or {}).values() if v)
    )

    # Sources — clearly track the three pillars
    sources = p.get("sources") or []
    if not sources:
        sources = []
        if halilit_url:
            sources.append("halilit")
        if official_url or has_official_specs or _is_real_desc(
            (p.get("official_description") or "")
        ):
            sources.append("official")
        if contextual_data or rating > 0 or pros or cons:
            sources.append("contextual")
        if not sources:
            sources = ["halilit"]

    # Data trust — provenance per field (app rules)
    data_trust = {
        "price_source": "halilit" if price > 0 else "none",
        "specs_source": "official" if has_official_specs else ("halilit" if specs else "none"),
        "description_source": "official" if _is_real_desc(p.get("official_description") or "") else ("halilit" if description else "none"),
        "image_source": "halilit" if image_url and "halilit" in image_url else ("official" if image_url else "none"),
        "review_source": "contextual" if rating > 0 else "none",
    }

    # Pre-computed search text
    search_text = f"{name} {brand} {raw_category} {raw_subcategory} {description_short}".lower()

    product_dict = {
        "id": str(pid),
        "name": name,
        "brand": brand,
        "brand_logo": brand_logo,
        "galaxy_id": galaxy_id,
        "spectrum_id": spectrum_id,
        "category": raw_category or galaxy_id,
        "subcategory": raw_subcategory,
        "price": price,
        "price_eilat": price_eilat,
        "currency": "ILS",
        "tier": tier,
        "market_price_estimate": 0,
        "market_price_peers": 0,
        "image_url": image_url,
        "image_gallery": image_gallery,
        "description": description,
        "description_short": description_short,
        "specs": specs,
        "features": features,
        "faq": faq,
        "audiences": audiences,
        "rating": float(rating) if rating else 0,
        "review_count": int(review_count) if review_count else 0,
        "pros": pros,
        "cons": cons,
        "contextual_data": contextual_data,
        "review_synthesis_summary": review_synthesis_summary,
        "real_world_insights": real_world_insights,
        "review_sources": review_sources,
        "quality_score": 0,  # computed below
        "data_status": "MINIMAL",  # computed below
        "data_missing": [],  # computed below
        "halilit_url": halilit_url,
        "official_url": official_url,
        "sources": sources,
        "data_trust": data_trust,
        "search_text": search_text,
    }

    # Smart quality scoring — scores on what the UI actually renders
    validation = _validate_product(product_dict)
    product_dict["quality_score"] = validation["score"]
    product_dict["data_status"] = validation["status"]
    product_dict["data_missing"] = validation["missing"]

    return product_dict


# ═══════════════════════════════════════════════════════════════════════════
# CATALOG BUILDER — Returns pre-indexed catalog for instant frontend use
# ═══════════════════════════════════════════════════════════════════════════

# Feature flag — set ENABLE_PRODUCT_GRAPH=true to activate family/relationship discovery
ENABLE_PRODUCT_GRAPH = os.environ.get(
    "ENABLE_PRODUCT_GRAPH", "true").lower() in ("1", "true", "yes")


def build_catalog(data_dir: str, resolve: bool = True) -> dict:
    """
    Read all brand JSON files, normalize every product, optionally resolve
    missing data, and return a pre-indexed catalog with health metrics.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return _empty_catalog()

    excluded = {"index.json", "search_index.json", "search_index_min.json",
                "galaxy_db.json", "package.json"}

    products_map: Dict[str, dict] = {}
    # Dedup by English model name within same brand to catch
    # duplicates across variant files (e.g., "adam audio.json" + "adam-audio.json")
    brand_model_map: Dict[str, str] = {}  # brand+model -> first product id
    brands_found: set = set()

    for json_file in sorted(data_path.glob("*.json")):
        if json_file.name in excluded:
            continue

        try:
            with open(json_file, "r") as f:
                file_data = json.load(f)

            raw_products = (
                file_data if isinstance(file_data, list)
                else file_data.get("products", []) if isinstance(file_data, dict)
                else []
            )

            for raw in raw_products:
                product = normalize_product(raw, fallback_brand=json_file.stem)
                if not product:
                    continue

                # Dedup: check for same brand + English model name
                eng_model = _extract_english_name(
                    product["name"]).lower().strip()
                brand_key = _brand_dedup_key(product["brand"])
                dedup_key = f"{brand_key}::{eng_model}" if eng_model else ""

                if dedup_key and dedup_key in brand_model_map:
                    # Merge: keep whichever has higher quality, but merge missing fields
                    existing_id = brand_model_map[dedup_key]
                    if existing_id in products_map:
                        existing = products_map[existing_id]
                        if product["quality_score"] > existing["quality_score"]:
                            # New one is better — use it but keep any data the old one had
                            if not product["image_url"] and existing["image_url"]:
                                product["image_url"] = existing["image_url"]
                            if not product["description"] and existing["description"]:
                                product["description"] = existing["description"]
                            if not product["specs"] and existing["specs"]:
                                product["specs"] = existing["specs"]
                            products_map[existing_id] = product
                        else:
                            # Existing is better — merge any new data into it
                            if not existing["image_url"] and product["image_url"]:
                                existing["image_url"] = product["image_url"]
                            if not existing["description"] and product["description"]:
                                existing["description"] = product["description"]
                            if not existing["specs"] and product["specs"]:
                                existing["specs"] = product["specs"]
                        continue

                if product["id"] not in products_map:
                    products_map[product["id"]] = product
                    if dedup_key:
                        brand_model_map[dedup_key] = product["id"]
                    brands_found.add(product["brand"])
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")

    products = list(products_map.values())

    # Smart resolution — auto-fill missing data using peer heuristics
    if resolve and products:
        from backend.catalog_validator import resolve_catalog, validate_catalog
        products, resolve_summary = resolve_catalog(products)
        logger.info(
            f"Resolver: improved {resolve_summary['products_improved']} products "
            f"with {resolve_summary['total_changes']} changes"
        )

    # Sort: products with price & image first, then by quality
    products.sort(key=lambda p: (
        -(1 if p["price"] > 0 else 0),
        -(1 if p["image_url"] else 0),
        -p["quality_score"],
    ))

    # ── Product Graph: Family & Relationship Discovery ──
    graph_indexes = {}
    graph_stats = {}
    families_meta = {}  # family_id → {family_name, brand, series, hero_image, variant_count}
    if ENABLE_PRODUCT_GRAPH:
        try:
            from backend.product_graph import ProductGraph
            from backend.product_graph_store import get_graph_store
            # Build graph from flat products
            graph = ProductGraph.from_flat_products(products)

            # Load persisted families/relationships (curated data survives rebuilds)
            store = get_graph_store()
            has_snapshot = store.has_json_snapshot()
            graph = store.load_graph_overlay(graph)

            # CRITICAL: Skip expensive discovery on every load — use cached graph for instant startup.
            # Discovery only runs on explicit GET /api/conductor/refresh.
            if not has_snapshot:
                logger.warning(
                    "⚠️  Graph snapshot not found. Starting with EMPTY graph for fast load."
                )
                logger.warning(
                    "👉 Call GET /api/conductor/refresh to trigger full relationship discovery."
                )
            else:
                # Snapshot exists — use cached families/relationships, skip re-discovery.
                # sync_relationship_ids_to_products populates each product from loaded graph edges.
                graph.sync_relationship_ids_to_products()

            # Merge graph data back into flat products (family + variant + relationship_ids)
            for i, p in enumerate(products):
                pid = p["id"]
                if pid in graph.products:
                    cp = graph.products[pid]
                    p["family_id"] = cp.family_id
                    p["variant_key"] = cp.variant.variant_key if cp.variant else None
                    p["variant_is_default"] = cp.variant.is_default if cp.variant else None
                    p["relationship_ids"] = list(cp.relationship_ids)

            # Build graph-specific indexes
            product_id_to_idx = {p["id"]: i for i, p in enumerate(products)}
            graph_indexes = graph.to_catalog_indexes(product_id_to_idx)
            graph_stats = graph.get_graph_stats()

            # Serialize family metadata for frontend
            for fam_id, fam in graph.families.items():
                families_meta[fam_id] = {
                    "id": fam.id,
                    "family_name": fam.family_name,
                    "brand": fam.brand,
                    "series": fam.series,
                    "hero_image": fam.hero_image,
                    "variant_count": len(fam.variant_ids),
                }

            logger.info(
                f"Product graph: {graph_stats.get('total_families', 0)} families, "
                f"{graph_stats.get('total_relationships', 0)} relationships, "
                f"{graph_stats.get('products_in_families', 0)} products in families"
            )
        except Exception as e:
            logger.warning(f"Product graph discovery failed (non-fatal): {e}")
            graph_indexes = {"by_family": {}, "relationships": {}}
            graph_stats = {}
            for p in products:
                p.setdefault("relationship_ids", [])

    else:
        # Graph disabled — add empty fields for consistent shape
        for p in products:
            p["family_id"] = None
            p["variant_key"] = None
            p["variant_is_default"] = None
            p["relationship_ids"] = []

    # Build indexes
    by_galaxy: Dict[str, List[int]] = {}
    by_spectrum: Dict[str, List[int]] = {}
    by_brand: Dict[str, List[int]] = {}
    galaxy_counts: Dict[str, int] = {}
    spectrum_counts: Dict[str, int] = {}
    brand_counts: Dict[str, int] = {}

    for idx, p in enumerate(products):
        gid = p["galaxy_id"]
        sid = p["spectrum_id"]
        b = p["brand"].lower()

        by_galaxy.setdefault(gid, []).append(idx)
        by_spectrum.setdefault(sid, []).append(idx)
        by_brand.setdefault(b, []).append(idx)

        galaxy_counts[gid] = galaxy_counts.get(gid, 0) + 1
        spectrum_counts[sid] = spectrum_counts.get(sid, 0) + 1
        brand_counts[b] = brand_counts.get(b, 0) + 1

    # Catalog health metrics
    from backend.catalog_validator import validate_catalog as _validate_catalog
    health = _validate_catalog(products)

    metadata = {
        "total_products": len(products),
        "brands": sorted(brands_found),
        "galaxy_counts": galaxy_counts,
        "spectrum_counts": spectrum_counts,
        "brand_counts": brand_counts,
        "galaxies": GALAXIES,
        "source": "conductor_v10",
        "cache_ttl_seconds": 300,
        # Health metrics for the UI
        "health_score": health["health_score"],
        "health_status": health["health_status"],
        "status_counts": health["status_counts"],
        "field_coverage": health["field_coverage"],
        "top_issues": health["top_issues"][:5],
        # Product graph metrics
        "graph_stats": graph_stats,
    }

    logger.info(
        f"Catalog built: {len(products)} products, {len(brands_found)} brands, "
        f"{len(galaxy_counts)} galaxies, {len(spectrum_counts)} spectrums"
    )

    # Merge graph indexes with standard indexes
    all_indexes = {
        "by_galaxy": by_galaxy,
        "by_spectrum": by_spectrum,
        "by_brand": by_brand,
    }
    if graph_indexes:
        all_indexes["by_family"] = graph_indexes.get("by_family", {})
        all_indexes["relationships"] = graph_indexes.get("relationships", {})

    return {
        "products": products,
        "indexes": all_indexes,
        "metadata": metadata,
        "families": families_meta,
    }


def _empty_catalog() -> dict:
    return {
        "products": [],
        "indexes": {
            "by_galaxy": {}, "by_spectrum": {}, "by_brand": {},
            "by_family": {}, "relationships": {},
        },
        "metadata": {
            "total_products": 0, "brands": [], "galaxy_counts": {},
            "spectrum_counts": {}, "brand_counts": {}, "galaxies": GALAXIES,
            "source": "conductor_v10", "cache_ttl_seconds": 300,
            "graph_stats": {},
        },
        "families": {},
    }
