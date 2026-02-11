/**
 * Brand Logo Helper - Maps brands to logo paths
 * Extracts brands from products in each category for visual display
 */

import type { Product } from "../types";
import { getConsolidatedProductCategory, getGalaxyForSpectrum } from "./categoryConsolidator";

// Map brand names to their logo file names (in public/assets/logos/)
// Auto-generated from the 92 logos on disk + aliases
const BRAND_LOGO_MAP: Record<string, string> = {
    // --- A ---
    "adam audio": "adam-audio_logo.svg",
    "adam-audio": "adam-audio_logo.svg",
    adams: "adams_logo.jpg",
    "akai professional": "akai-professional_logo.svg",
    "akai-professional": "akai-professional_logo.svg",
    akai: "akai-professional_logo.svg",
    "allen & heath": "allen-heath_logo.png",
    "allen-heath": "allen-heath_logo.png",
    ampeg: "ampeg_logo.jpg",
    amphion: "amphion_logo.png",
    antigua: "antigua_logo.jpg",
    "ashdown engineering": "ashdown-engineering_logo.png",
    "ashdown-engineering": "ashdown-engineering_logo.png",
    ashdown: "ashdown-engineering_logo.png",
    asm: "asm_logo.png",
    "austrian audio": "austrian-audio_logo.png",
    "austrian-audio": "austrian-audio_logo.png",
    avid: "avid_logo.png",
    // --- B ---
    bespeco: "bespeco_logo.png",
    "bohemian ukuleles": "bohemian-ukuleles-guitars-basses_logo.png",
    boss: "boss_logo.png",
    "breedlove guitars": "breedlove-guitars_logo.png",
    "breedlove-guitars": "breedlove-guitars_logo.png",
    breedlove: "breedlove-guitars_logo.png",
    // --- C ---
    "cordoba guitars": "cordoba-guitars_logo.gif",
    "cordoba-guitars": "cordoba-guitars_logo.gif",
    cordoba: "cordoba-guitars_logo.gif",
    // --- D ---
    dixon: "dixon_logo.png",
    drumdots: "drumdots_logo.png",
    dynaudio: "dynaudio_logo.png",
    // --- E ---
    "eaw": "-eaw-eastern-acoustic-works-_logo.png",
    eden: "eden_logo.png",
    encore: "encore_logo.png",
    esp: "esp_logo.jpg",
    "eve audio": "eve-audio_logo.jpg",
    "eve-audio": "eve-audio_logo.jpg",
    "expressive e": "expressive-e_logo.jpg",
    "expressive-e": "expressive-e_logo.jpg",
    // --- F ---
    foxgear: "foxgear-guitar-effects-and-pedals_logo.png",
    fusion: "fusion_logo.png",
    fzone: "fzone_logo.png",
    // --- G ---
    "gon bops": "gon-bops-percussion_logo.jpg",
    "gon-bops": "gon-bops-percussion_logo.jpg",
    guild: "guild_logo.jpg",
    // --- H ---
    headliner: "headliner-la-equipment-stands-_logo.png",
    "headrush fx": "headrush-fx_logo.png",
    "headrush-fx": "headrush-fx_logo.png",
    headrush: "headrush-fx_logo.png",
    // --- I ---
    "innovative percussion": "innovative-percussion_logo.png",
    "innovative-percussion": "innovative-percussion_logo.png",
    // --- J ---
    "jasmine guitars": "jasmine-guitars_logo.png",
    jasmine: "jasmine-guitars_logo.png",
    // --- K ---
    "keith mcmillen": "keith-mcmillen-instruments-kmi_logo.png",
    "keith-mcmillen": "keith-mcmillen-instruments-kmi_logo.png",
    kmi: "keith-mcmillen-instruments-kmi_logo.png",
    "krk systems": "krk-systems_logo.jpg",
    "krk-systems": "krk-systems_logo.jpg",
    krk: "krk-systems_logo.jpg",
    // --- L ---
    "lag guitars": "lag-guitars_logo.jpg",
    "lag-guitars": "lag-guitars_logo.jpg",
    lag: "lag-guitars_logo.jpg",
    lynx: "lynx_logo.png",
    // --- M ---
    "m-audio": "m-audio_logo.jpg",
    "m audio": "m-audio_logo.jpg",
    mackie: "mackie_logo.svg",
    maestro: "maestro-guitar-pedals-and-effects_logo.png",
    magma: "magma_logo.jpg",
    "marimba one": "marimba-one_logo.jpg",
    "marimba-one": "marimba-one_logo.jpg",
    "maton guitars": "maton-guitars_logo.png",
    "maton-guitars": "maton-guitars_logo.png",
    maton: "maton-guitars_logo.png",
    maybach: "maybach_logo.png",
    medeli: "medeli_logo.jpg",
    "mjc ironworks": "mjc-ironworks_logo.jpg",
    montarbo: "montarbo_logo.jpg",
    moog: "moog_logo.png",
    // --- N ---
    nord: "nord_logo.png",
    // --- O ---
    oberheim: "oberheim_logo.png",
    "on-stage": "on-stage_logo.jpg",
    "on stage": "on-stage_logo.jpg",
    "oscar schmidt": "oscar-schmidt-acoustic-guitars-_logo.png",
    "oscar-schmidt": "oscar-schmidt-acoustic-guitars-_logo.png",
    // --- P ---
    paiste: "paiste-cymbals_logo.jpg",
    pearl: "pearl_logo.jpg",
    "perri's leathers": "perri-s-leathers_logo.png",
    "perri-s-leathers": "perri-s-leathers_logo.png",
    presonus: "presonus_logo.png",
    // --- R ---
    rapier: "rapier-33-electric-guitars_logo.png",
    rcf: "rcf_logo.jpg",
    "regal tip": "regal-tip_logo.jpg",
    "regal-tip": "regal-tip_logo.jpg",
    remo: "remo_logo.jpg",
    "rhythm tech": "rhythm-tech_logo.jpg",
    "rhythm-tech": "rhythm-tech_logo.jpg",
    rogers: "rogers_logo.png",
    roland: "roland_logo.png",
    rode: "rode_logo.png",
    // --- S ---
    "santos martinez": "santos-martinez_logo.png",
    "santos-martinez": "santos-martinez_logo.png",
    sequential: "sequential_logo.svg",
    "sequential circuits": "sequential_logo.svg",
    show: "show_logo.png",
    shure: "shure_logo.png",
    "solar guitars": "solar-guitars_logo.jpg",
    "solar-guitars": "solar-guitars_logo.jpg",
    solar: "solar-guitars_logo.jpg",
    spector: "spector_logo.png",
    steinberg: "steinberg-_logo.png",
    "studio logic": "studio-logic_logo.png",
    "studio-logic": "studio-logic_logo.png",
    studiologic: "studio-logic_logo.png",
    // --- T ---
    "teenage engineering": "teenage-engineering_logo.svg",
    "teenage-engineering": "teenage-engineering_logo.svg",
    tombo: "tombo_logo.jpg",
    "topp pro": "topp-pro_logo.png",
    "topp-pro": "topp-pro_logo.png",
    turkish: "turkish_logo.jpg",
    // --- U ---
    "universal audio": "universal-audio_logo.svg",
    "universal-audio": "universal-audio_logo.svg",
    // --- V ---
    "v-moda": "v-moda_logo.png",
    "v moda": "v-moda_logo.png",
    vintage: "vintage_logo.jpg",
    // --- W ---
    "warm audio": "warm-audio_logo.svg",
    "warm-audio": "warm-audio_logo.svg",
    washburn: "washburn_logo.jpg",
    // --- X ---
    xotic: "xotic_logo.png",
    xvive: "xvive_logo.png",
};

