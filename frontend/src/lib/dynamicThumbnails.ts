/**
 * Dynamic Thumbnail Selection
 *
 * Automatically selects category thumbnails based on the most expensive
 * product in each category that matches specific keywords.
 */

import type { Product, ProductImagesObject } from "../types";
import { consolidateCategory } from "./categoryConsolidator";
import { UNIVERSAL_CATEGORIES } from "./universalCategories";

export interface CategoryThumbnail {
  categoryId: string;
  subcategory?: string;
  imageUrl: string;
  productName: string;
  price: number;
  brand: string;
}

// Map of "UI Label" -> Keywords to search for
const SUBCATEGORY_MATCHERS: Record<string, string[]> = {
  // --- Keys & Pianos ---
  Synthesizers: [
    "Synthesizer",
    "Synth",
    "System-8",
    "Jupiter",
    "Juno",
    "Fantom",
    "Moog",
    "Matriarch",
    "Subsequent",
    "Nord Lead",
    "Nord Wave",
    "Op-1",
    "Op-z",
    "GAIA",
  ],
  "Stage Pianos": [
    "Stage Piano",
    "RD-2000",
    "RD-88",
    "Nord Stage",
    "Nord Piano",
    "Grand",
    "Piano",
    "CP88",
  ],
  "MIDI Controllers": [
    "Controller",
    "MIDI",
    "A-88",
    "KeyLab",
    "MPK",
    "Launchkey",
    "Keystep",
    "Beatstep",
  ],
  Arrangers: ["Arranger", "Pa5X", "Pa4X", "BK-", "E-A7", "Genos"],
  Organs: ["Organ", "C2D", "Electro", "Combo", "VK-"],
  Workstations: [
    "Workstation",
    "Fantom",
    "Nautilus",
    "Montage",
    "MODX",
    "FA-0",
    "FA-08",
  ],

  // --- Drums & Percussion ---
  "Electronic Drum Kits": ["V-Drums", "TD-", "VAD", "Electronic Drum", "DTX"],
  "Acoustic Drums": [
    "Acoustic Drum",
    "Shell Pack",
    "Snare",
    "Kick",
    "Tom",
    "Starclassic",
  ],
  Cymbals: ["Cymbal", "Crash", "Ride", "Hi-Hat", "Byzance"],
  Percussion: ["Percussion", "Cajon", "Conga", "Bongo", "SPD", "Handsonic"],
  "Drum Machines": [
    "Drum Machine",
    "TR-8",
    "TR-9",
    "TR-6S",
    "MPC",
    "Maschine",
    "DrumBrute",
  ],
  "Drum Pads": ["Drum Pad", "SPD-SX", "Octapad", "Sample Pad", "MultiPad"],

  // --- Guitars & Amps ---
  "Electric Guitars": [
    "Electric Guitar",
    "Stratocaster",
    "Telecaster",
    "Les Paul",
    "Ibanez",
    "Fender",
  ],
  "Bass Guitars": ["Bass Guitar", "Precision Bass", "Jazz Bass", "Ibanez Bass"],
  Amplifiers: [
    "Amplifier",
    "Amp",
    "Katana",
    "Blues Cube",
    "JC-120",
    "Nextone",
    "Marshall",
  ],
  "Effects Pedals": [
    "Pedal",
    "Stompbox",
    "Overdrive",
    "Distortion",
    "Delay",
    "Reverb",
    "Chorus",
    "Boss",
  ],
  "Multi-Effects": [
    "Multi-Effects",
    "GT-1000",
    "GX-100",
    "ME-90",
    "Helix",
    "Kemper",
    "Headrush",
  ],
  Accessories: ["Accessory", "Case", "Cable", "Stand", "Tuner"],

  // --- Studio & Recording ---
  "Audio Interfaces": [
    "Interface",
    "Apollo",
    "Volt",
    "Rubix",
    "Studio-Capture",
    "Mbox",
    "Scarlett",
  ],
  "Studio Monitors": [
    "Monitor",
    "Speaker",
    "A7V",
    "A4V",
    "HR",
    "MR",
    "CR",
    "HS8",
  ],
  Microphones: [
    "Microphone",
    "Mic",
    "Condenser",
    "Dynamic",
    "Ribbon",
    "WA-",
    "SM7B",
  ],
  "Outboard Gear": [
    "Compressor",
    "EQ",
    "Preamp",
    "Channel Strip",
    "WA-2A",
    "WA-76",
    "1176",
  ],
  Preamps: ["Preamp", "Microphone Preamp", "WA-12", "WA-412", "1073"],
  Software: ["Software", "Plugin", "DAW"],

  // --- Live Sound ---
  "PA Speakers": [
    "PA Speaker",
    "Loudspeaker",
    "Thump",
    "SRM",
    "Eon",
    "Mackie",
    "K12",
  ],
  Mixers: ["Mixer", "Console", "Onyx", "ProFX", "M32", "X32", "Wing"],
  "Powered Mixers": ["Powered Mixer", "PPM"],
  "Wireless Systems": ["Wireless", "Mic System", "IEM", "EW-D"],
  "In-Ear Monitoring": ["In-Ear", "IEM", "MP-", "SE215"],
  "Stage Boxes": ["Stage Box", "Digital Snake", "S16", "DL16"],

  // --- DJ & Production ---
  "DJ Controllers": [
    "DJ Controller",
    "DJ-808",
    "DJ-505",
    "Traktor",
    "Serato",
    "DDJ",
  ],
  Grooveboxes: [
    "Groovebox",
    "MC-707",
    "MC-101",
    "Circuit",
    "OP-1",
    "EP-133",
    "Play",
  ],
  Samplers: ["Sampler", "SP-404", "MPC", "Digitakt", "Octatrack"],
  "DJ Headphones": ["DJ Headphone", "V-Moda", "Crossfade", "Aira", "HD-25"],
  Production: ["Production", "OP-1", "Field", "Pocket Operator"],
};

