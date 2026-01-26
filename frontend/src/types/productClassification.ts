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

export type ProductClass = "MI" | "PA" | "ACCESSORIES" | "CASES" | "CABLES";

export interface ProductClassification {
  /** Primary classification - MI, PA, Accessories, etc. */
  primaryClass: ProductClass;

  /** Secondary classes (for products with overlap) */
  secondaryClasses?: ProductClass[];

  /** Brand identifier */
  brand: string;

  /** Category within brand taxonomy */
  category: string;

  /** Subcategory (if applicable) */
  subcategory?: string;

  /** Direct relations (accessories for this product, etc.) */
  directRelations?: string[];

  /** Related products (alternatives, upgrades, etc.) */
  relatedProducts?: string[];
}

/**
 * Brand Classification Map
 * Defines the primary classification for each brand
 */
export const BRAND_CLASSIFICATIONS: Record<string, ProductClass> = {
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
export const CATEGORY_CLASSIFICATION_OVERRIDES: Record<
  string,
  Record<string, ProductClass>
> = {
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
export function getProductClass(
  brand: string,
  category?: string,
): ProductClass {
  const normalizedBrand = brand.toLowerCase();

  // Check for category-specific override
  if (
    category &&
    CATEGORY_CLASSIFICATION_OVERRIDES[normalizedBrand]?.[category]
  ) {
    return CATEGORY_CLASSIFICATION_OVERRIDES[normalizedBrand][category];
  }

  // Use brand default
  return BRAND_CLASSIFICATIONS[normalizedBrand] || "MI";
}

/**
 * Determine if a product has overlapping classifications
 */
export function getSecondaryClasses(
  brand: string,
  category: string,
): ProductClass[] {
  const secondary: ProductClass[] = [];

  // Example: MIDI controllers can be both MI and PA
  if (
    category.toLowerCase().includes("controller") ||
    category.toLowerCase().includes("interface")
  ) {
    const primary = getProductClass(brand, category);
    if (primary === "MI") secondary.push("PA");
    if (primary === "PA") secondary.push("MI");
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
export function classifyProduct(
  brand: string,
  category: string,
  subcategory?: string,
  directRelations?: string[],
  relatedProducts?: string[],
): ProductClassification {
  const primaryClass = getProductClass(brand, category);
  const secondaryClasses = getSecondaryClasses(brand, category);

  return {
    primaryClass,
    secondaryClasses:
      secondaryClasses.length > 0 ? secondaryClasses : undefined,
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
export function filterByClass<T extends { brand: string; category: string }>(
  products: T[],
  productClass: ProductClass,
): T[] {
  return products.filter((p) => {
    const classification = getProductClass(p.brand, p.category);
    return classification === productClass;
  });
}

/**
 * Get human-readable label for product class
 */
export function getClassLabel(productClass: ProductClass): string {
  const labels: Record<ProductClass, string> = {
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
export function getClassIcon(productClass: ProductClass): string {
  const icons: Record<ProductClass, string> = {
    MI: "🎹",
    PA: "🎙️",
    ACCESSORIES: "🔧",
    CASES: "💼",
    CABLES: "🔌",
  };
  return icons[productClass];
}
