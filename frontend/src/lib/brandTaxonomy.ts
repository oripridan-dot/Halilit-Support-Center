/**
 * Brand Taxonomy - Official Category Structures from Each Brand's Website
 *
 * This module defines the EXACT taxonomy used by each brand on their official website.
 * The UI must be 100% compatible with these official taxonomies.
 *
 * IMPORTANT: These are scraped directly from brand websites and should be treated
 * as the SOURCE OF TRUTH for product categorization.
 *
 * Architecture Decision: We display brand categories EXACTLY as they appear on
 * the brand's website. No remapping, no "universal" categories that obscure
 * the brand's own organization.
 */

export interface CategoryNode {
  id: string; // URL slug: "drums_percussion"
  label: string; // Display name: "Drums & Percussion"
  urlPath: string; // Full URL path for scraping
  parentId: string | null; // Parent category ID, null if root
  children: string[]; // Child category IDs
  icon?: string; // Emoji icon
  description?: string; // Short description
}

export interface BrandTaxonomy {
  brandId: string;
  brandName: string;
  baseUrl: string;
  categories: Record<string, CategoryNode>;
}

// =============================================================================
// ROLAND OFFICIAL TAXONOMY
// Source: https://www.roland.com/global/categories/
// Last verified: January 2026
// =============================================================================

