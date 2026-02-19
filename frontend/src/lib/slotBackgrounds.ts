/**
 * Slot Background Mappings
 * Maps product categories to contextual background images for:
 *   1. Galaxy Dashboard category slots
 *   2. Product Cockpit contextual backgrounds
 *   3. Contextual Response wrappers
 *
 * Each config includes an overlayColor for brand-tinted glassmorphism.
 */

export interface BackgroundConfig {
  imageUrl: string;
  fallbackGradient: string;
  overlayColor: string; // Tint color for glassmorphism overlay (rgba)
  label: string;
}

const BACKGROUNDS: Record<string, BackgroundConfig> = {
  // Electric Guitars — Stage & Amps
  "electric-guitars": {
    imageUrl: "/assets/bg/stage-amps-blur.jpg",
    fallbackGradient: "linear-gradient(135deg, #2a1a0a 0%, #1a0a00 50%, #4a3a2a 100%)",
    overlayColor: "rgba(255, 120, 20, 0.08)",
    label: "Stage & Amps",
  },
  // Acoustic Guitars — Luthier Workshop
  "acoustic-guitars": {
    imageUrl: "/assets/bg/luthier-wood-shop.jpg",
    fallbackGradient: "linear-gradient(135deg, #3a2a1a 0%, #2a1a0a 50%, #1a0a00 100%)",
    overlayColor: "rgba(210, 170, 100, 0.08)",
    label: "Luthier Workshop",
  },
  // Bass Guitars — Dark Rig
  "bass-guitars": {
    imageUrl: "/assets/bg/bass-rig-dark.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a2a 0%, #0a0a1a 50%, #2a1a1a 100%)",
    overlayColor: "rgba(60, 100, 200, 0.08)",
    label: "Bass Rig",
  },
  // Drums & Percussion — Stage Lights
  drums: {
    imageUrl: "/assets/bg/drum-stage-lights.jpg",
    fallbackGradient: "linear-gradient(135deg, #2a1a3a 0%, #1a0a2a 50%, #3a1a2a 100%)",
    overlayColor: "rgba(180, 60, 200, 0.08)",
    label: "Stage Lights",
  },
  // Piano & Keys — Concert Hall
  keys: {
    imageUrl: "/assets/bg/concert-hall.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a2a1a 100%)",
    overlayColor: "rgba(200, 160, 60, 0.08)",
    label: "Concert Hall",
  },
  // Synthesizers — Modular Wall
  synth: {
    imageUrl: "/assets/bg/modular-synth-wall.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a2a 0%, #0a1a2a 50%, #1a0a1a 100%)",
    overlayColor: "rgba(0, 200, 255, 0.08)",
    label: "Modular Synth",
  },
  // Studio & Recording — Mixing Desk
  studio: {
    imageUrl: "/assets/bg/studio-mixing-desk.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a1a0a 100%)",
    overlayColor: "rgba(60, 120, 200, 0.06)",
    label: "Studio Desk",
  },
  // Microphones — Vocal Booth
  vocal: {
    imageUrl: "/assets/bg/vocal-booth.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #1a1a2a 100%)",
    overlayColor: "rgba(200, 160, 80, 0.08)",
    label: "Vocal Booth",
  },
  // PA & Live Sound — Festival
  live: {
    imageUrl: "/assets/bg/outdoor-festival-crowd.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a0a0a 0%, #0a0a1a 50%, #2a1a1a 100%)",
    overlayColor: "rgba(255, 60, 60, 0.06)",
    label: "Festival Stage",
  },
  // Percussion (distinct from drums kit)
  percussion: {
    imageUrl: "/assets/bg/drum-stage-lights.jpg",
    fallbackGradient: "linear-gradient(135deg, #2a1a1a 0%, #1a0a1a 50%, #3a2a1a 100%)",
    overlayColor: "rgba(200, 100, 40, 0.08)",
    label: "Percussion Stage",
  },
  // Piano (standalone, not general keys)
  piano: {
    imageUrl: "/assets/bg/concert-hall.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a0a 0%, #0a0a0a 50%, #2a2a1a 100%)",
    overlayColor: "rgba(180, 140, 40, 0.08)",
    label: "Grand Piano Hall",
  },
  // Headphones
  headphones: {
    imageUrl: "/assets/bg/studio-mixing-desk.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a2a 0%, #0a0a1a 50%, #1a1a1a 100%)",
    overlayColor: "rgba(100, 100, 200, 0.08)",
    label: "Studio Session",
  },
  // DJ Equipment
  dj: {
    imageUrl: "/assets/bg/outdoor-festival-crowd.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a0a2a 0%, #0a0a1a 50%, #2a1a2a 100%)",
    overlayColor: "rgba(200, 0, 255, 0.08)",
    label: "DJ Stage",
  },
  // Default fallback
  default: {
    imageUrl: "/assets/bg/general-store-blur.jpg",
    fallbackGradient: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)",
    overlayColor: "rgba(100, 100, 100, 0.06)",
    label: "General Store",
  },
};

