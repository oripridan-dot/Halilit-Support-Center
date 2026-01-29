/**
 * Brand Extraction Utilities
 * Helper functions to determine brand from spectrum ID
 * 
 * Path: frontend/src/lib/brandExtraction.ts
 */

/**
 * Mapping of spectrum IDs to primary brands
 * Used to determine which brand to highlight for each product category
 */
const SPECTRUM_BRAND_MAP: Record<string, string> = {
  // Guitars & Bass
  "electric-guitars": "fender",
  "acoustic-guitars": "lag",
  "bass-guitars": "spector",
  "guitar-amps": "marshall",
  "guitar-pedals": "boss",
  "folk-instruments": "vintage",
  "guitar-accessories": "boss",

  // Drums & Percussion
  "acoustic-drums": "pearl",
  "electronic-drums": "roland",
  "cymbals": "paiste",
  "percussion-instruments": "gon-bops",
  "drum-hardware": "pearl",

  // Keys & Synths
  "digital-pianos": "nord",
  "synthesizers": "moog",
  "production-keyboards": "arturia",
  "keys-accessories": "nord",

  // Studio & Recording
  "studio-monitors": "krk",
  "audio-interfaces": "universalaudio",
  "microphones": "universal-audio",
  "studio-accessories": "warmaudio",

  // Live & DJ
  "pa-speakers": "rcf",
  "mixers": "mackie",
  "live-sound-accessories": "mackie",

  // General & Accessories
  "accessories": "boss",
  "general": "default",
};

/**
 * Extract brand from spectrum ID
 * Maps spectrum category to primary brand
 * 
 * Example: "electric-guitars" → "fender"
 * Example: "studio-monitors" → "krk"
 */
export const extractBrandFromSpectrumId = (spectrumId: string): string => {
  const brand = SPECTRUM_BRAND_MAP[spectrumId];
  return brand || "default";
};

/**
 * Get brand display name (capitalized, readable format)
 * Example: "fender" → "Fender"
 * Example: "adam-audio" → "Adam Audio"
 */
export const getBrandDisplayName = (brand: string): string => {
  const displayNameMap: Record<string, string> = {
    fender: "Fender",
    gibson: "Gibson",
    ibanez: "Ibanez",
    vintage: "Vintage",
    solar: "Solar",
    washburn: "Washburn",
    rapier: "Rapier",
    marshall: "Marshall",
    orange: "Orange",
    vox: "Vox",
    ampeg: "Ampeg",
    boss: "Boss",
    roland: "Roland",
    nord: "Nord",
    moog: "Moog",
    arturia: "Arturia",
    teenageengineering: "Teenage Engineering",
    admaudio: "Adam Audio",
    krk: "KRK",
    universalaudio: "Universal Audio",
    warmaudio: "Warm Audio",
    mackie: "Mackie",
    rcf: "RCF",
    akaiprofessional: "Akai Professional",
    paiste: "Paiste",
    "gon-bops": "Gon Bops",
    spector: "Spector",
    lag: "Lag",
    "default": "General",
  };

  return displayNameMap[brand.toLowerCase().replace(/[^a-z0-9]/g, "")] || brand;
};

/**
 * Verify if a brand is recognized/supported
 */
export const isBrandSupported = (brand: string): boolean => {
  return brand !== "default" && Object.values(SPECTRUM_BRAND_MAP).includes(brand);
};

/**
 * Get all supported brands (for UI filters, etc.)
 */
export const getSupportedBrands = (): string[] => {
  return Object.values(SPECTRUM_BRAND_MAP)
    .filter((brand) => brand !== "default")
    .filter((brand, index, arr) => arr.indexOf(brand) === index) // Remove duplicates
    .sort();
};

/**
 * Batch extract brands from multiple spectrum IDs
 */
export const extractBrandsFromSpectrumIds = (
  spectrumIds: string[]
): string[] => {
  return spectrumIds
    .map((id) => extractBrandFromSpectrumId(id))
    .filter((brand, index, arr) => arr.indexOf(brand) === index); // Remove duplicates
};

/**
 * Generate fallback brand color if not found in theme system
 * Uses simple hash-based color generation
 */
export const generateBrandColor = (brand: string): string => {
  // Fallback colors for brands without explicit theme
  const fallbackColors = [
    "#3b82f6", // Blue
    "#ef4444", // Red
    "#f59e0b", // Amber
    "#10b981", // Green
    "#8b5cf6", // Purple
    "#ec4899", // Pink
  ];

  let hash = 0;
  for (let i = 0; i < brand.length; i++) {
    hash = brand.charCodeAt(i) + ((hash << 5) - hash);
  }

  return fallbackColors[Math.abs(hash) % fallbackColors.length];
};