export const ROLAND_TAXONOMY: BrandTaxonomy = {
  brandId: "roland",
  brandName: "Roland",
  baseUrl: "https://www.roland.com/global",
  categories: {
    // Root categories
    pianos: {
      id: "pianos",
      label: "Pianos",
      urlPath: "/global/categories/pianos/",
      parentId: null,
      icon: "🎹",
      description: "Digital Pianos, Stage Pianos, Grand Pianos",
      children: [
        "grand_pianos",
        "portable_pianos",
        "stage_pianos",
        "upright_pianos",
        "pianos_accessories",
      ],
    },
    synthesizers: {
      id: "synthesizers",
      label: "Synthesizers",
      urlPath: "/global/categories/synthesizers/",
      parentId: null,
      icon: "🎛️",
      description: "Analog Modeling, Performance Workstations",
      children: [
        "analog_modeling",
        "performance_workstation",
        "sound_expansion_patches",
        "synths_accessories",
      ],
    },
    keyboards: {
      id: "keyboards",
      label: "Keyboards",
      urlPath: "/global/categories/keyboards/",
      parentId: null,
      icon: "⌨️",
      description: "Arrangers, Controllers, Portable Keyboards",
      children: [],
    },
    organs: {
      id: "organs",
      label: "Organs",
      urlPath: "/global/categories/organs/",
      parentId: null,
      icon: "🎹",
      description: "Combo Organs, Organ Accessories",
      children: [],
    },
    drums_percussion: {
      id: "drums_percussion",
      label: "Drums & Percussion",
      urlPath: "/global/categories/drums_percussion/",
      parentId: null,
      icon: "🥁",
      description: "V-Drums, Electronic Percussion, Hybrid Drums",
      children: [
        "v_drums",
        "electronic_percussion",
        "hybrid_drums",
        "drums_accessories",
      ],
    },
    guitar_bass: {
      id: "guitar_bass",
      label: "Guitar & Bass",
      urlPath: "/global/categories/guitar_bass/",
      parentId: null,
      icon: "🎸",
      description: "Effects, Processors, Guitar Synths",
      children: [],
    },
    amplifiers: {
      id: "amplifiers",
      label: "Amplifiers",
      urlPath: "/global/categories/amplifiers/",
      parentId: null,
      icon: "🔊",
      description: "Guitar Amps, Keyboard Amps, Bass Amps",
      children: ["keyboard_amplifiers", "guitar_amplifiers", "bass_amplifiers"],
    },
    production: {
      id: "production",
      label: "Production",
      urlPath: "/global/categories/production/",
      parentId: null,
      icon: "🎚️",
      description: "Audio Interfaces, Mixers, Video",
      children: [],
    },
    aira: {
      id: "aira",
      label: "AIRA",
      urlPath: "/global/categories/aira/",
      parentId: null,
      icon: "🔮",
      description: "TR, TB, System-1, AIRA Compact",
      children: [],
    },
    wind_instruments: {
      id: "wind_instruments",
      label: "Wind Instruments",
      urlPath: "/global/categories/wind_instruments/",
      parentId: null,
      icon: "🎷",
      description: "Aerophone, Digital Wind Instruments",
      children: [],
    },
    roland_cloud: {
      id: "roland_cloud",
      label: "Roland Cloud",
      urlPath: "/global/categories/roland_cloud/",
      parentId: null,
      icon: "☁️",
      description: "Software, Plugins, Sound Libraries",
      children: [],
    },
    accessories: {
      id: "accessories",
      label: "Accessories",
      urlPath: "/global/categories/accessories/",
      parentId: null,
      icon: "🔧",
      description: "Cables, Stands, Cases, Pedals",
      children: [
        "cables",
        "instrument_cables",
        "microphone_cables",
        "interconnect_cables",
        "digital_cables",
        "midi_cables",
        "headphones",
        "stands",
        "cases_bags",
        "pedals",
      ],
    },

    // Pianos subcategories
    grand_pianos: {
      id: "grand_pianos",
      label: "Grand Pianos",
      urlPath: "/global/categories/pianos/grand_pianos/",
      parentId: "pianos",
      children: [],
    },
    portable_pianos: {
      id: "portable_pianos",
      label: "Portable Pianos",
      urlPath: "/global/categories/pianos/portable_pianos/",
      parentId: "pianos",
      children: [],
    },
    stage_pianos: {
      id: "stage_pianos",
      label: "Stage Pianos",
      urlPath: "/global/categories/pianos/stage_pianos/",
      parentId: "pianos",
      children: [],
    },
    upright_pianos: {
      id: "upright_pianos",
      label: "Upright Pianos",
      urlPath: "/global/categories/pianos/upright_pianos/",
      parentId: "pianos",
      children: [],
    },
    pianos_accessories: {
      id: "pianos_accessories",
      label: "Piano Accessories",
      urlPath: "/global/categories/pianos/accessories/",
      parentId: "pianos",
      children: [],
    },

    // Synthesizers subcategories
    analog_modeling: {
      id: "analog_modeling",
      label: "Analog Modeling",
      urlPath: "/global/categories/synthesizers/analog_modeling/",
      parentId: "synthesizers",
      children: [],
    },
    performance_workstation: {
      id: "performance_workstation",
      label: "Performance Workstation",
      urlPath: "/global/categories/synthesizers/performance_workstation/",
      parentId: "synthesizers",
      children: [],
    },
    sound_expansion_patches: {
      id: "sound_expansion_patches",
      label: "Sound Expansion & Patches",
      urlPath: "/global/categories/synthesizers/sound_expansion_patches/",
      parentId: "synthesizers",
      children: [],
    },
    synths_accessories: {
      id: "synths_accessories",
      label: "Synthesizer Accessories",
      urlPath: "/global/categories/synthesizers/accessories/",
      parentId: "synthesizers",
      children: [],
    },

    // Drums subcategories
    v_drums: {
      id: "v_drums",
      label: "V-Drums",
      urlPath: "/global/categories/drums_percussion/v_drums/",
      parentId: "drums_percussion",
      children: [],
    },
    electronic_percussion: {
      id: "electronic_percussion",
      label: "Electronic Percussion",
      urlPath: "/global/categories/drums_percussion/electronic_percussion/",
      parentId: "drums_percussion",
      children: [],
    },
    hybrid_drums: {
      id: "hybrid_drums",
      label: "Hybrid Drums",
      urlPath: "/global/categories/drums_percussion/hybrid_drums/",
      parentId: "drums_percussion",
      children: [],
    },
    drums_accessories: {
      id: "drums_accessories",
      label: "Drums Accessories",
      urlPath: "/global/categories/drums_percussion/accessories/",
      parentId: "drums_percussion",
      children: [],
    },

    // Amplifier subcategories
    keyboard_amplifiers: {
      id: "keyboard_amplifiers",
      label: "Keyboard Amplifiers",
      urlPath: "/global/categories/amplifiers/keyboard_amplifiers/",
      parentId: "amplifiers",
      children: [],
    },
    guitar_amplifiers: {
      id: "guitar_amplifiers",
      label: "Guitar Amplifiers",
      urlPath: "/global/categories/amplifiers/guitar_amplifiers/",
      parentId: "amplifiers",
      children: [],
    },
    bass_amplifiers: {
      id: "bass_amplifiers",
      label: "Bass Amplifiers",
      urlPath: "/global/categories/amplifiers/bass_amplifiers/",
      parentId: "amplifiers",
      children: [],
    },

    // Accessories subcategories
    cables: {
      id: "cables",
      label: "Cables",
      urlPath: "/global/categories/accessories/cables/",
      parentId: "accessories",
      children: [],
    },
    instrument_cables: {
      id: "instrument_cables",
      label: "Instrument Cables",
      urlPath: "/global/categories/accessories/instrument_cables/",
      parentId: "accessories",
      children: [],
    },
    microphone_cables: {
      id: "microphone_cables",
      label: "Microphone Cables",
      urlPath: "/global/categories/accessories/microphone_cables/",
      parentId: "accessories",
      children: [],
    },
    interconnect_cables: {
      id: "interconnect_cables",
      label: "Interconnect Cables",
      urlPath: "/global/categories/accessories/interconnect_cables/",
      parentId: "accessories",
      children: [],
    },
    digital_cables: {
      id: "digital_cables",
      label: "Digital Cables",
      urlPath: "/global/categories/accessories/digital_cables/",
      parentId: "accessories",
      children: [],
    },
    midi_cables: {
      id: "midi_cables",
      label: "MIDI Cables",
      urlPath: "/global/categories/accessories/midi_cables/",
      parentId: "accessories",
      children: [],
    },
    headphones: {
      id: "headphones",
      label: "Headphones",
      urlPath: "/global/categories/accessories/headphones/",
      parentId: "accessories",
      children: [],
    },
    stands: {
      id: "stands",
      label: "Stands",
      urlPath: "/global/categories/accessories/stands/",
      parentId: "accessories",
      children: [],
    },
    cases_bags: {
      id: "cases_bags",
      label: "Cases & Bags",
      urlPath: "/global/categories/accessories/cases_bags/",
      parentId: "accessories",
      children: [],
    },
    pedals: {
      id: "pedals",
      label: "Pedals",
      urlPath: "/global/categories/accessories/pedals/",
      parentId: "accessories",
      children: [],
    },
  },
};

