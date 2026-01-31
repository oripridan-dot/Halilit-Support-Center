"use strict";
/**
 * Product Classification System
 *
 * First-level classification for all products:
 * 1. MI (Musical Instruments)
 * 2. PA (Pro Audio)
 * 3. Accessories
 * 4. Cases
 * 5. Cables
 *
 * Product Hierarchy:
 * Primary Class → Brand → Category → Subcategory → Direct Relations → Related Products
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CATEGORY_CLASSIFICATION_OVERRIDES = exports.BRAND_CLASSIFICATIONS = void 0;
exports.getProductClass = getProductClass;
exports.getSecondaryClasses = getSecondaryClasses;
exports.classifyProduct = classifyProduct;
exports.filterByClass = filterByClass;
exports.getClassLabel = getClassLabel;
exports.getClassIcon = getClassIcon;
/**
 * Brand Classification Map
 * Defines the primary classification for each brand
 */
exports.BRAND_CLASSIFICATIONS = {
    // Musical Instruments (MI)
    roland: "MI",
    nord: "MI",
    moog: "MI",
    boss: "MI", // Effects are MI
    "teenage-engineering": "MI",
    "akai-professional": "MI", // Controllers/samplers are MI
    // Pro Audio (PA)
    "universal-audio": "PA",
    "warm-audio": "PA",
    mackie: "PA",
    "adam-audio": "PA",
};
/**
 * Category Classification Overrides
 * Some categories within brands have different classifications
 */
exports.CATEGORY_CLASSIFICATION_OVERRIDES = {
    roland: {
        Accessories: "ACCESSORIES",
        Cases: "CASES",
        Cables: "CABLES",
    },
    boss: {
        Accessories: "ACCESSORIES",
        Cases: "CASES",
    },
    // Add more brand-specific overrides as needed
};
/**
 * Get the primary classification for a product
 */
function getProductClass(brand, category) {
    const normalizedBrand = brand.toLowerCase();
    // Check for category-specific override
    if (category &&
        exports.CATEGORY_CLASSIFICATION_OVERRIDES[normalizedBrand]?.[category]) {
        return exports.CATEGORY_CLASSIFICATION_OVERRIDES[normalizedBrand][category];
    }
    // Use brand default
    return exports.BRAND_CLASSIFICATIONS[normalizedBrand] || "MI";
}
/**
 * Determine if a product has overlapping classifications
 */
function getSecondaryClasses(brand, category) {
    const secondary = [];
    // Example: MIDI controllers can be both MI and PA
    if (category.toLowerCase().includes("controller") ||
        category.toLowerCase().includes("interface")) {
        const primary = getProductClass(brand, category);
        if (primary === "MI")
            secondary.push("PA");
        if (primary === "PA")
            secondary.push("MI");
    }
    // Headphones can be both MI and PA
    if (category.toLowerCase().includes("headphone")) {
        secondary.push("PA");
    }
    return secondary;
}
/**
 * Build complete classification for a product
 */
function classifyProduct(brand, category, subcategory, directRelations, relatedProducts) {
    const primaryClass = getProductClass(brand, category);
    const secondaryClasses = getSecondaryClasses(brand, category);
    return {
        primaryClass,
        secondaryClasses: secondaryClasses.length > 0 ? secondaryClasses : undefined,
        brand: brand.toLowerCase(),
        category,
        subcategory,
        directRelations,
        relatedProducts,
    };
}
/**
 * Filter products by primary class
 */
function filterByClass(products, productClass) {
    return products.filter((p) => {
        const classification = getProductClass(p.brand, p.category);
        return classification === productClass;
    });
}
/**
 * Get human-readable label for product class
 */
function getClassLabel(productClass) {
    const labels = {
        MI: "Musical Instruments",
        PA: "Pro Audio",
        ACCESSORIES: "Accessories",
        CASES: "Cases",
        CABLES: "Cables",
    };
    return labels[productClass];
}
/**
 * Get icon for product class
 */
function getClassIcon(productClass) {
    const icons = {
        MI: "🎹",
        PA: "🎙️",
        ACCESSORIES: "🔧",
        CASES: "💼",
        CABLES: "🔌",
    };
    return icons[productClass];
}
