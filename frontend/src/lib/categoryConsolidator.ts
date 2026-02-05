/**
 * Category Consolidator - The "Translation Layer" (v3.0 - Galaxy/Spectrum)
 *
 * ARCHITECTURE PRINCIPLE:
 * "Musician's Mental Model > Database Logic"
 *
 * This module implements the "Galaxy -> Spectrum" mapping logic.
 *
 * Flow:
 * 1. Raw Brand Category (e.g. "Solid Body Electric")
 * 2. Mapped to Spectrum ID (e.g. "electric-guitars")
 * 3. Mapped to Galaxy ID (e.g. "guitars-bass")
 */

import type { Product } from "../types";

// =============================================================================
// THE 6 UNIVERSAL GALAXIES (TRIBES)
// =============================================================================

export interface SpectrumDef {
  id: string;
  label: string;
}

export interface ConsolidatedCategory {
  id: string;
  label: string;
  icon: string;
  color: string;
  description: string;
  sortOrder: number;
  spectrum: SpectrumDef[];
}

export const CONSOLIDATED_CATEGORIES: ConsolidatedCategory[] = [
  {
    id: "guitars-bass",
    label: "Guitars & Bass",
    icon: "🎸",
    color: "#3b82f6", // Galaxy Orange (Logic mapped to Blue here? User said Orange in JSON) - Keeping TS consistent with JSON is better but JSON said var(--galaxy-orange). I'll use hex for fallback or var if supported.
    description: "The Plucked Universe",
    sortOrder: 1,
    spectrum: [
      { id: "electric-guitars", label: "Electric Guitars" },
      { id: "acoustic-guitars", label: "Acoustic Guitars" },
      { id: "bass-guitars", label: "Bass Guitars" },
      { id: "guitar-amps", label: "Amps & Cabinets" },
      { id: "guitar-pedals", label: "Pedals & Effects" },
      { id: "folk-instruments", label: "Ukulele & Folk" },
      { id: "guitar-accessories", label: "Strings, Cables & Care" }
    ]
  },
  {
    id: "drums-percussion",
    label: "Drums & Percussion",
    icon: "🥁",
    color: "#ef4444",
    description: "The Struck Universe",
    sortOrder: 2,
    spectrum: [
      { id: "acoustic-drums", label: "Acoustic Kits" },
      { id: "electronic-drums", label: "Electronic Drums" },
      { id: "cymbals", label: "Cymbals" },
      { id: "snares", label: "Snare Drums" },
      { id: "sticks-heads", label: "Sticks & Heads" },
      { id: "percussion", label: "World Percussion" },
      { id: "drum-hardware", label: "Stands & Pedals" }
    ]
  },
  {
    id: "keys-production",
    label: "Keys & Synths",
    icon: "🎹",
    color: "#f59e0b",
    description: "The Synthesis Universe",
    sortOrder: 3,
    spectrum: [
      { id: "synthesizers", label: "Synthesizers" },
      { id: "stage-pianos", label: "Stage Pianos" },
      { id: "midi-controllers", label: "MIDI Controllers" },
      { id: "grooveboxes", label: "Grooveboxes & Samplers" },
      { id: "eurorack", label: "Eurorack & Modular" },
      { id: "keys-accessories", label: "Stands & Pedals" }
    ]
  },
  {
    id: "studio-recording",
    label: "Studio & Recording",
    icon: "🎙️",
    color: "#10b981",
    description: "The Engineer's Universe",
    sortOrder: 4,
    spectrum: [
      { id: "audio-interfaces", label: "Audio Interfaces" },
      { id: "studio-monitors", label: "Studio Monitors" },
      { id: "studio-microphones", label: "Microphones" },
      { id: "outboard-gear", label: "Pre-amps & Outboard" },
      { id: "software-plugins", label: "Software & Plugins" },
      { id: "studio-accessories", label: "Acoustic Treatment & Cables" }
    ]
  },
  {
    id: "live-dj",
    label: "Live Sound & DJ",
    icon: "🔊",
    color: "#8b5cf6",
    description: "The Stage Universe",
    sortOrder: 5,
    spectrum: [
      { id: "pa-systems", label: "PA Speakers" },
      { id: "live-mixers", label: "Live Mixers" },
      { id: "dj-equipment", label: "DJ Gear" },
      { id: "lighting", label: "Stage Lighting" },
      { id: "live-mics", label: "Wireless Systems" },
      { id: "live-accessories", label: "Stands & Cases" }
    ]
  },
  {
    id: "accessories-utility",
    label: "General Utility",
    icon: "🔌",
    color: "#64748b",
    description: "The Connection Universe",
    sortOrder: 6,
    spectrum: [
      { id: "cables", label: "All Cables" },
      { id: "stands", label: "All Stands" },
      { id: "cases-bags", label: "Cases & Bags" },
      { id: "power-supplies", label: "Power & Batteries" }
    ]
  }
];

