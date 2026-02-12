/**
 * Brand Themes & Color System
 * Defines visual DNA for each brand including:
 * - Primary & secondary colors
 * - Emissive colors for 3D lighting
 * - Lighting intensity for environments
 * 
 * All colors are in hex format for consistency
 */

export interface BrandTheme {
  primary: string;
  secondary: string;
  emissive: string;
  intensity: number;
}

export const brandThemes: Record<string, BrandTheme> = {
  // Guitars & Bass
  fender: {
    primary: "#FF0000",
    secondary: "#F5D033",
    emissive: "#FF4444",
    intensity: 1.5,
  },
  gibson: {
    primary: "#E29132",
    secondary: "#3C2012",
    emissive: "#FF9900",
    intensity: 1.2,
  },
  ibanez: {
    primary: "#8C1F2B",
    secondary: "#000000",
    emissive: "#D32F2F",
    intensity: 1.4,
  },
  vintage: {
    primary: "#DEB887",
    secondary: "#8B4513",
    emissive: "#FFD700",
    intensity: 0.8,
  },
  solar: {
    primary: "#FF0000",
    secondary: "#000000",
    emissive: "#FF0000",
    intensity: 2.0,
  },
  washburn: {
    primary: "#1a1a1a",
    secondary: "#8B7355",
    emissive: "#FFB347",
    intensity: 1.0,
  },
  rapier: {
    primary: "#2C2C2C",
    secondary: "#FFD700",
    emissive: "#FFD700",
    intensity: 1.3,
  },

  // Amps
  marshall: {
    primary: "#FFFFFF",
    secondary: "#111111",
    emissive: "#FFFFFF",
    intensity: 1.0,
  },
  orange: {
    primary: "#FF7F00",
    secondary: "#000000",
    emissive: "#FFA500",
    intensity: 1.5,
  },
  vox: {
    primary: "#FF8C00",
    secondary: "#2F1B0C",
    emissive: "#FF4500",
    intensity: 1.3,
  },
  ampeg: {
    primary: "#1a1a1a",
    secondary: "#FFD700",
    emissive: "#FFD700",
    intensity: 1.2,
  },
  boss: {
    primary: "#0055a4",
    secondary: "#FFD700",
    emissive: "#06b6d4",
    intensity: 1.4,
  },
  roland: {
    primary: "#f89a1c",
    secondary: "#000000",
    emissive: "#FF6600",
    intensity: 1.5,
  },

  // Keys & Synths
  nord: {
    primary: "#e31e24",
    secondary: "#550000",
    emissive: "#FF0033",
    intensity: 1.8,
  },
  moog: {
    primary: "#111111",
    secondary: "#8B4513",
    emissive: "#FFFFFF",
    intensity: 0.6,
  },
  arturia: {
    primary: "#0055a4",
    secondary: "#FFD700",
    emissive: "#0055a4",
    intensity: 1.3,
  },
  teenageengineering: {
    primary: "#ff4d00",
    secondary: "#000000",
    emissive: "#ff4d00",
    intensity: 1.6,
  },

  // Studio & Recording
  admaudio: {
    primary: "#000000",
    secondary: "#FFD700",
    emissive: "#FFD700",
    intensity: 1.0,
  },
  krk: {
    primary: "#ffcc00",
    secondary: "#000000",
    emissive: "#ffcc00",
    intensity: 1.4,
  },
  universalaudio: {
    primary: "#1f2937",
    secondary: "#FFD700",
    emissive: "#FFD700",
    intensity: 1.0,
  },
  warmaudio: {
    primary: "#ea580c",
    secondary: "#000000",
    emissive: "#ea580c",
    intensity: 1.2,
  },
  // New Additions
  neumann: {
    primary: "#1e293b", // Slate 800
    secondary: "#cbd5e1",
    emissive: "#94a3b8",
    intensity: 1.0,
  },
  focal: {
    primary: "#b91c1c", // Red 700
    secondary: "#000000",
    emissive: "#ef4444",
    intensity: 1.4,
  },
  rode: {
    primary: "#ca8a04", // Yellow 600 (Gold-ish)
    secondary: "#000000",
    emissive: "#eab308",
    intensity: 1.3,
  },
  shure: {
    primary: "#15803d", // Green 700
    secondary: "#000000",
    emissive: "#22c55e",
    intensity: 1.2,
  },

  // Live & PA
  mackie: {
    primary: "#00a651",
    secondary: "#000000",
    emissive: "#8dc63f",
    intensity: 1.3,
  },
  rcf: {
    primary: "#000000",
    secondary: "#FFFFFF",
    emissive: "#FF0000",
    intensity: 1.2,
  },
  akaiprofessional: {
    primary: "#ff0000",
    secondary: "#000000",
    emissive: "#ff0000",
    intensity: 1.5,
  },

  // Additional Brands (logo-matched)
  adams: { primary: "#1e3a5f", secondary: "#c0c0c0", emissive: "#4a90d9", intensity: 1.0 },
  allenheath: { primary: "#003366", secondary: "#ffffff", emissive: "#0066cc", intensity: 1.2 },
  amphion: { primary: "#1a1a1a", secondary: "#e0c868", emissive: "#d4af37", intensity: 1.0 },
  antigua: { primary: "#8b6914", secondary: "#2c1810", emissive: "#daa520", intensity: 0.9 },
  ashdownengineering: { primary: "#005599", secondary: "#ffffff", emissive: "#0088ff", intensity: 1.3 },
  ashdown: { primary: "#005599", secondary: "#ffffff", emissive: "#0088ff", intensity: 1.3 },
  asm: { primary: "#111111", secondary: "#00d4ff", emissive: "#00d4ff", intensity: 1.5 },
  austrianaudio: { primary: "#e31e24", secondary: "#1a1a1a", emissive: "#ff3333", intensity: 1.4 },
  avid: { primary: "#0072bc", secondary: "#ffffff", emissive: "#0088ff", intensity: 1.2 },
  bespeco: { primary: "#cc0000", secondary: "#1a1a1a", emissive: "#ff0000", intensity: 1.1 },
  bohemian: { primary: "#2e4057", secondary: "#ffb400", emissive: "#ffd700", intensity: 1.0 },
  breedlove: { primary: "#5c3d2e", secondary: "#d4a574", emissive: "#deb887", intensity: 0.8 },
  breedloveguitars: { primary: "#5c3d2e", secondary: "#d4a574", emissive: "#deb887", intensity: 0.8 },
  cordoba: { primary: "#8b0000", secondary: "#f5deb3", emissive: "#cd5c5c", intensity: 1.0 },
  cordobaguitars: { primary: "#8b0000", secondary: "#f5deb3", emissive: "#cd5c5c", intensity: 1.0 },
  dixon: { primary: "#c41e3a", secondary: "#1a1a1a", emissive: "#ff2244", intensity: 1.3 },
  drumdots: { primary: "#1a1a1a", secondary: "#ffffff", emissive: "#666666", intensity: 0.7 },
  dynaudio: { primary: "#1a1a1a", secondary: "#aaaaaa", emissive: "#888888", intensity: 0.9 },
  eden: { primary: "#003300", secondary: "#66cc33", emissive: "#33ff00", intensity: 1.2 },
  encore: { primary: "#cc0033", secondary: "#000000", emissive: "#ff0044", intensity: 1.1 },
  esp: { primary: "#1a1a1a", secondary: "#ff0000", emissive: "#ff0000", intensity: 1.6 },
  eveaudio: { primary: "#0066cc", secondary: "#c0c0c0", emissive: "#0088ff", intensity: 1.3 },
  expressivee: { primary: "#6a0dad", secondary: "#000000", emissive: "#8b00ff", intensity: 1.4 },
  foxgear: { primary: "#ff6600", secondary: "#000000", emissive: "#ff8800", intensity: 1.5 },
  fusion: { primary: "#333333", secondary: "#ff4444", emissive: "#ff2222", intensity: 1.0 },
  fzone: { primary: "#005599", secondary: "#ffcc00", emissive: "#0088ff", intensity: 1.1 },
  gonbops: { primary: "#8b4513", secondary: "#daa520", emissive: "#cd853f", intensity: 1.0 },
  gonbopspercussion: { primary: "#8b4513", secondary: "#daa520", emissive: "#cd853f", intensity: 1.0 },
  guild: { primary: "#c8a82e", secondary: "#1a1a1a", emissive: "#ffd700", intensity: 1.2 },
  headrushfx: { primary: "#00cc66", secondary: "#000000", emissive: "#00ff88", intensity: 1.5 },
  innovativepercussion: { primary: "#2e4057", secondary: "#cd853f", emissive: "#daa520", intensity: 0.9 },
  jasmine: { primary: "#4a2c2a", secondary: "#f5deb3", emissive: "#d2b48c", intensity: 0.8 },
  jasmineguitars: { primary: "#4a2c2a", secondary: "#f5deb3", emissive: "#d2b48c", intensity: 0.8 },
  keithmcmillen: { primary: "#333333", secondary: "#00ccff", emissive: "#00ccff", intensity: 1.3 },
  lag: { primary: "#003366", secondary: "#cc9933", emissive: "#336699", intensity: 1.0 },
  lagguitars: { primary: "#003366", secondary: "#cc9933", emissive: "#336699", intensity: 1.0 },
  lynx: { primary: "#1a1a1a", secondary: "#0099cc", emissive: "#00bbee", intensity: 1.2 },
  maestro: { primary: "#000000", secondary: "#ffd700", emissive: "#ffd700", intensity: 1.3 },
  magma: { primary: "#cc0000", secondary: "#1a1a1a", emissive: "#ff3300", intensity: 1.5 },
  marimbaone: { primary: "#5c3d2e", secondary: "#f0c040", emissive: "#daa520", intensity: 1.0 },
  maton: { primary: "#2c1810", secondary: "#d4a574", emissive: "#cd853f", intensity: 0.9 },
  matonguitars: { primary: "#2c1810", secondary: "#d4a574", emissive: "#cd853f", intensity: 0.9 },
  maudio: { primary: "#0055aa", secondary: "#ffffff", emissive: "#0077cc", intensity: 1.2 },
  maybach: { primary: "#1a1a1a", secondary: "#c9a84c", emissive: "#daa520", intensity: 1.1 },
  medeli: { primary: "#003399", secondary: "#ffffff", emissive: "#0055ff", intensity: 1.1 },
  montarbo: { primary: "#cc0000", secondary: "#1a1a1a", emissive: "#ff0000", intensity: 1.2 },
  oberheim: { primary: "#1a1a1a", secondary: "#ff6600", emissive: "#ff8800", intensity: 1.3 },
  onstage: { primary: "#333333", secondary: "#ffffff", emissive: "#888888", intensity: 0.8 },
  oscarschmidt: { primary: "#4a2c2a", secondary: "#daa520", emissive: "#cd853f", intensity: 0.9 },
  paiste: { primary: "#000000", secondary: "#d4af37", emissive: "#ffd700", intensity: 1.4 },
  paistecymbals: { primary: "#000000", secondary: "#d4af37", emissive: "#ffd700", intensity: 1.4 },
  pearl: { primary: "#cc0000", secondary: "#ffffff", emissive: "#ff2222", intensity: 1.5 },
  presonus: { primary: "#0066cc", secondary: "#ffffff", emissive: "#0088ff", intensity: 1.2 },
  regaltip: { primary: "#8b4513", secondary: "#ffffff", emissive: "#cd853f", intensity: 0.9 },
  remo: { primary: "#0055aa", secondary: "#ffffff", emissive: "#0077dd", intensity: 1.2 },
  rhythmtech: { primary: "#cc6600", secondary: "#000000", emissive: "#ff8800", intensity: 1.1 },
  rogers: { primary: "#1a1a1a", secondary: "#c0c0c0", emissive: "#aaaaaa", intensity: 0.9 },
  santosmartinez: { primary: "#8b0000", secondary: "#f5deb3", emissive: "#cd5c5c", intensity: 0.9 },
  sequential: { primary: "#0066aa", secondary: "#ffffff", emissive: "#0088dd", intensity: 1.3 },
  show: { primary: "#333333", secondary: "#ffffff", emissive: "#888888", intensity: 0.8 },
  spector: { primary: "#1a1a1a", secondary: "#8b0000", emissive: "#cc0000", intensity: 1.3 },
  steinberg: { primary: "#003366", secondary: "#66ccff", emissive: "#00aaff", intensity: 1.2 },
  studiologic: { primary: "#cc0000", secondary: "#ffffff", emissive: "#ff2222", intensity: 1.2 },
  tombo: { primary: "#cc0000", secondary: "#ffffff", emissive: "#ff0000", intensity: 1.0 },
  topppro: { primary: "#0055aa", secondary: "#000000", emissive: "#0077cc", intensity: 1.1 },
  turkish: { primary: "#c8a82e", secondary: "#1a1a1a", emissive: "#ffd700", intensity: 1.2 },
  vmoda: { primary: "#1a1a1a", secondary: "#c0c0c0", emissive: "#ffffff", intensity: 1.0 },
  xotic: { primary: "#000000", secondary: "#00ccff", emissive: "#00ccff", intensity: 1.4 },
  xvive: { primary: "#ff6600", secondary: "#000000", emissive: "#ff8800", intensity: 1.3 },

  // Default fallback
  default: {
    primary: "#4A90E2",
    secondary: "#1C1C1C",
    emissive: "#4A90E2",
    intensity: 1.0,
  },
};

/**
 * Get brand theme by name (case-insensitive, handles special chars)
 */
export const getBrandTheme = (brandName: string): BrandTheme => {
  const key = brandName
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(0, 30); // Limit key length
  return brandThemes[key] || brandThemes["default"];
};

/**
 * Get theme by exact key match (for internal use)
 */
export const getThemeByKey = (key: string): BrandTheme => {
  return brandThemes[key] || brandThemes["default"];
};