/**
 * Get background configuration based on category ID.
 * Uses explicit switch for known IDs, then fuzzy fallback.
 */
export const getContextBackground = (categoryId: string): BackgroundConfig => {
  switch (categoryId) {
    // --- GUITARS ---
    case "electric-guitars":
    case "guitar-amps":
    case "guitar-pedals":
      return BACKGROUNDS["electric-guitars"];

    case "acoustic-guitars":
    case "folk-instruments":
    case "guitar-accessories":
      return BACKGROUNDS["acoustic-guitars"];

    case "bass-guitars":
      return BACKGROUNDS["bass-guitars"];

    // --- DRUMS ---
    case "acoustic-drums":
    case "electronic-drums":
    case "cymbals":
    case "snares":
    case "sticks-heads":
    case "drum-hardware":
      return BACKGROUNDS["drums"];

    case "percussion":
      return BACKGROUNDS["percussion"];

    // --- KEYS ---
    case "stage-pianos":
    case "keys-accessories":
      return BACKGROUNDS["keys"];

    case "piano":
    case "digital-piano":
      return BACKGROUNDS["piano"];

    case "synthesizers":
    case "midi-controllers":
    case "grooveboxes":
    case "eurorack":
      return BACKGROUNDS["synth"];

    // --- STUDIO ---
    case "audio-interfaces":
    case "studio-monitors":
    case "outboard-gear":
    case "software-plugins":
      return BACKGROUNDS["studio"];

    case "studio-microphones":
    case "studio-accessories":
    case "live-mics":
      return BACKGROUNDS["vocal"];

    case "headphones":
    case "studio-headphones":
      return BACKGROUNDS["headphones"];

    // --- LIVE ---
    case "pa-systems":
    case "live-mixers":
    case "lighting":
    case "live-accessories":
      return BACKGROUNDS["live"];

    case "dj-equipment":
    case "dj":
      return BACKGROUNDS["dj"];

    // --- UTILITY ---
    case "power-supplies":
      return BACKGROUNDS["electric-guitars"];

    case "cables":
    case "cases-bags":
    case "stands":
      return BACKGROUNDS["default"];

    default: {
      // Fuzzy fallback
      const cat = categoryId.toLowerCase();
      if (cat.includes("guitar")) return BACKGROUNDS["electric-guitars"];
      if (cat.includes("bass")) return BACKGROUNDS["bass-guitars"];
      if (cat.includes("drum")) return BACKGROUNDS["drums"];
      if (cat.includes("percuss")) return BACKGROUNDS["percussion"];
      if (cat.includes("piano")) return BACKGROUNDS["piano"];
      if (cat.includes("keys") || cat.includes("keyboard")) return BACKGROUNDS["keys"];
      if (cat.includes("synth")) return BACKGROUNDS["synth"];
      if (cat.includes("headphone")) return BACKGROUNDS["headphones"];
      if (cat.includes("studio") || cat.includes("monitor")) return BACKGROUNDS["studio"];
      if (cat.includes("mic")) return BACKGROUNDS["vocal"];
      if (cat.includes("dj")) return BACKGROUNDS["dj"];
      if (cat.includes("pa") || cat.includes("live")) return BACKGROUNDS["live"];
      return BACKGROUNDS["default"];
    }
  }
};

/**
 * Get background for a product's category (for Contextual Response wrapper).
 */
export const getProductBackground = (categoryHint: string): BackgroundConfig => {
  return getContextBackground(categoryHint);
};
