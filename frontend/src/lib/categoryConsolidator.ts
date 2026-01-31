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

  // --- STUDIO ---
  "audio interface": "audio-interfaces",
  "studio monitor": "studio-monitors",
  "condenser microphone": "studio-microphones",
  "ribbon microphone": "studio-microphones",
  "daw": "software-plugins",
  "plugin": "software-plugins",
  "preamp": "outboard-gear",
  "compressor": "outboard-gear",

  // --- LIVE ---
  "pa speaker": "pa-systems",
  "subwoofer": "pa-systems",
  "live mixer": "live-mixers",
  "dj controller": "dj-equipment",
  "turntable": "dj-equipment",
  "wireless microphone": "live-mics",
  "moving head": "lighting",
  "par can": "lighting",
};

// =============================================================================
// CONSOLIDATION FUNCTIONS
// =============================================================================

function getSpectrumId(rawCategoryString: string): string {
  if (!rawCategoryString) return "accessories-utility";

  const normalized = rawCategoryString.toLowerCase();

  // Iterate through map
  for (const [keyword, spectrumId] of Object.entries(SPECTRUM_MAP)) {
    if (normalized.includes(keyword)) {
      return spectrumId;
    }
  }

  // Fallbacks
  if (normalized.includes("cable")) return "cables";
  if (normalized.includes("stand")) return "stands";
  if (normalized.includes("case") || normalized.includes("bag")) return "cases-bags";
  if (normalized.includes("power")) return "power-supplies";

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
  // 0. Priority: v4.6.1 Standard (ui_meta directly on root)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if ((product as any).ui_meta?.primary_category) {
    const primary = (product as any).ui_meta.primary_category;
    const TAXONOMY_BRIDGE: Record<string, string> = {
      "STUDIO_MONITORS": "studio-monitors",
      "AUDIO_INTERFACES": "audio-interfaces",
      "MICROPHONES": "studio-microphones",
      "CONDENSER": "studio-microphones",
      "ACCESSORIES": "accessories-utility",
      "STANDS": "stands",
      "TUNING": "accessories-utility",
      "UNCATEGORIZED": "accessories-utility"
    };

    const spectrumId = TAXONOMY_BRIDGE[primary] || "accessories-utility";
    const galaxy = getGalaxyForSpectrum(spectrumId);

    return {
      spectrumId,
      galaxyId: galaxy?.id || "accessories-utility",
      galaxyLabel: galaxy?.label || "Accessories",
      originalCategory: primary
    };
  }

  // 1. Priority: Use refined UI Context from "Refinery" v5 (pill_data)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pillData = (product as any).pill_data;
  if (pillData?.ui_meta?.primary_category) {
    // Map Backend Taxonomy Keys to Frontend Spectrum IDs
    const TAXONOMY_BRIDGE: Record<string, string> = {
      "STUDIO_MONITORS": "studio-monitors",
      "AUDIO_INTERFACES": "audio-interfaces",
      "MICROPHONES": "studio-microphones",
      "CONDENSER": "studio-microphones",
      "ACCESSORIES": "accessories-utility",
      "STANDS": "stands",
      "TUNING": "accessories-utility",
      "UNCATEGORIZED": "accessories-utility"
    };

    const spectrumId = TAXONOMY_BRIDGE[pillData.ui_meta.primary_category] || "accessories-utility";
    const galaxy = getGalaxyForSpectrum(spectrumId);

    return {
      spectrumId,
      galaxyId: galaxy?.id || "accessories-utility",
      galaxyLabel: galaxy?.label || "Accessories",
      originalCategory: pillData.ui_meta.primary_category
    };
  }

  // 2. Fallback: Use legacy UI Context
  const uiContext = product.ui_context;
  if (uiContext && uiContext.primary) {
    // Map Backend Tax Keys to Frontend Spectrum IDs
    // This is a "Bridge" map until the backend outputs Spectrum IDs directly
    const TAXONOMY_BRIDGE: Record<string, string> = {
      "STUDIO_MONITORS": "studio-monitors",
      "AUDIO_INTERFACES": "audio-interfaces",
      "MICROPHONES": "studio-microphones",
      // Add default mappings for cases where refined data uses generic keys
      "UNCATEGORIZED": "accessories-utility"
    };
    // If it has Sub-Division (e.g. "Subwoofer"), we might map specifically too
    // For now, let's map the Primary Category to Spectrum ID

    let spectrumId = TAXONOMY_BRIDGE[uiContext.primary] || "accessories-utility";

    // Handle special sub-cases if needed (e.g. Subwoofers in backend might match PA vs Studio?)
    // Actually, let's trust the backend primary for now.

    const galaxy = getGalaxyForSpectrum(spectrumId);
    const galaxyId = galaxy ? galaxy.id : "accessories-utility";
    const galaxyLabel = galaxy ? galaxy.label : "General Utility";

    return {
      spectrumId,
      galaxyId,
      galaxyLabel,
      originalCategory: product.category || "Refined",
    };
  }

  const originalCategory = product.category || "Uncategorized";
  const spectrumId = consolidateCategory("unknown", originalCategory);

  // Find which Galaxy this spectrum belongs to
  const galaxy = getGalaxyForSpectrum(spectrumId);
  const galaxyId = galaxy ? galaxy.id : "accessories-utility";
  const galaxyLabel = galaxy ? galaxy.label : "General Utility";

  return {
    spectrumId,
    galaxyId,
    galaxyLabel,
    originalCategory,
  };
}

export function productMatchesGalaxy(
  product: Product,
  galaxyId: string
): boolean {
  if (galaxyId === "all") return true;
  const { galaxyId: pGalaxyId } = getConsolidatedProductCategory(product);
  return pGalaxyId === galaxyId;
}