// =============================================================================
// BOSS OFFICIAL TAXONOMY
// Source: https://www.boss.info/global/categories/
// Last verified: January 2026
// =============================================================================

export const BOSS_TAXONOMY: BrandTaxonomy = {
  brandId: "boss",
  brandName: "BOSS",
  baseUrl: "https://www.boss.info/global",
  categories: {
    effects_pedals: {
      id: "effects_pedals",
      label: "Effects Pedals",
      urlPath: "/global/categories/effects_pedals/",
      parentId: null,
      icon: "🎸",
      description: "Stompboxes, Compact Pedals",
      children: [],
    },
    multi_effects: {
      id: "multi_effects",
      label: "Multi-Effects",
      urlPath: "/global/categories/multi-effects/",
      parentId: null,
      icon: "🎛️",
      description: "Floor Units, Desktop",
      children: [],
    },
    guitar_synthesizers: {
      id: "guitar_synthesizers",
      label: "Guitar Synthesizers",
      urlPath: "/global/categories/guitar_synthesizers/",
      parentId: null,
      icon: "🎹",
      description: "GK, SY Series",
      children: [],
    },
    amplifiers: {
      id: "amplifiers",
      label: "Amplifiers",
      urlPath: "/global/categories/amplifiers/",
      parentId: null,
      icon: "🔊",
      description: "Katana, Cube, Acoustic",
      children: [],
    },
    acoustic: {
      id: "acoustic",
      label: "Acoustic",
      urlPath: "/global/categories/acoustic/",
      parentId: null,
      icon: "🪕",
      description: "Acoustic Amps, Preamps",
      children: [],
    },
    loop_station: {
      id: "loop_station",
      label: "Loop Station",
      urlPath: "/global/categories/loop_station/",
      parentId: null,
      icon: "🔁",
      description: "RC Series, Loop Stations",
      children: [],
    },
    vocal_effects: {
      id: "vocal_effects",
      label: "Vocal Effects",
      urlPath: "/global/categories/vocal_effects/",
      parentId: null,
      icon: "🎤",
      description: "VE Series, Vocal Processors",
      children: [],
    },
    mixers_audio_solutions: {
      id: "mixers_audio_solutions",
      label: "Mixers & Audio Solutions",
      urlPath: "/global/categories/mixers_audio_solutions/",
      parentId: null,
      icon: "🎚️",
      description: "Personal Mixers, Audio Interfaces",
      children: [],
    },
    tuners_metronomes: {
      id: "tuners_metronomes",
      label: "Tuners & Metronomes",
      urlPath: "/global/categories/tuners_metronomes/",
      parentId: null,
      icon: "🎵",
      description: "TU Series, DB Series",
      children: [],
    },
    wireless: {
      id: "wireless",
      label: "Wireless",
      urlPath: "/global/categories/wireless/",
      parentId: null,
      icon: "📡",
      description: "WL Series",
      children: [],
    },
    accessories: {
      id: "accessories",
      label: "Accessories",
      urlPath: "/global/categories/accessories/",
      parentId: null,
      icon: "🔧",
      description: "Footswitches, Power Supplies, Cables",
      children: [],
    },
  },
};