/**
 * Get logo URL for a brand
 */
export function getBrandLogoUrl(brandName: string): string | null {
    const normalized = brandName.toLowerCase().trim();
    const logoFile = BRAND_LOGO_MAP[normalized];

    if (!logoFile) {
        return null;
    }

    return `/assets/logos/${logoFile}`;
}

/**
 * Extract unique brands from products in a specific spectrum/category
 * Uses the consolidator to properly map products to spectrum IDs
 */
export function extractBrandsForCategory(
    products: Product[] | any[],
    categoryId: string
): string[] {
    const uniqueBrands = new Set<string>();

    products.forEach((product: any) => {
        try {
            const { spectrumId, galaxyId } = getConsolidatedProductCategory(product);
            // Match by spectrum ID or galaxy ID
            if (spectrumId === categoryId || galaxyId === categoryId) {
                if (product.brand) {
                    uniqueBrands.add(product.brand);
                }
            }
        } catch {
            // Fallback: simple string matching
            const productCategory = product.taxonomy?.canonical_category
                || product.category || '';
            if (productCategory.toString().toLowerCase().includes(categoryId.toLowerCase())) {
                if (product.brand) {
                    uniqueBrands.add(product.brand);
                }
            }
        }
    });

    return Array.from(uniqueBrands).sort();
}

/**
 * Get top brands (with logos) for a category
 * Returns array of { brand, logoUrl } objects, limited to N brands
 */
export function getTopBrandsForCategory(
    products: Product[] | any[],
    categoryId: string,
    limit: number = 5
): Array<{ brand: string; logoUrl: string | null }> {
    const brands = extractBrandsForCategory(products, categoryId);

    return brands
        .slice(0, limit)
        .map((brand) => ({
            brand,
            logoUrl: getBrandLogoUrl(brand),
        }));
}

/**
 * Get brands with valid logos for a category
 */
export function getBrandsWithLogos(
    products: Product[] | any[],
    categoryId: string,
    limit: number = 5
): Array<{ brand: string; logoUrl: string }> {
    return getTopBrandsForCategory(products, categoryId, limit)
        .filter((b) => b.logoUrl !== null)
        .map((b) => ({ brand: b.brand, logoUrl: b.logoUrl! }));
}
