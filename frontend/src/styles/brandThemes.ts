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