/**
 * Build a complete thumbnail map for all categories and subcategories
 */
export function buildDynamicThumbnailMap(
  products: Product[],
): Map<string, CategoryThumbnail> {
  const thumbnailMap = new Map<string, CategoryThumbnail>();

  // 1. Group products by consolidated category for faster access
  const productsByCategory = new Map<string, Product[]>();

  for (const p of products) {
    if (!p.brand) continue;
    const catId = consolidateCategory(p.brand, p.category);
    if (!productsByCategory.has(catId)) {
      productsByCategory.set(catId, []);
    }
    productsByCategory.get(catId)?.push(p);
  }

  // 2. Iterate Universal Categories (Top-Down)
  for (const catDetails of UNIVERSAL_CATEGORIES) {
    const catId = catDetails.id;
    const catProducts = productsByCategory.get(catId) || [];

    // A. Find Hero for the main Category (Any premium product in category)
    const mainHero = findPremiumProduct(catProducts);
    if (mainHero) {
      thumbnailMap.set(catId, mainHero);
    }

    // B. Find Hero for each Subcategory
    for (const sub of catDetails.spectrum) {
      const matchers = SUBCATEGORY_MATCHERS[sub.label];

      // Filter products that match THIS subcategory using keywords
      const subProducts = catProducts.filter((p) => {
        // Strict keyword matching if defined
        if (matchers) {
          const combinedText =
            `${p.name} ${p.subcategory || ""} ${p.category || ""}`.toLowerCase();
          return matchers.some((keyword) =>
            combinedText.includes(keyword.toLowerCase()),
          );
        }
        // Fallback: simple inclusion if no matchers defined
        return (
          p.subcategory?.includes(sub.label) || p.category?.includes(sub.label)
        );
      });

      const subHero = findPremiumProduct(subProducts);

      // Store with composite key: "categoryId:Sublabel"
      if (subHero) {
        thumbnailMap.set(`${catId}:${sub.label}`, {
          ...subHero,
          subcategory: sub.label,
        });
      }
    }
  }

  return thumbnailMap;
}

/**
 * Helper to find the most expensive product with an image
 */
function findPremiumProduct(products: Product[]): CategoryThumbnail | null {
  if (!products || products.length === 0) return null;

  let bestProduct: Product | null = null;
  let maxPrice = -1;

  for (const p of products) {
    if (!hasImage(p)) continue;

    const price = getPrice(p);

    // Logic: Higher price is better.
    if (price > maxPrice) {
      maxPrice = price;
      bestProduct = p;
    } else if (maxPrice === -1) {
      // Initialize with first valid product even if price is 0
      maxPrice = price;
      bestProduct = p;
    }
  }

  // Last resort: just pick matching one
  if (!bestProduct) {
    bestProduct = products.find(hasImage) || null;
  }

  if (!bestProduct) return null;

  return productToThumbnail(bestProduct);
}

function getPrice(p: Product): number {
  // Handle pricing as number or object
  const pricing = typeof p.pricing === "number" ? p.pricing : p.pricing;
  return (
    p.halilit_price ||
    (pricing && typeof pricing === "object"
      ? pricing.regular_price || pricing.sale_price
      : pricing) ||
    0
  );
}

function hasImage(p: Product): boolean {
  if (typeof p.images === "string") return !!p.images;
  if (Array.isArray(p.images) && p.images.length > 0) return true;
  if (p.image_url) return true;
  // Handle object format { 'main': ... }
  if (p.images && typeof p.images === "object" && !Array.isArray(p.images)) {
    const imgs = p.images as ProductImagesObject;
    return !!(imgs.main || imgs.thumbnail);
  }
  return false;
}

function productToThumbnail(p: Product): CategoryThumbnail {
  let imageUrl = "";

  if (Array.isArray(p.images) && p.images.length > 0) {
    const bestImg = p.images.find(
      (i) => i.type === "thumbnail" || i.type === "main",
    );
    imageUrl = bestImg ? bestImg.url : p.images[0].url;
  } else if (typeof p.images === "string") {
    imageUrl = p.images;
  } else if (p.image_url) {
    imageUrl = p.image_url;
  } else if (p.images && typeof p.images === "object") {
    const imgs = p.images as ProductImagesObject;
    imageUrl = imgs.thumbnail || imgs.main || "";
  }

  return {
    categoryId: consolidateCategory(p.brand, p.category),
    imageUrl,
    productName: p.name,
    price: getPrice(p),
    brand: p.brand,
  };
}

/**
 * Get thumbnail for a specific category/subcategory combination
 */
export function getThumbnailForCategory(
  thumbnailMap: Map<string, CategoryThumbnail>,
  categoryId: string,
  subcategory?: string,
): string | null {
  const key = subcategory ? `${categoryId}:${subcategory}` : categoryId;
  return thumbnailMap.get(key)?.imageUrl || null;
}

// Deprecated functions kept for compatibility
export function getMostExpensiveProductImage(
  _products: Product[],
  _universalCategoryId?: string,
  _subcategory?: string,
): CategoryThumbnail | null {
  return null;
}

export function getTopProductsByCategory(
  products: Product[],
  categoryId: string,
  limit = 10,
): Product[] {
  return products
    .filter((p) => consolidateCategory(p.brand, p.category) === categoryId)
    .sort((a, b) => getPrice(b) - getPrice(a))
    .slice(0, limit);
}
