/**
 * Universal Categories - UI Enrichment (v3.0 - Galaxy/Spectrum)
 *
 * Adds "Visual Cortex" (Icons & Thumbnails) to the "Logic Engine".
 * Maps Spectrum IDs to real product thumbnails.
 */

import type { Product } from "../types";
import {
  CONSOLIDATED_CATEGORIES,
  getConsolidatedProductCategory,
  type ConsolidatedCategory,
  type SpectrumDef,
} from "./categoryConsolidator";

export interface SpectrumUIDef extends SpectrumDef {
  image: string;
  glowColor: string; // Brand-specific stage light flavor
}

export interface UniversalCategoryDef extends Omit<
  ConsolidatedCategory,
  "spectrum"
> {
  iconName: string; // Lucide icon name override
  spectrum: SpectrumUIDef[];
}

// Map Spectrum ID -> Thumbnail Path
const SPECTRUM_IMAGES: Record<string, string> = {
  // GUITARS
  "electric-guitars":
    "/data/category_thumbnails/guitars-electric-guitars_thumb.webp",
  "acoustic-guitars":
    "/data/category_thumbnails/guitars-acoustic-guitars_thumb.webp",
  "bass-guitars": "/data/category_thumbnails/guitars-bass-guitars_thumb.webp",
  "guitar-amps": "/data/category_thumbnails/guitars-guitar-amps_thumb.webp",
  "guitar-pedals": "/data/category_thumbnails/guitars-guitar-pedals_thumb.webp",
  "folk-instruments":
    "/data/category_thumbnails/guitars-folk-instruments_thumb.webp",
  "guitar-accessories":
    "/data/category_thumbnails/guitars-guitar-accessories_thumb.webp",

  // DRUMS
  "acoustic-drums": "/data/category_thumbnails/drums-acoustic-drums_thumb.webp",
  "electronic-drums":
    "/data/category_thumbnails/drums-electronic-drums_thumb.webp",
  cymbals: "/data/category_thumbnails/drums-cymbals_thumb.webp",
  snares: "/data/category_thumbnails/drums-snares_thumb.webp",
  "sticks-heads": "/data/category_thumbnails/drums-sticks-heads_thumb.webp",
  percussion: "/data/category_thumbnails/drums-percussion_thumb.webp",
  "drum-hardware": "/data/category_thumbnails/drums-drum-hardware_thumb.webp",

  // KEYS
  synthesizers: "/data/category_thumbnails/keys-synthesizers_thumb.webp",
  "stage-pianos": "/data/category_thumbnails/keys-stage-pianos_thumb.webp",
  "midi-controllers":
    "/data/category_thumbnails/keys-midi-controllers_thumb.webp",
  grooveboxes: "/data/category_thumbnails/keys-grooveboxes_thumb.webp",
  eurorack: "/data/category_thumbnails/keys-eurorack_thumb.webp",
  "keys-accessories":
    "/data/category_thumbnails/keys-keys-accessories_thumb.webp",

  // STUDIO
  "audio-interfaces":
    "/data/category_thumbnails/studio-audio-interfaces_thumb.webp",
  "studio-monitors":
    "/data/category_thumbnails/studio-studio-monitors_thumb.webp",
  "studio-microphones":
    "/data/category_thumbnails/studio-studio-microphones_thumb.webp",
  "outboard-gear": "/data/category_thumbnails/studio-outboard-gear_thumb.webp",
  "software-plugins":
    "/data/category_thumbnails/studio-software-plugins_thumb.webp",
  "studio-accessories":
    "/data/category_thumbnails/studio-studio-accessories_thumb.webp",

  // LIVE
  "pa-systems": "/data/category_thumbnails/live-pa-systems_thumb.webp",
  "live-mixers": "/data/category_thumbnails/live-live-mixers_thumb.webp",
  "dj-equipment": "/data/category_thumbnails/live-dj-equipment_thumb.webp",
  lighting: "/data/category_thumbnails/live-lighting_thumb.webp",
  "live-mics": "/data/category_thumbnails/live-live-mics_thumb.webp",
  "live-accessories":
    "/data/category_thumbnails/live-live-accessories_thumb.webp",

  // UTILITY
  cables: "/data/category_thumbnails/accessories-cables_thumb.webp",
  stands: "/data/category_thumbnails/accessories-stands_thumb.webp",
  "cases-bags": "/data/category_thumbnails/accessories-cases-bags_thumb.webp",
  "power-supplies":
    "/data/category_thumbnails/accessories-power-supplies_thumb.webp",
};