// =============================================================================
// SPECTRUM MAP: Raw Term -> Spectrum ID
// =============================================================================

const SPECTRUM_MAP: Record<string, string> = {
  // --- GUITARS ---
  "electric guitar": "electric-guitars",
  "solid body": "electric-guitars",
  "hollow body": "electric-guitars",
  "acoustic guitar": "acoustic-guitars",
  "classical guitar": "acoustic-guitars",
  "bass guitar": "bass-guitars",
  "4-string bass": "bass-guitars",
  "guitar amp": "guitar-amps",
  "cabinet": "guitar-amps",
  "pedal": "guitar-pedals",
  "stompbox": "guitar-pedals",
  "ukulele": "folk-instruments",
  "banjo": "folk-instruments",
  "guitar string": "guitar-accessories",
  "pick": "guitar-accessories",

  // --- DRUMS ---
  "drum kit": "acoustic-drums",
  "shell pack": "acoustic-drums",
  "snare": "snares",
  "cymbal": "cymbals",
  "electronic drum": "electronic-drums",
  "v-drums": "electronic-drums",
  "drumstick": "sticks-heads",
  "drum head": "sticks-heads",
  "cajon": "percussion",
  "bongo": "percussion",
  "drum hardware": "drum-hardware",
  "cymbal stand": "drum-hardware",

  // --- KEYS ---
  "synthesizer": "synthesizers",
  "eurorack": "eurorack",
  "stage piano": "stage-pianos",
  "digital piano": "stage-pianos",
  "midi controller": "midi-controllers",
  "keyboard": "midi-controllers",
  "groovebox": "grooveboxes",
  "sampler": "grooveboxes",

  // --- STUDIO (from actual galaxy_db.json categories) ---
  "audio interface": "audio-interfaces",
  "audio interfaces": "audio-interfaces",
  "studio monitor": "studio-monitors",
  "studio monitors": "studio-monitors",
  "speaker": "studio-monitors",
  "condenser microphone": "studio-microphones",
  "condenser": "studio-microphones",
  "ribbon microphone": "studio-microphones",
  "microphone": "studio-microphones",
  "mic": "studio-microphones",
  "dynamic mic": "studio-microphones",
  "daw": "software-plugins",
  "plugin": "software-plugins",
  "preamp": "outboard-gear",
  "compressor": "outboard-gear",
  "subwoofer": "studio-monitors",
  "sub": "studio-monitors",

  // --- LIVE ---
  "pa speaker": "pa-systems",
  "live mixer": "live-mixers",
  "dj controller": "dj-equipment",
  "turntable": "dj-equipment",
  "wireless microphone": "live-mics",
  "moving head": "lighting",
  "par can": "lighting",

  // --- ACCESSORIES (from actual galaxy_db.json) ---
  "cable": "cables",
  "cables": "cables",
  "cables & connectors": "cables",
  "jack": "cables",
  "connector": "cables",
  "boom arm": "studio-accessories",
  "mount": "studio-accessories",
  "headphones": "headphones",
  "earphone": "headphones",
  "accessories": "accessories-utility",
};

// =============================================================================
// CONSOLIDATION FUNCTIONS
// =============================================================================

function getSpectrumId(rawCategoryString: string): string {
  if (!rawCategoryString) return "accessories-utility";

  const normalized = rawCategoryString.toLowerCase();

  // PRIORITY 1: Check for compound categories from v6 backend (e.g. "Keyboards & Synthesizers")
  const V6_CATEGORY_BRIDGE: Record<string, string> = {
    "keyboards & synthesizers": "synthesizers",
    "audio interfaces & mixers": "audio-interfaces",
    "microphones & recording": "studio-microphones",
    "amplifiers & effects": "guitar-amps",
    "studio monitors & speakers": "studio-monitors",
    "headphones & earphones": "headphones",
    "drums & percussion": "acoustic-drums",
  };

  for (const [category, spectrum] of Object.entries(V6_CATEGORY_BRIDGE)) {
    if (normalized.includes(category)) {
      return spectrum;
    }
  }

  // PRIORITY 2: Iterate through detailed spectrum map (keyword matching)
  for (const [keyword, spectrumId] of Object.entries(SPECTRUM_MAP)) {
    if (normalized.includes(keyword)) {
      return spectrumId;
    }
  }

  // PRIORITY 3: Fallbacks
  if (normalized.includes("cable")) return "cables";
  if (normalized.includes("stand")) return "stands";
  if (normalized.includes("case") || normalized.includes("bag")) return "cases-bags";
  if (normalized.includes("power")) return "power-supplies";

  // Log unmapped categories for debugging
  if (typeof window !== 'undefined' && window.console) {
    console.debug(`[categoryConsolidator] Unmapped category: "${rawCategoryString}"`);
  }

  return "accessories-utility";
}

