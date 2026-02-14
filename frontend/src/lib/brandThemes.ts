/**
 * Brand Themes — "Chameleon Interface"
 *
 * Maps brand names to visual themes so the ProductPage
 * can adapt its color accent to the current product's brand.
 * Falls back to a neutral slate theme for unknown brands.
 */

export interface BrandVisualTheme {
    /** Primary accent color (CSS) */
    primary: string;
    /** Secondary / lighter accent */
    secondary: string;
    /** Tailwind bg class for subtle tint */
    bgTint: string;
    /** Tailwind border class */
    borderTint: string;
    /** Tailwind text class */
    textAccent: string;
}

const BRAND_THEMES: Record<string, BrandVisualTheme> = {
    // Percussion & drums
    'Meinl': { primary: '#e2b714', secondary: '#f5d855', bgTint: 'bg-yellow-500/5', borderTint: 'border-yellow-500/20', textAccent: 'text-yellow-400' },
    'Remo': { primary: '#d32f2f', secondary: '#ef5350', bgTint: 'bg-red-500/5', borderTint: 'border-red-500/20', textAccent: 'text-red-400' },
    'LP': { primary: '#1565c0', secondary: '#42a5f5', bgTint: 'bg-blue-500/5', borderTint: 'border-blue-500/20', textAccent: 'text-blue-400' },
    'Toca': { primary: '#00897b', secondary: '#4db6ac', bgTint: 'bg-teal-500/5', borderTint: 'border-teal-500/20', textAccent: 'text-teal-400' },
    'Nino': { primary: '#ff8f00', secondary: '#ffb74d', bgTint: 'bg-amber-500/5', borderTint: 'border-amber-500/20', textAccent: 'text-amber-400' },

    // Guitars & strings
    'Fender': { primary: '#c62828', secondary: '#e57373', bgTint: 'bg-red-500/5', borderTint: 'border-red-500/20', textAccent: 'text-red-400' },
    'Gibson': { primary: '#f57f17', secondary: '#fdd835', bgTint: 'bg-yellow-500/5', borderTint: 'border-yellow-500/20', textAccent: 'text-yellow-400' },
    'Ibanez': { primary: '#1a237e', secondary: '#5c6bc0', bgTint: 'bg-indigo-500/5', borderTint: 'border-indigo-500/20', textAccent: 'text-indigo-400' },
    'Yamaha': { primary: '#6a1b9a', secondary: '#ab47bc', bgTint: 'bg-purple-500/5', borderTint: 'border-purple-500/20', textAccent: 'text-purple-400' },
    'Taylor': { primary: '#33691e', secondary: '#7cb342', bgTint: 'bg-green-500/5', borderTint: 'border-green-500/20', textAccent: 'text-green-400' },
    'Martin': { primary: '#4e342e', secondary: '#8d6e63', bgTint: 'bg-amber-500/5', borderTint: 'border-amber-500/20', textAccent: 'text-amber-400' },

    // Keys
    'Roland': { primary: '#b71c1c', secondary: '#ef5350', bgTint: 'bg-red-500/5', borderTint: 'border-red-500/20', textAccent: 'text-red-400' },
    'Korg': { primary: '#0d47a1', secondary: '#42a5f5', bgTint: 'bg-blue-500/5', borderTint: 'border-blue-500/20', textAccent: 'text-blue-400' },
    'Casio': { primary: '#1b5e20', secondary: '#66bb6a', bgTint: 'bg-green-500/5', borderTint: 'border-green-500/20', textAccent: 'text-green-400' },
    'Nord': { primary: '#c62828', secondary: '#ef5350', bgTint: 'bg-red-500/5', borderTint: 'border-red-500/20', textAccent: 'text-red-400' },

    // Wind
    'Hohner': { primary: '#1565c0', secondary: '#42a5f5', bgTint: 'bg-blue-500/5', borderTint: 'border-blue-500/20', textAccent: 'text-blue-400' },
    'Nuvo': { primary: '#00bcd4', secondary: '#4dd0e1', bgTint: 'bg-cyan-500/5', borderTint: 'border-cyan-500/20', textAccent: 'text-cyan-400' },

    // Audio & PA
    'Shure': { primary: '#263238', secondary: '#546e7a', bgTint: 'bg-slate-500/5', borderTint: 'border-slate-500/20', textAccent: 'text-slate-300' },
    'Sennheiser': { primary: '#1a237e', secondary: '#5c6bc0', bgTint: 'bg-indigo-500/5', borderTint: 'border-indigo-500/20', textAccent: 'text-indigo-400' },
    'JBL': { primary: '#ff6f00', secondary: '#ffa726', bgTint: 'bg-orange-500/5', borderTint: 'border-orange-500/20', textAccent: 'text-orange-400' },
    'Harman': { primary: '#37474f', secondary: '#78909c', bgTint: 'bg-slate-500/5', borderTint: 'border-slate-500/20', textAccent: 'text-slate-300' },

    // Education
    'Boomwhackers': { primary: '#e91e63', secondary: '#f48fb1', bgTint: 'bg-pink-500/5', borderTint: 'border-pink-500/20', textAccent: 'text-pink-400' },
    'Angel': { primary: '#00bcd4', secondary: '#4dd0e1', bgTint: 'bg-cyan-500/5', borderTint: 'border-cyan-500/20', textAccent: 'text-cyan-400' },
};

const DEFAULT_THEME: BrandVisualTheme = {
    primary: '#3b82f6',
    secondary: '#60a5fa',
    bgTint: 'bg-blue-500/5',
    borderTint: 'border-blue-500/20',
    textAccent: 'text-blue-400',
};

/**
 * Get visual theme for a brand. Case-insensitive lookup.
 */
export function getBrandTheme(brand: string | undefined): BrandVisualTheme {
    if (!brand) return DEFAULT_THEME;
    // Try exact match first, then case-insensitive
    return (
        BRAND_THEMES[brand] ||
        BRAND_THEMES[Object.keys(BRAND_THEMES).find(
            (k) => k.toLowerCase() === brand.toLowerCase(),
        ) || ''] ||
        DEFAULT_THEME
    );
}

/**
 * CSS custom property object for inline brand theming.
 * Use in style={{ ...brandCssVars(brand) }} on a wrapper element.
 */
export function brandCssVars(brand: string | undefined): Record<string, string> {
    const theme = getBrandTheme(brand);
    return {
        '--brand-primary': theme.primary,
        '--brand-secondary': theme.secondary,
    };
}