// Brand Colors
const GLOW_COLORS = {
  roland: "#ff8c00", // Roland Orange
  boss: "#06b6d4", // Boss Cyan/Blue
  nord: "#e61d2b", // Nord Red
  generic: "#ffffff", // White
};

// Map Spectrum ID -> Brand Color
const SPECTRUM_GLOW: Record<string, string> = {
  // GUITARS (Boss Dominance)
  "electric-guitars": GLOW_COLORS.boss,
  "acoustic-guitars": GLOW_COLORS.boss,
  "bass-guitars": GLOW_COLORS.boss,
  "guitar-amps": GLOW_COLORS.boss,
  "guitar-pedals": GLOW_COLORS.boss,
  "folk-instruments": GLOW_COLORS.boss,
  "guitar-accessories": GLOW_COLORS.boss,

  // DRUMS (Roland Dominance)
  "acoustic-drums": GLOW_COLORS.roland,
  "electronic-drums": GLOW_COLORS.roland,
  cymbals: GLOW_COLORS.roland,
  snares: GLOW_COLORS.roland,
  "sticks-heads": GLOW_COLORS.roland,
  percussion: GLOW_COLORS.roland,
  "drum-hardware": GLOW_COLORS.roland,

  // KEYS (Mixed: Roland + Nord)
  synthesizers: GLOW_COLORS.roland,
  "stage-pianos": GLOW_COLORS.nord, // RED
  "midi-controllers": GLOW_COLORS.roland,
  grooveboxes: GLOW_COLORS.roland,
  eurorack: GLOW_COLORS.roland,
  "keys-accessories": GLOW_COLORS.roland,

  // STUDIO (Mixed)
  "audio-interfaces": GLOW_COLORS.roland,
  "studio-monitors": GLOW_COLORS.nord, // RED
  "studio-microphones": GLOW_COLORS.roland,
  "outboard-gear": GLOW_COLORS.boss,
  "software-plugins": GLOW_COLORS.roland,
  "studio-accessories": GLOW_COLORS.roland,

  // LIVE
  "pa-systems": GLOW_COLORS.roland,
  "live-mixers": GLOW_COLORS.roland,
  "dj-equipment": GLOW_COLORS.roland,
  lighting: GLOW_COLORS.roland,
  "live-mics": GLOW_COLORS.boss,
  "live-accessories": GLOW_COLORS.boss,

  // UTILITY
  cables: GLOW_COLORS.roland,
  stands: GLOW_COLORS.roland,
  "cases-bags": GLOW_COLORS.roland,
  "power-supplies": GLOW_COLORS.boss,
};

// Map Galaxy ID -> Lucide Icon Name
const GALAXY_ICONS: Record<string, string> = {
  "guitars-bass": "Guitar",
  "drums-percussion": "Music",
  "keys-production": "Piano",
  "studio-recording": "Mic2",
  "live-dj": "Speaker",
  "accessories-utility": "Plug",
};

export const UNIVERSAL_CATEGORIES: UniversalCategoryDef[] =
  CONSOLIDATED_CATEGORIES.map((galaxy) => ({
    ...galaxy,
    iconName: GALAXY_ICONS[galaxy.id] || "HelpCircle",
    spectrum: galaxy.spectrum.map((spec) => ({
      ...spec,
      image:
        SPECTRUM_IMAGES[spec.id] ||
        "/data/category_thumbnails/default_thumb.webp",
      glowColor: SPECTRUM_GLOW[spec.id] || GLOW_COLORS.roland, // Default to Roland Orange
    })),
  }));

export function getUniversalCategory(
  id: string,
): UniversalCategoryDef | undefined {
  return UNIVERSAL_CATEGORIES.find((c) => c.id === id);
}

export function productMatchesSpectrum(
  product: Product,
  spectrumId: string,
): boolean {
  const { spectrumId: productSpectrumId } =
    getConsolidatedProductCategory(product);
  return productSpectrumId === spectrumId;
}