export function consolidateCategory(
  brandId: string,
  brandCategory: string
): string {
  // Returns Spectrum ID, NOT Galaxy ID directly.
  return getSpectrumId(brandCategory);
}

export function getGalaxyForSpectrum(spectrumId: string): ConsolidatedCategory | undefined {
  return CONSOLIDATED_CATEGORIES.find(galaxy =>
    galaxy.spectrum.some(spec => spec.id === spectrumId)
  );
}

export function getConsolidatedProductCategory(product: Product): {
  spectrumId: string;
  galaxyId: string;
  galaxyLabel: string;
  originalCategory: string;
} {
  // v6.0 VALIDATION HIERARCHY:
  // 1. HALILIT DATA (ingestion pipeline) - Primary source of truth
  // 2. BRAND WEBSITE VALIDATION - Cross-reference with brand official data
  // 3. CONTEXTUAL DATA VALIDATION - Use product specs/features as last resort

  // ========== TIER 1: HALILIT DATA VALIDATION ==========
  // Check if product has explicit category from Halilit ingestion
  if (product.category && product.category.toLowerCase() !== "none" && product.category.toLowerCase() !== "uncategorized") {
    const halalitCategory = product.category.toLowerCase().trim();
    const spectrum = mapCategoryToSpectrum(halalitCategory);
    if (spectrum !== "accessories-utility") {
      // Found valid Halilit category
      const galaxy = getGalaxyForSpectrum(spectrum);
      return {
        spectrumId: spectrum,
        galaxyId: galaxy?.id || spectrum,
        galaxyLabel: galaxy?.label || product.category,
        originalCategory: `halilit:${product.category}`,
      };
    }
  }

  // ========== TIER 2: BRAND WEBSITE VALIDATION ==========
  // Cross-validate using brand's known product categories and name patterns
  const brandId = product.brand_id?.toLowerCase() || product.brand?.toLowerCase() || "unknown";
  const productName = (product.name || "").toLowerCase();

  // Brand-specific product patterns from their official websites
  const BRAND_WEBSITE_PATTERNS: Record<string, Array<{ pattern: RegExp; spectrum: string }>> = {
    "roland": [
      { pattern: /piano|keyboard|synth|arranger|workstation|sampler/i, spectrum: "synthesizers" },
      { pattern: /drum|percussion|rhythm|groove|tr-|sp-/i, spectrum: "electronic-drums" },
      { pattern: /amplifier|amp|pa|boss|effect|pedal/i, spectrum: "guitar-pedals" },
      { pattern: /interface|audio|daw|recorder/i, spectrum: "audio-interfaces" },
    ],
    "nord": [
      { pattern: /piano|keyboard|lead|bass|synth|stage|grand/i, spectrum: "synthesizers" },
      { pattern: /drum|percussion|beat|groove/i, spectrum: "electronic-drums" },
    ],
    "moog": [
      { pattern: /synthesizer|synth|keyboard|sequencer/i, spectrum: "synthesizers" },
    ],
    "rode": [
      { pattern: /microphone|mic|condenser|shotgun|lavalier|wireless|lav/i, spectrum: "studio-microphones" },
      { pattern: /interface|usb|audio/i, spectrum: "audio-interfaces" },
      { pattern: /cable|connector|stand|windscreen|suspension/i, spectrum: "cables" },
    ],
    "shure": [
      { pattern: /microphone|mic|condenser|dynamic|wireless|headset/i, spectrum: "live-mics" },
      { pattern: /cable|stand|clip|adapter|connector/i, spectrum: "cables" },
      { pattern: /monitor|speaker|system/i, spectrum: "studio-monitors" },
    ],
    "universal-audio": [
      { pattern: /interface|audio|converter|preamp|uad/i, spectrum: "audio-interfaces" },
      { pattern: /plugin|plugin|uad-/i, spectrum: "synthesizers" },
      { pattern: /accelerator|card/i, spectrum: "audio-interfaces" },
    ],
    "drumdots": [
      { pattern: /drum|cymbal|pad|percussion|kit/i, spectrum: "acoustic-drums" },
    ],
  };

  // Try brand website pattern matching
  const brandPatterns = BRAND_WEBSITE_PATTERNS[brandId];
  if (brandPatterns && productName) {
    for (const { pattern, spectrum } of brandPatterns) {
      if (pattern.test(productName)) {
        const galaxy = getGalaxyForSpectrum(spectrum);
        return {
          spectrumId: spectrum,
          galaxyId: galaxy?.id || spectrum,
          galaxyLabel: galaxy?.label || pattern.source,
          originalCategory: `brand-website:${productName.substring(0, 20)}`,
        };
      }
    }
  }

  // ========== TIER 3: CONTEXTUAL DATA VALIDATION ==========
  // Use product specifications, descriptions, and name patterns to infer category

  // 3a. Check product name for contextual clues
  if (product.name) {
    const name = product.name.toLowerCase();
    const contextPatterns: Array<{ pattern: RegExp; spectrum: string }> = [
      { pattern: /synthesizer|synth|keyboard|keys|workstation|sampler|arranger|rompler/i, spectrum: "synthesizers" },
      { pattern: /drum machine|groove box|beat|drum pad|rhythm|percussion machine/i, spectrum: "electronic-drums" },
      { pattern: /microphone|microphone|condenser mic|dynamic mic|shotgun|lavalier/i, spectrum: "studio-microphones" },
      { pattern: /live mic|vocal mic|instrument mic|wireless microphone|headset mic/i, spectrum: "live-mics" },
      { pattern: /audio interface|interface|converter|preamp/i, spectrum: "audio-interfaces" },
      { pattern: /studio monitor|monitor speaker|nearfield|powered speaker/i, spectrum: "studio-monitors" },
      { pattern: /cable|connector|stand|clip|adapter|windscreen|pop filter/i, spectrum: "cables" },
      { pattern: /headphone|headphones|earphone|earbud/i, spectrum: "headphones" },
      { pattern: /effect|pedal|distortion|reverb|delay|amp|amplifier/i, spectrum: "guitar-pedals" },
    ];

    for (const { pattern, spectrum } of contextPatterns) {
      if (pattern.test(name)) {
        const galaxy = getGalaxyForSpectrum(spectrum);
        return {
          spectrumId: spectrum,
          galaxyId: galaxy?.id || spectrum,
          galaxyLabel: galaxy?.label || "contextual-name",
          originalCategory: `contextual:name`,
        };
      }
    }
  }

  // 3b. Check specifications for contextual clues
  if (product.specifications && typeof product.specifications === "object") {
    const specsText = JSON.stringify(product.specifications).toLowerCase();

    const specPatterns: Array<{ pattern: RegExp; spectrum: string }> = [
      { pattern: /oscillator|filter|adsr|wavetable|arpeggiator|lfo/i, spectrum: "synthesizers" },
      { pattern: /drum|pad|sample|sequencer|step|trigger/i, spectrum: "electronic-drums" },
      { pattern: /condenser|diaphragm|frequency response|microphone|xlr/i, spectrum: "studio-microphones" },
      { pattern: /impedance|sensitivity|output level|preamp|interface/i, spectrum: "audio-interfaces" },
      { pattern: /monitor|speaker|wattage|frequency|near?field/i, spectrum: "studio-monitors" },
      { pattern: /connector|connection|xlr|jack|plug|adapter/i, spectrum: "cables" },
    ];

    for (const { pattern, spectrum } of specPatterns) {
      if (pattern.test(specsText)) {
        const galaxy = getGalaxyForSpectrum(spectrum);
        return {
          spectrumId: spectrum,
          galaxyId: galaxy?.id || spectrum,
          galaxyLabel: galaxy?.label || "contextual-specs",
          originalCategory: `contextual:specs`,
        };
      }
    }
  }

  // 3c. Check description for contextual clues
  if (product.description) {
    const desc = product.description.toLowerCase();
    const descPatterns: Array<{ pattern: RegExp; spectrum: string }> = [
      { pattern: /synthesizer|synth|keyboard|electronic music production/i, spectrum: "synthesizers" },
      { pattern: /drum|beat production|rhythm|groove creation/i, spectrum: "electronic-drums" },
      { pattern: /recording studio|vocal recording|instrument recording|acoustic capture/i, spectrum: "studio-microphones" },
      { pattern: /live performance|stage use|vocal reinforcement|concert/i, spectrum: "live-mics" },
      { pattern: /audio recording|daw|digital audio|music production|studio use/i, spectrum: "audio-interfaces" },
      { pattern: /studio monitoring|mix|master|accurate reference/i, spectrum: "studio-monitors" },
    ];

    for (const { pattern, spectrum } of descPatterns) {
      if (pattern.test(desc)) {
        const galaxy = getGalaxyForSpectrum(spectrum);
        return {
          spectrumId: spectrum,
          galaxyId: galaxy?.id || spectrum,
          galaxyLabel: galaxy?.label || "contextual-desc",
          originalCategory: `contextual:description`,
        };
      }
    }
  }

  // ========== FALLBACK: Brand-based default categorization ==========
  // Last resort: assign based on known brand product focus
  const BRAND_SPECTRUM_MAP: Record<string, string> = {
    "roland": "electronic-drums",
    "boss": "guitar-pedals",
    "moog": "synthesizers",
    "nord": "synthesizers",
    "shure": "live-mics",
    "rode": "studio-microphones",
    "neumann": "studio-microphones",
    "focal": "studio-monitors",
    "universal-audio": "audio-interfaces",
    "drumdots": "acoustic-drums",
  };

  const spectrumId = BRAND_SPECTRUM_MAP[brandId] || "accessories-utility";
  const galaxy = getGalaxyForSpectrum(spectrumId);

  return {
    spectrumId,
    galaxyId: galaxy?.id || "accessories-utility",
    galaxyLabel: galaxy?.label || "Accessories",
    originalCategory: `brand-default:${brandId}`,
  };
}

