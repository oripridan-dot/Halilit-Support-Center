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
  "electric-guitars": "/data/thumbnails/esp_67_eiihorfrqmrdb.jpg",
  "acoustic-guitars": "/data/thumbnails/breedlove_guitars_17_dscn01euam.jpg",
  "bass-guitars": "/data/thumbnails/spector_69_euro4lx_dw.jpg",
  "guitar-amps": "/data/thumbnails/roland_87-jc120p.jpg",
  "guitar-pedals": "/data/thumbnails/warm_audio_80_wajpjetphaser.jpg",
  "folk-instruments": "/data/thumbnails/cordoba_guitars_76_20tm.jpg",
  "guitar-accessories": "/data/thumbnails/perri_s_leathers_57_1333.jpg",

  // DRUMS
  "acoustic-drums": "/data/thumbnails/pearl_88_mct924xedpc_348.jpg",
  "electronic-drums": "/data/thumbnails/roland_87-vad716sw.jpg",
  cymbals: "/data/thumbnails/paiste_cymbals_90_1061418.jpg",
  snares: "/data/thumbnails/pearl_88_mwa1465s_c.jpg",
  "sticks-heads": "/data/thumbnails/remo_19_am14c.jpg",
  percussion: "/data/thumbnails/gon_bops_percussion_82_aacj.jpg",
  "drum-hardware": "/data/thumbnails/pearl_88_p930.jpg",

  // KEYS
  synthesizers: "/data/thumbnails/moog_29_matriarch.jpg",
  "stage-pianos": "/data/thumbnails/roland_87-rd2000.jpg",
  "midi-controllers": "/data/thumbnails/roland_87-a88mk2.jpg",
  grooveboxes: "/data/thumbnails/roland_87-mc707.jpg",
  eurorack: "/data/thumbnails/moog_29_mother32.jpg",
  "keys-accessories": "/data/thumbnails/roland_87-ks10z.jpg",

  // STUDIO
  "audio-interfaces": "/data/thumbnails/universal_audio_44_apx8he.jpg",
  "studio-monitors": "/data/thumbnails/krk_systems_21_rp5g5.jpg",
  "studio-microphones": "/data/thumbnails/warm_audio_80_wa87r2.jpg",
  "outboard-gear": "/data/thumbnails/warm_audio_80_wa76.jpg",
  "software-plugins": "/data/thumbnails/steinberg__45_dac_cubase_pro.jpg",
  "studio-accessories": "/data/thumbnails/on_stage_65_ms7701b.jpg",

  // LIVE
  "pa-systems": "/data/thumbnails/rcf_61_art912a.jpg",
  "live-mixers": "/data/thumbnails/mackie_60_onyx16.jpg",
  "dj-equipment": "/data/thumbnails/roland_87-dj707m.jpg",
  lighting: "/data/thumbnails/show_03_csb175.jpg",
  "live-mics": "/data/thumbnails/mackie_60_em91c.jpg",
  "live-accessories": "/data/thumbnails/on_stage_65_db200.jpg",

  // UTILITY
  cables: "/data/thumbnails/roland_87-rcc10trtr.jpg",
  stands: "/data/thumbnails/on_stage_65_ks7191.jpg",
  "cases-bags": "/data/thumbnails/fusion_78_ub01bk.jpg",
  "power-supplies": "/data/thumbnails/foxgear_guitar_effects_and_pedals_20_fxp55.jpg",
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
        "/assets/thumbs/electric.svg",
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