// =============================================================================
// NORD OFFICIAL TAXONOMY
// Source: https://www.nordkeyboards.com/products
// Last verified: January 2026
// =============================================================================

export const NORD_TAXONOMY: BrandTaxonomy = {
  brandId: "nord",
  brandName: "Nord",
  baseUrl: "https://www.nordkeyboards.com",
  categories: {
    stage: {
      id: "stage",
      label: "Stage",
      urlPath: "/products/nord-stage",
      parentId: null,
      icon: "🎹",
      description: "Flagship Stage Keyboards",
      children: [],
    },
    piano: {
      id: "piano",
      label: "Piano",
      urlPath: "/products/nord-piano",
      parentId: null,
      icon: "🎹",
      description: "Stage Piano Series",
      children: [],
    },
    electro: {
      id: "electro",
      label: "Electro",
      urlPath: "/products/nord-electro",
      parentId: null,
      icon: "🎹",
      description: "Electro-Mechanical Keyboards",
      children: [],
    },
    lead: {
      id: "lead",
      label: "Lead",
      urlPath: "/products/nord-lead",
      parentId: null,
      icon: "🎛️",
      description: "Virtual Analog Synths",
      children: [],
    },
    wave: {
      id: "wave",
      label: "Wave",
      urlPath: "/products/nord-wave",
      parentId: null,
      icon: "🌊",
      description: "Wavetable Synthesizers",
      children: [],
    },
    drum: {
      id: "drum",
      label: "Drum",
      urlPath: "/products/nord-drum",
      parentId: null,
      icon: "🥁",
      description: "Virtual Analog Drum Machines",
      children: [],
    },
    c_organ: {
      id: "c_organ",
      label: "C2D Organ",
      urlPath: "/products/nord-c2d",
      parentId: null,
      icon: "🎹",
      description: "Combo Organ",
      children: [],
    },
    accessories: {
      id: "accessories",
      label: "Accessories",
      urlPath: "/products/accessories",
      parentId: null,
      icon: "🔧",
      description: "Pedals, Cases, Stands",
      children: [],
    },
    software: {
      id: "software",
      label: "Software",
      urlPath: "/software",
      parentId: null,
      icon: "💻",
      description: "Sound Manager, Sample Editor",
      children: [],
    },
  },
};

// =============================================================================
// MOOG OFFICIAL TAXONOMY
// Source: https://www.moogmusic.com/products
// Last verified: January 2026
// =============================================================================

