/**
 * Color Validation & Fallback Utilities
 * Resilient color handling for UI that gracefully degrades on invalid colors
 */

const DEFAULT_BRAND_COLORS = {
    primary: "#3b82f6", // blue-500
    secondary: "#1e293b", // slate-900
};

/**
 * Validates and sanitizes hex color strings
 * Returns a safe hex color or fallback
 */
export function validateHexColor(color: unknown): string {
    if (!color || typeof color !== "string") {
        return DEFAULT_BRAND_COLORS.primary;
    }

    // Trim whitespace
    const trimmed = color.trim();

    // Check if it looks like a hex color (with # prefix)
    if (/^#[0-9a-fA-F]{6}$/.test(trimmed)) {
        return trimmed.toLowerCase();
    }

    // Try to fix common issues
    // Remove spaces
    const noSpaces = trimmed.replace(/\s/g, "");

    // Add # if missing
    const withHash = noSpaces.startsWith("#") ? noSpaces : `#${noSpaces}`;

    // Check again
    if (/^#[0-9a-fA-F]{6}$/.test(withHash)) {
        return withHash.toLowerCase();
    }

    // Last resort: try to use first 6 hex chars
    const hexMatch = withHash.match(/#[0-9a-fA-F]{6}/);
    if (hexMatch) {
        return hexMatch[0].toLowerCase();
    }

    // Completely invalid - return fallback
    console.warn(`Invalid color "${color}" - using fallback`);
    return DEFAULT_BRAND_COLORS.primary;
}

/**
 * Get a safe color pair (primary + secondary) for a brand
 * Ensures colors are always valid
 */
export function getSafeBrandColors(
    primary?: string | null,
    secondary?: string | null
) {
    return {
        primary: validateHexColor(primary),
        secondary: validateHexColor(secondary) || DEFAULT_BRAND_COLORS.secondary,
    };
}

/**
 * Convert hex color to CSS compatible format with opacity
 */
export function hexToRgba(hex: string, opacity: number = 1): string {
    const validHex = validateHexColor(hex);
    const r = parseInt(validHex.slice(1, 3), 16);
    const g = parseInt(validHex.slice(3, 5), 16);
    const b = parseInt(validHex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Check if a color is "dark" (luminance < 0.5)
 * Useful for determining text color
 */
export function isDarkColor(hex: string): boolean {
    const validHex = validateHexColor(hex);
    const r = parseInt(validHex.slice(1, 3), 16);
    const g = parseInt(validHex.slice(3, 5), 16);
    const b = parseInt(validHex.slice(5, 7), 16);

    // Calculate relative luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance < 0.5;
}
