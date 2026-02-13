"""
Model Grouper — Extracts model identity from product names and groups variations.

Given: "ESP LTD EC 256VGS Electric Guitar" → model="LTD EC-256", variation="VGS"
Given: "ESP LTD EC 256FM Electric Guitar"  → model="LTD EC-256", variation="FM"

This powers the Track/Subtrack view in the redesigned Spectrum Module.
Products are grouped into ModelGroups, classified by instrument family,
and served at different zoom levels.
"""

import re
from collections import defaultdict
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN-DRIVEN INSTRUMENT FAMILIES
# ═══════════════════════════════════════════════════════════════════════════
# These replace the generic "electric-guitars" categories with musician-
# centric families: Guitars (all 6-string), Bass (all bass), Amps, etc.

INSTRUMENT_FAMILIES: dict[str, dict[str, Any]] = {
    "guitars": {
        "label": "Guitars",
        "icon": "guitar",
        "keywords": ["guitar", "guitarra", "gitarre"],
        "exclude_keywords": ["bass guitar", "bass guitarra"],
        "sub_categories": {
            "electric": {
                "label": "Electric Guitars",
                "keywords": ["electric guitar", "e-guitar", "electric solid"],
                "body_types": {
                    "lp_type": ["les paul", " lp ", "lp-", "ec-", "ec ", "single cut", "singlecut"],
                    "strat_type": ["strat", "st-", "s-type", "stratocaster"],
                    "sg_type": [" sg ", "sg-", "double cutaway"],
                    "tele_type": ["tele", "tl-", "t-type", "telecaster"],
                    "offset": ["jazzmaster", "jaguar", "mustang", "offset"],
                    "metal": ["flying v", "explorer", "warlock", "v-type", "rhoads", "kelly", "king v", "warrior"],
                    "hollow_semi": ["hollow", "semi-hollow", "335", "339", "casino", "archtop", "jazz box"],
                    "superstrat": ["superstrat", "dinky", "soloist", "rg ", "rg-", "jem", "ibanez rg"],
                    "7_string": ["7-string", "7 string", "seven string"],
                    "8_string": ["8-string", "8 string", "eight string"],
                },
            },
            "acoustic": {
                "label": "Acoustic Guitars",
                "keywords": ["acoustic guitar", "folk guitar", "western guitar"],
                "body_types": {
                    "dreadnought": ["dreadnought", "dread"],
                    "folk": ["folk", "000", " om ", "orchestra model"],
                    "jumbo": ["jumbo"],
                    "parlor": ["parlor", "parlour"],
                    "concert": ["concert", "grand concert"],
                    "grand_auditorium": ["grand auditorium", " ga ", "ga-"],
                    "cutaway_electro": ["cutaway", "electro acoustic", "electro-acoustic", " ce ", "ce-"],
                    "12_string": ["12-string", "12 string", "twelve string"],
                },
            },
            "classical": {
                "label": "Classical Guitars",
                "keywords": ["classical", "nylon", "spanish guitar", "flamenco"],
                "body_types": {
                    "full_size": ["4/4", "full size"],
                    "three_quarter": ["3/4"],
                    "half": ["1/2"],
                    "quarter": ["1/4"],
                    "flamenco": ["flamenco"],
                },
            },
            "travel": {
                "label": "Travel & Mini",
                "keywords": ["travel guitar", "mini guitar", "backpacker", "baby taylor"],
                "body_types": {},
            },
        },
    },
    "bass": {
        "label": "Bass",
        "icon": "bass",
        "keywords": ["bass"],
        "exclude_keywords": [],
        "sub_categories": {
            "electric_bass": {
                "label": "Electric Bass",
                "keywords": ["bass guitar", "electric bass", "e-bass", "bass "],
                "body_types": {
                    "4_string": ["4-string", "4 string", "four string"],
                    "5_string": ["5-string", "5 string", "five string"],
                    "6_string": ["6-string bass", "6 string bass"],
                    "short_scale": ["short scale"],
                    "jazz_bass": ["jazz bass", "jb-", "j-bass", "j bass"],
                    "precision": ["precision", "pb-", "p-bass", "p bass"],
                    "active": ["active bass", "active pickup"],
                },
            },
            "acoustic_bass": {
                "label": "Acoustic Bass",
                "keywords": ["acoustic bass"],
                "body_types": {},
            },
        },
    },
    "amps_effects": {
        "label": "Amps & Effects",
        "icon": "amp",
        "keywords": ["amp", "amplifier", "combo amp", "pedal", "effect", "stompbox"],
        "exclude_keywords": [],
        "sub_categories": {
            "guitar_amps": {
                "label": "Guitar Amps",
                "keywords": ["guitar amp", "combo amp", "tube amp", "guitar amplifier", "valve amp"],
                "body_types": {
                    "combo": ["combo"],
                    "head": ["amp head", "head "],
                    "cabinet": ["cabinet", " cab ", "speaker cab"],
                    "practice": ["practice", "mini amp", "micro amp"],
                    "modelling": ["modelling", "modeling", "digital amp"],
                },
            },
            "bass_amps": {
                "label": "Bass Amps",
                "keywords": ["bass amp", "bass combo", "bass amplifier"],
                "body_types": {},
            },
            "effects_pedals": {
                "label": "Effects Pedals",
                "keywords": ["pedal", "effect", "stompbox", "multi-fx", "processor"],
                "body_types": {
                    "overdrive_dist": ["overdrive", "distortion", "fuzz", "boost", "drive"],
                    "modulation": ["chorus", "flanger", "phaser", "tremolo", "vibrato", "rotary"],
                    "delay_reverb": ["delay", "reverb", "echo", "shimmer"],
                    "multi_fx": ["multi-fx", "multi fx", "processor", "multi-effect"],
                    "tuner": ["tuner", "tuning pedal"],
                    "wah_filter": ["wah", "auto-wah", "envelope filter"],
                    "looper": ["looper", "loop station", "loop pedal"],
                    "compressor": ["compressor", "comp pedal"],
                },
            },
        },
    },
    "drums_percussion": {
        "label": "Drums & Percussion",
        "icon": "drums",
        "keywords": [
            "drum", "percussion", "cymbal", "snare", "kick", "bongo",
            "djembe", "cajon", "cajón", "tambourine", "triangle",
            "shaker", "maracas", "xylophone", "glockenspiel",
            "metallophone", "conga",
        ],
        "exclude_keywords": [],
        "sub_categories": {
            "drum_kits": {
                "label": "Drum Kits",
                "keywords": ["drum kit", "drum set", "shell pack", "drum kit", "drumset"],
                "body_types": {
                    "acoustic_kit": ["acoustic drum", "shell pack"],
                    "electronic_kit": ["electronic drum", "e-drum", "electric drum", "mesh pad"],
                    "junior_kit": ["junior", "kid", "child"],
                },
            },
            "cymbals": {
                "label": "Cymbals",
                "keywords": ["cymbal", "hi-hat", "crash", "ride", "splash", "china"],
                "body_types": {},
            },
            "hand_percussion": {
                "label": "Hand Percussion",
                "keywords": ["bongo", "djembe", "cajon", "cajón", "conga", "hand drum"],
                "body_types": {},
            },
            "small_percussion": {
                "label": "Small Percussion",
                "keywords": [
                    "tambourine", "triangle", "shaker", "maracas",
                    "claves", "guiro", "woodblock", "castanets",
                    "egg shaker", "cabasa", "bell",
                ],
                "body_types": {},
            },
            "mallet_instruments": {
                "label": "Mallet Instruments",
                "keywords": ["xylophone", "glockenspiel", "metallophone", "vibraphone", "marimba", "chime"],
                "body_types": {},
            },
            "drum_hardware": {
                "label": "Hardware & Heads",
                "keywords": ["drum stand", "cymbal stand", "drum throne", "kick pedal", "drum head", "drum stick"],
                "body_types": {},
            },
        },
    },
    "keys_production": {
        "label": "Keys & Production",
        "icon": "keyboard",
        "keywords": ["keyboard", "piano", "synthesizer", "synth", "midi", "controller"],
        "exclude_keywords": [],
        "sub_categories": {
            "keyboards_pianos": {
                "label": "Keyboards & Pianos",
                "keywords": ["keyboard", "piano", "digital piano", "stage piano", "portable keyboard"],
                "body_types": {
                    "digital_piano": ["digital piano"],
                    "stage_piano": ["stage piano"],
                    "portable": ["portable keyboard", "arranger"],
                    "weighted": ["weighted", "hammer action"],
                },
            },
            "synthesizers": {
                "label": "Synthesizers",
                "keywords": ["synthesizer", "synth", "analog synth", "digital synth"],
                "body_types": {},
            },
            "midi_controllers": {
                "label": "MIDI Controllers",
                "keywords": ["midi controller", "midi keyboard", "pad controller"],
                "body_types": {},
            },
            "grooveboxes": {
                "label": "Grooveboxes & Samplers",
                "keywords": ["groovebox", "sampler", "drum machine", "sequencer"],
                "body_types": {},
            },
        },
    },
    "studio_recording": {
        "label": "Studio & Recording",
        "icon": "mic",
        "keywords": ["interface", "monitor", "microphone", "mic ", "headphone", "studio", "recording"],
        "exclude_keywords": [],
        "sub_categories": {
            "audio_interfaces": {
                "label": "Audio Interfaces",
                "keywords": ["audio interface", "sound card", "usb interface"],
                "body_types": {},
            },
            "studio_monitors": {
                "label": "Studio Monitors",
                "keywords": ["studio monitor", "monitor speaker", "nearfield"],
                "body_types": {},
            },
            "microphones": {
                "label": "Microphones",
                "keywords": ["microphone", "condenser mic", "dynamic mic", "ribbon mic"],
                "body_types": {},
            },
            "headphones": {
                "label": "Headphones",
                "keywords": ["headphone", "earphone", "in-ear", "iem"],
                "body_types": {},
            },
        },
    },
    "live_pa": {
        "label": "Live & PA",
        "icon": "speaker",
        "keywords": ["pa ", "pa-", "speaker", "mixer", "live sound", "wireless"],
        "exclude_keywords": ["studio monitor"],
        "sub_categories": {
            "pa_speakers": {
                "label": "PA Speakers",
                "keywords": ["pa speaker", "powered speaker", "passive speaker", "subwoofer"],
                "body_types": {},
            },
            "mixers": {
                "label": "Mixers",
                "keywords": ["mixer", "mixing console", "analog mixer", "digital mixer"],
                "body_types": {},
            },
            "wireless_systems": {
                "label": "Wireless Systems",
                "keywords": ["wireless", "wireless mic", "wireless guitar", "bodypack"],
                "body_types": {},
            },
        },
    },
    "accessories": {
        "label": "Accessories",
        "icon": "wrench",
        "keywords": ["string", "pick", "capo", "strap", "case", "bag", "stand", "cable", "tuner"],
        "exclude_keywords": [],
        "sub_categories": {
            "guitar_strings": {
                "label": "Guitar Strings",
                "keywords": ["guitar string", "electric string", "acoustic string", "nylon string"],
                "body_types": {},
            },
            "bass_strings": {
                "label": "Bass Strings",
                "keywords": ["bass string"],
                "body_types": {},
            },
            "picks_plectrums": {
                "label": "Picks",
                "keywords": ["pick", "plectrum"],
                "body_types": {},
            },
            "cases_bags": {
                "label": "Cases & Bags",
                "keywords": ["case", "bag", "gig bag", "hard case", "softcase"],
                "body_types": {},
            },
            "stands_hangers": {
                "label": "Stands & Hangers",
                "keywords": ["stand", "hanger", "wall mount", "guitar stand"],
                "body_types": {},
            },
            "cables": {
                "label": "Cables",
                "keywords": ["cable", "instrument cable", "patch cable", "speaker cable"],
                "body_types": {},
            },
            "other_accessories": {
                "label": "Other Accessories",
                "keywords": ["capo", "strap", "tuner", "slide", "metronome", "music stand"],
                "body_types": {},
            },
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# MODEL IDENTITY EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

# Category words to strip from product names (longest first for greedy match)
_CATEGORY_SUFFIXES = sorted([
    "electric guitar", "acoustic guitar", "classical guitar",
    "bass guitar", "electric bass", "guitar", "bass",
    "combo amp", "amplifier", "amp", "pedal",
    "drum kit", "drum set", "cymbal", "keyboard", "piano",
    "synthesizer", "microphone", "headphone", "monitor",
    "audio interface",
], key=len, reverse=True)


def extract_model_identity(product_name: str, brand: str) -> dict[str, str]:
    """
    Extracts the canonical model name and variation suffix from a product name.

    Strategy:
    1. Remove the brand name prefix
    2. Remove generic category words (e.g., "Electric Guitar")
    3. Identify the model number/series (letters + numbers)
    4. Everything after the model = variation (finish, color, config)

    Returns: {"model": "LTD EC-256", "variation": "VGS", "raw": original}
    """
    name = product_name.strip()
    raw = name

    # Remove brand prefix (case-insensitive)
    if brand:
        brand_lower = brand.lower()
        name_lower = name.lower()
        if name_lower.startswith(brand_lower):
            name = name[len(brand):].strip()
        # Also try without spaces/hyphens
        brand_compact = brand_lower.replace(" ", "").replace("-", "")
        name_compact_start = name_lower[:len(
            brand_compact) + 2].replace(" ", "").replace("-", "")
        if name_compact_start.startswith(brand_compact) and not name_lower.startswith(brand_lower):
            # Find how many original chars to remove
            chars_consumed = 0
            compact_idx = 0
            for ch in name_lower:
                if compact_idx >= len(brand_compact):
                    break
                if ch in (' ', '-'):
                    chars_consumed += 1
                    continue
                if ch == brand_compact[compact_idx]:
                    compact_idx += 1
                    chars_consumed += 1
                else:
                    break
            if compact_idx == len(brand_compact):
                name = name[chars_consumed:].strip()

    # Remove category descriptors from anywhere in the name
    # This handles both trailing ("FG800 Acoustic Guitar") and mid-name
    # ("Oil Can Bass Guitar Moonshine") patterns.
    # When found mid-name: text before = model series, text after = variation hint
    name_compressed = name
    _category_variation_hint = ""
    for suffix in _CATEGORY_SUFFIXES:
        idx = name_compressed.lower().find(suffix)
        if idx >= 0:
            before = name_compressed[:idx].strip()
            after = name_compressed[idx + len(suffix):].strip()
            if before:
                _category_variation_hint = after  # potential variation
                name_compressed = before
            elif after:
                # Category word at start, e.g. "Electric Guitar FG800"
                name_compressed = after
            break

    # Also strip leading articles
    for prefix in ("the ", "a "):
        if name_compressed.lower().startswith(prefix):
            name_compressed = name_compressed[len(prefix):]

    if not name_compressed:
        name_compressed = name  # Don't leave empty

    # Now parse model vs. variation
    # Pattern: "LTD EC 256VGS" → model="LTD EC-256", variation="VGS"
    # Pattern: "Viper 256 FM" → model="Viper-256", variation="FM"

    # Find the core model: everything up to and including the first number sequence
    model_match = re.match(
        r'^(.*?\b\d+(?:\.\d+)?)\s*(.*?)$',
        name_compressed,
        re.IGNORECASE,
    )

    if model_match:
        model_core = model_match.group(1).strip()
        variation = model_match.group(2).strip()

        # Separate letters stuck after numbers: "256VGS" → "256", "VGS"
        inner_match = re.match(r'^(.*\d)([A-Za-z]{2,}.*)$', model_core)
        if inner_match:
            model_core = inner_match.group(1).strip()
            variation = (inner_match.group(2) + " " + variation).strip()

        # Normalize model: collapse multiple spaces
        model_core = re.sub(r'\s+', ' ', model_core).strip()

        return {
            "model": f"{brand} {model_core}".strip() if brand else model_core,
            "variation": variation if variation else "Standard",
            "raw": raw,
        }

    # No number found — use category variation hint if available
    variation = _category_variation_hint if _category_variation_hint else "Standard"
    return {
        "model": f"{brand} {name_compressed}".strip() if brand else name_compressed,
        "variation": variation,
        "raw": raw,
    }


# ═══════════════════════════════════════════════════════════════════════════
# INSTRUMENT FAMILY CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def classify_instrument_family(product: dict[str, Any]) -> dict[str, str]:
    """
    Classifies a product into instrument family → sub-category → body type.

    Priority order:
    1. spectrum_id mapping (curated, highest trust)
    2. Keyword scoring on name + description + category (NOT spectrum_id,
       to avoid cross-contamination like "bass-guitars" matching "guitar")

    Returns: {"family": "guitars", "sub_category": "electric", "body_type": "lp_type"}
    """
    name = (product.get("name") or "").lower()
    desc = (product.get("description") or product.get(
        "description_short") or "").lower()
    existing_cat = (product.get("category") or "").lower()
    spectrum = (product.get("spectrum_id") or "").lower()

    # Text for keyword scoring — deliberately EXCLUDES spectrum_id
    # to prevent cross-family contamination (e.g., "bass-guitars" matching "guitar")
    name_text = f"{name} {desc} {existing_cat}"
    # Full text including spectrum — only for sub-category / body-type refinement
    full_text = f"{name} {desc} {existing_cat} {spectrum}"

    result = {
        "family": "uncategorized",
        "sub_category": "general",
        "body_type": "general",
    }

    # ── Step 1: Spectrum-based mapping (PRIMARY — curated, highest trust) ──
    best_family = _family_from_spectrum_id(spectrum)

    # ── Step 2: Keyword scoring fallback (on name_text, NOT spectrum) ──
    if not best_family:
        best_family_score = 0.0

        for family_key, family_def in INSTRUMENT_FAMILIES.items():
            # Check exclusion keywords first (on name only)
            excluded = any(ex in name for ex in family_def.get(
                "exclude_keywords", []))
            if excluded:
                continue

            # Score family keywords with specificity weighting:
            # multi-word keywords score higher (more specific = more reliable)
            score = 0.0
            for kw in family_def["keywords"]:
                if kw in name_text:
                    word_count = len(kw.strip().split())
                    score += word_count  # "bass guitar" = 2, "guitar" = 1

            if score > best_family_score:
                best_family_score = score
                best_family = family_key

    if best_family:
        result["family"] = best_family
        family_def = INSTRUMENT_FAMILIES[best_family]

        # Find sub-category (best match by keyword count, using full_text)
        best_sub = None
        best_sub_score = 0.0
        for sub_key, sub_def in family_def["sub_categories"].items():
            sub_score = 0.0
            for kw in sub_def["keywords"]:
                if kw in full_text:
                    sub_score += len(kw.strip().split())
            if sub_score > best_sub_score:
                best_sub_score = sub_score
                best_sub = sub_key

        if best_sub:
            result["sub_category"] = best_sub

            # Find body type
            sub_def = family_def["sub_categories"][best_sub]
            for body_key, body_keywords in sub_def.get("body_types", {}).items():
                if any(kw in full_text for kw in body_keywords):
                    result["body_type"] = body_key
                    break

    return result


def _family_from_spectrum_id(spectrum_id: str) -> str | None:
    """Map existing spectrum IDs to the new instrument families."""
    mapping = {
        "electric-guitars": "guitars",
        "acoustic-guitars": "guitars",
        "bass-guitars": "bass",
        "guitar-amps": "amps_effects",
        "guitar-pedals": "amps_effects",
        "guitar-accessories": "accessories",
        "folk-instruments": "guitars",
        "acoustic-drums": "drums_percussion",
        "electronic-drums": "drums_percussion",
        "cymbals": "drums_percussion",
        "snares": "drums_percussion",
        "sticks-heads": "drums_percussion",
        "percussion": "drums_percussion",
        "drum-hardware": "drums_percussion",
        "synthesizers": "keys_production",
        "stage-pianos": "keys_production",
        "midi-controllers": "keys_production",
        "grooveboxes": "keys_production",
        "eurorack": "keys_production",
        "keys-accessories": "accessories",
        "audio-interfaces": "studio_recording",
        "studio-monitors": "studio_recording",
        "studio-microphones": "studio_recording",
        "outboard-gear": "studio_recording",
        "software-plugins": "studio_recording",
        "studio-accessories": "accessories",
        "pa-systems": "live_pa",
        "live-mixers": "live_pa",
        "dj-equipment": "live_pa",
        "lighting": "live_pa",
        "live-mics": "live_pa",
        "live-accessories": "accessories",
        "cables": "accessories",
        "stands": "accessories",
        "cases-bags": "accessories",
        "power-supplies": "accessories",
        "general-accessories": "accessories",
    }
    return mapping.get(spectrum_id)


# ═══════════════════════════════════════════════════════════════════════════
# MODEL GROUPING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def group_products_by_model(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Groups a flat list of products into ModelGroups.

    Each model group contains:
    - modelName: canonical model identity
    - brand: brand name
    - variations: list of product dicts (individual SKUs)
    - priceRange: {min, max, currency}
    - classification: {family, sub_category, body_type}
    - heroImage, variationCount, avgConfidence
    """
    model_map: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for product in products:
        brand = product.get("brand", "")
        name = product.get("name") or product.get("title", "")
        if not name:
            continue

        identity = extract_model_identity(name, brand)
        classification = classify_instrument_family(product)

        # Enrich product with parsed data (non-destructive)
        product["_model_identity"] = identity
        product["_classification"] = classification

        model_key = identity["model"].lower().strip()
        model_map[model_key].append(product)

    # Build model groups
    model_groups = []
    for model_key, variations in model_map.items():
        prices = [
            v.get("price", 0)
            for v in variations
            if v.get("price", 0) and v.get("price", 0) > 0
        ]

        # Use first variation's classification (should all match within a model)
        classification = variations[0].get("_classification", {})
        identity = variations[0].get("_model_identity", {})
        brand = variations[0].get("brand", "")

        # Pick hero image from the first variation that has one
        hero_image = ""
        for v in variations:
            img = v.get("image_url", "")
            if img:
                hero_image = img
                break

        # Average quality/confidence score
        scores = [v.get("quality_score", 0)
                  for v in variations if v.get("quality_score")]
        avg_score = sum(scores) / len(scores) if scores else 0

        group = {
            "modelName": identity.get("model", model_key),
            "modelKey": model_key,
            "brand": brand,
            "family": classification.get("family", "uncategorized"),
            "subCategory": classification.get("sub_category", "general"),
            "bodyType": classification.get("body_type", "general"),
            "variations": [
                {
                    "id": v.get("id", ""),
                    "name": v.get("name", ""),
                    "variation": v.get("_model_identity", {}).get("variation", "Standard"),
                    "price": v.get("price", 0),
                    "price_eilat": v.get("price_eilat", 0),
                    "tier": v.get("tier", ""),
                    "image_url": v.get("image_url", ""),
                    "sources": v.get("sources", []),
                    "quality_score": v.get("quality_score", 0),
                    "data_status": v.get("data_status", "MINIMAL"),
                    "specs": v.get("specs", {}),
                    "rating": v.get("rating", 0),
                    "family_id": v.get("family_id"),
                }
                for v in variations
            ],
            "priceRange": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "currency": "ILS",
            },
            "heroImage": hero_image,
            "variationCount": len(variations),
            "avgConfidence": round(avg_score, 1),
        }
        model_groups.append(group)

    # Sort by brand, then by price range min
    model_groups.sort(key=lambda g: (
        g["brand"].lower(), g["priceRange"]["min"]))

    return model_groups


def get_family_tree() -> list[dict[str, Any]]:
    """
    Returns the full instrument family tree for navigation sidebar.
    """
    families = []
    for key, fam in INSTRUMENT_FAMILIES.items():
        sub_cats = []
        for sub_key, sub_def in fam["sub_categories"].items():
            body_types = [
                {"slug": bt_key, "label": bt_key.replace("_", " ").title()}
                for bt_key in sub_def.get("body_types", {}).keys()
            ]
            sub_cats.append({
                "slug": sub_key,
                "label": sub_def.get("label", sub_key.replace("_", " ").title()),
                "bodyTypes": body_types,
            })
        families.append({
            "slug": key,
            "label": fam.get("label", key.replace("_", " ").title()),
            "icon": fam.get("icon", "music"),
            "subCategories": sub_cats,
        })
    return families