export const MOOG_TAXONOMY: BrandTaxonomy = {
  brandId: "moog",
  brandName: "Moog",
  baseUrl: "https://www.moogmusic.com",
  categories: {
    synthesizers: {
      id: "synthesizers",
      label: "Synthesizers",
      urlPath: "/products/synthesizers",
      parentId: null,
      icon: "🎛️",
      description: "Analog Synthesizers",
      children: ["semi_modular", "polyphonic", "monophonic", "modular"],
    },
    semi_modular: {
      id: "semi_modular",
      label: "Semi-Modular",
      urlPath: "/products/semi-modular",
      parentId: "synthesizers",
      description: "Mother-32, DFAM, Subharmonicon",
      children: [],
    },
    polyphonic: {
      id: "polyphonic",
      label: "Polyphonic",
      urlPath: "/products/polyphonic",
      parentId: "synthesizers",
      description: "One, Matriarch, Grandmother",
      children: [],
    },
    monophonic: {
      id: "monophonic",
      label: "Monophonic",
      urlPath: "/products/monophonic",
      parentId: "synthesizers",
      description: "Minimoog, Sub, Voyager",
      children: [],
    },
    modular: {
      id: "modular",
      label: "Modular",
      urlPath: "/products/modular",
      parentId: "synthesizers",
      description: "Eurorack Modules",
      children: [],
    },
    effects: {
      id: "effects",
      label: "Effects",
      urlPath: "/products/effects",
      parentId: null,
      icon: "🎸",
      description: "Moogerfooger, Minifooger",
      children: [],
    },
    keyboards: {
      id: "keyboards",
      label: "Keyboards",
      urlPath: "/products/keyboards",
      parentId: null,
      icon: "⌨️",
      description: "Controllers",
      children: [],
    },
    accessories: {
      id: "accessories",
      label: "Accessories",
      urlPath: "/products/accessories",
      parentId: null,
      icon: "🔧",
      description: "Cables, Cases, Patch Cables",
      children: [],
    },
  },
};

// =============================================================================
// MASTER REGISTRY
// =============================================================================

export const BRAND_TAXONOMIES: Record<string, BrandTaxonomy> = {
  roland: ROLAND_TAXONOMY,
  boss: BOSS_TAXONOMY,
  nord: NORD_TAXONOMY,
  moog: MOOG_TAXONOMY,
};

/**
 * Get the taxonomy for a specific brand
 */
export function getBrandTaxonomy(brandId: string): BrandTaxonomy | undefined {
  return BRAND_TAXONOMIES[brandId.toLowerCase()];
}

/**
 * Get root categories for a brand (no parent)
 */
export function getRootCategories(brandId: string): CategoryNode[] {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return [];

  return Object.values(taxonomy.categories).filter(
    (cat) => cat.parentId === null,
  );
}

/**
 * Get child categories for a parent
 */
export function getChildCategories(
  brandId: string,
  parentId: string,
): CategoryNode[] {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return [];

  const parent = taxonomy.categories[parentId];
  if (!parent) return [];

  return parent.children
    .map((childId) => taxonomy.categories[childId])
    .filter(Boolean);
}

/**
 * Validate if a category exists in a brand's taxonomy
 */
export function validateCategory(brandId: string, category: string): boolean {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return false;

  const normalized = category.toLowerCase().replace(/[\s-]/g, "_");

  return Object.values(taxonomy.categories).some(
    (cat) =>
      cat.id === normalized ||
      cat.label.toLowerCase() === category.toLowerCase(),
  );
}

/**
 * Normalize a raw category string to the official brand taxonomy label
 */
export function normalizeCategory(
  brandId: string,
  rawCategory: string,
): string | null {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return null;

  const normalized = rawCategory.toLowerCase().replace(/[\s-]/g, "_");

  // Direct ID match
  if (taxonomy.categories[normalized]) {
    return taxonomy.categories[normalized].label;
  }

  // Label match (case-insensitive)
  const match = Object.values(taxonomy.categories).find(
    (cat) => cat.label.toLowerCase() === rawCategory.toLowerCase(),
  );

  if (match) return match.label;

  // Fuzzy match - check if raw contains category keywords
  for (const cat of Object.values(taxonomy.categories)) {
    const words = cat.label.toLowerCase().split(/[\s&]/);
    if (words.some((word) => word.length > 3 && normalized.includes(word))) {
      return cat.label;
    }
  }

  return null;
}

/**
 * Get the full path from root to a category
 */
export function getCategoryPath(brandId: string, categoryId: string): string[] {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return [];

  const path: string[] = [];
  let current: CategoryNode | undefined = taxonomy.categories[categoryId];

  while (current) {
    path.unshift(current.label);
    current = current.parentId
      ? taxonomy.categories[current.parentId]
      : undefined;
  }

  return path;
}

/**
 * Get all category labels for a brand
 */
export function getAllCategoryLabels(brandId: string): string[] {
  const taxonomy = getBrandTaxonomy(brandId);
  if (!taxonomy) return [];

  return Object.values(taxonomy.categories).map((cat) => cat.label);
}

/**
 * Get list of all available brands
 */
export function getAvailableBrands(): string[] {
  return Object.keys(BRAND_TAXONOMIES);
}
