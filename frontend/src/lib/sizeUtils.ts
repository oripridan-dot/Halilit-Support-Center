/**
 * Size Utilities
 * 
 * Extracts and normalizes product dimensions from specs
 * to enable visual size comparisons between variants
 */

export interface ProductDimensions {
  height?: number; // in cm
  width?: number; // in cm
  depth?: number; // in cm
  weight?: number; // in kg
  volume?: number; // calculated volume in cm³
}

/**
 * Extract dimensions from product specs
 * Handles various formats: "45 cm", "45cm", "45", "45x30x20", etc.
 */
export function extractDimensions(specs: Record<string, any>): ProductDimensions | null {
  if (!specs || typeof specs !== "object") return null;

  const dimensions: ProductDimensions = {};
  let foundAny = false;

  // Common dimension field names (case-insensitive)
  const heightKeys = ["height", "h", "højde", "גובה", "altura", "hauteur"];
  const widthKeys = ["width", "w", "bredde", "רוחב", "ancho", "largeur"];
  const depthKeys = ["depth", "d", "dybde", "עומק", "profundidad", "profondeur"];
  const weightKeys = ["weight", "w", "vægt", "משקל", "peso", "poids", "kg"];

  // Try to find dimensions
  for (const [key, value] of Object.entries(specs)) {
    const keyLower = key.toLowerCase().replace(/[_\s-]/g, "");

    // Height
    if (!dimensions.height && heightKeys.some(k => keyLower.includes(k))) {
      const parsed = parseDimension(value);
      if (parsed !== null) {
        dimensions.height = parsed;
        foundAny = true;
      }
    }

    // Width
    if (!dimensions.width && widthKeys.some(k => keyLower.includes(k))) {
      const parsed = parseDimension(value);
      if (parsed !== null) {
        dimensions.width = parsed;
        foundAny = true;
      }
    }

    // Depth
    if (!dimensions.depth && depthKeys.some(k => keyLower.includes(k))) {
      const parsed = parseDimension(value);
      if (parsed !== null) {
        dimensions.depth = parsed;
        foundAny = true;
      }
    }

    // Weight
    if (!dimensions.weight && weightKeys.some(k => keyLower.includes(k))) {
      const parsed = parseWeight(value);
      if (parsed !== null) {
        dimensions.weight = parsed;
        foundAny = true;
      }
    }

    // Try to parse combined format: "45 x 30 x 20 cm" or "45x30x20"
    if (!dimensions.height || !dimensions.width || !dimensions.depth) {
      const combinedMatch = String(value).match(/(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)/i);
      if (combinedMatch) {
        dimensions.width = parseFloat(combinedMatch[1]);
        dimensions.height = parseFloat(combinedMatch[2]);
        dimensions.depth = parseFloat(combinedMatch[3]);
        foundAny = true;
      }
    }
  }

  // Calculate volume if we have all three dimensions
  if (dimensions.height && dimensions.width && dimensions.depth) {
    dimensions.volume = dimensions.height * dimensions.width * dimensions.depth;
  }

  return foundAny ? dimensions : null;
}

/**
 * Parse a dimension value (handles "45 cm", "45cm", "45", etc.)
 */
function parseDimension(value: any): number | null {
  if (typeof value === "number") return value;
  if (typeof value !== "string") return null;

  // Remove common separators and extract number
  const match = value.match(/(\d+(?:\.\d+)?)/);
  if (!match) return null;

  const num = parseFloat(match[1]);
  if (isNaN(num) || num <= 0) return null;

  // Check if it's in inches and convert to cm
  if (value.toLowerCase().includes("inch") || value.toLowerCase().includes('"')) {
    return num * 2.54; // Convert inches to cm
  }

  return num;
}

/**
 * Parse a weight value (handles "5 kg", "5000 g", "5kg", etc.)
 */
function parseWeight(value: any): number | null {
  if (typeof value === "number") return value;
  if (typeof value !== "string") return null;

  const match = value.match(/(\d+(?:\.\d+)?)/);
  if (!match) return null;

  const num = parseFloat(match[1]);
  if (isNaN(num) || num <= 0) return null;

  // Convert grams to kg
  if (value.toLowerCase().includes("g") && !value.toLowerCase().includes("kg")) {
    return num / 1000;
  }

  return num;
}

/**
 * Calculate relative size ratio between two products
 * Returns a ratio (0-1) representing how much larger product2 is compared to product1
 */
export function calculateSizeRatio(
  dim1: ProductDimensions | null,
  dim2: ProductDimensions | null
): number | null {
  if (!dim1 || !dim2) return null;

  // Use volume if available (most accurate)
  if (dim1.volume && dim2.volume) {
    return dim2.volume / dim1.volume;
  }

  // Otherwise use average of dimensions
  const avg1 = dim1.height && dim1.width && dim1.depth
    ? (dim1.height + dim1.width + dim1.depth) / 3
    : null;
  const avg2 = dim2.height && dim2.width && dim2.depth
    ? (dim2.height + dim2.width + dim2.depth) / 3
    : null;

  if (!avg1 || !avg2) return null;

  return avg2 / avg1;
}

/**
 * Format dimensions for display
 */
export function formatDimensions(dim: ProductDimensions | null): string {
  if (!dim) return "Size not available";

  const parts: string[] = [];

  if (dim.width) parts.push(`W: ${dim.width.toFixed(1)} cm`);
  if (dim.height) parts.push(`H: ${dim.height.toFixed(1)} cm`);
  if (dim.depth) parts.push(`D: ${dim.depth.toFixed(1)} cm`);
  if (dim.weight) parts.push(`${dim.weight.toFixed(1)} kg`);

  return parts.length > 0 ? parts.join(" • ") : "Size not available";
}

/**
 * Get size category label (Small, Medium, Large, etc.)
 */
export function getSizeCategory(dim: ProductDimensions | null): string {
  if (!dim || !dim.volume) return "Unknown";

  // Rough categorization based on volume (cm³)
  if (dim.volume < 10000) return "Compact";
  if (dim.volume < 50000) return "Small";
  if (dim.volume < 150000) return "Medium";
  if (dim.volume < 500000) return "Large";
  return "Extra Large";
}