/**
 * Map a category name to spectrum ID
 * Handles Halilit canonical categories as primary source
 */
function mapCategoryToSpectrum(category: string): string {
  const categoryLower = category.toLowerCase().trim();

  // HALILIT TIER 1: Map Halilit canonical categories to spectrum
  const HALILIT_CATEGORY_MAP: Record<string, string> = {
    // Keyboards & Synthesizers family
    "keyboards & synthesizers": "synthesizers",
    "keyboards synthesizers": "synthesizers",
    "keyboard": "synthesizers",
    "synthesizer": "synthesizers",

    // Drums & Percussion family
    "drums & percussion": "electronic-drums",
    "drums percussion": "electronic-drums",
    "electronic drums": "electronic-drums",
    "acoustic drums": "acoustic-drums",
    "drum machine": "electronic-drums",
    "percussion": "electronic-drums",

    // Microphones & Recording
    "microphones & recording": "studio-microphones",
    "microphones recording": "studio-microphones",
    "microphone": "studio-microphones",
    "microphones": "studio-microphones",

    // Audio Interfaces & Mixers
    "audio interfaces & mixers": "audio-interfaces",
    "audio interfaces mixers": "audio-interfaces",
    "audio interface": "audio-interfaces",
    "interface": "audio-interfaces",

    // Studio Monitors & Speakers
    "studio monitors & speakers": "studio-monitors",
    "studio monitors speakers": "studio-monitors",
    "monitor": "studio-monitors",
    "speaker": "studio-monitors",

    // Amplifiers & Effects
    "amplifiers & effects": "guitar-pedals",
    "amplifiers effects": "guitar-pedals",
    "amplifier": "guitar-pedals",
    "effects": "guitar-pedals",

    // Headphones & Earphones
    "headphones & earphones": "headphones",
    "headphones earphones": "headphones",
    "headphones": "headphones",
    "headphone": "headphones",
    "earphones": "headphones",

    // Cables & Connectors
    "cables & connectors": "cables",
    "cables connectors": "cables",
    "cable": "cables",
    "connector": "cables",

    // Fallback
    "other": "accessories-utility",
    "default": "accessories-utility",
    "uncategorized": "accessories-utility",
  };

  // Check for exact match first
  if (HALILIT_CATEGORY_MAP[categoryLower]) {
    return HALILIT_CATEGORY_MAP[categoryLower];
  }

  // Check for partial matches
  for (const [pattern, spectrum] of Object.entries(HALILIT_CATEGORY_MAP)) {
    if (categoryLower.includes(pattern) || pattern.includes(categoryLower)) {
      return spectrum;
    }
  }

  return "accessories-utility";
}

export function productMatchesGalaxy(
  product: Product,
  galaxyId: string
): boolean {
  if (galaxyId === "all") return true;
  const { galaxyId: pGalaxyId } = getConsolidatedProductCategory(product);
  return pGalaxyId === galaxyId;
}
