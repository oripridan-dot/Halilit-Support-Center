/* eslint-disable @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access */ /**
 * Mock Data for Testing
 * Fixtures and test data
 */

import type { BrandCatalog, MasterIndex, Product } from "../src/types";

export const mockProduct: Product = {
  id: "roland-td-17kvx",
  name: "TD-17KVX V-Drums Electronic Drum Kit",
  brand: "roland",
  category: "Electronic Drums",
  description:
    "Premium electronic drum kit with mesh heads and superior sound engine",
  image_url: "https://example.com/td-17kvx.jpg",
  images: [
    {
      url: "https://example.com/td-17kvx.jpg",
      type: "main",
    },
    {
      url: "https://example.com/td-17kvx-thumb.jpg",
      type: "thumbnail",
    },
  ],
  sku: "ROLAND-TD17KVX-IL",
  pricing: {
    regular_price: 8500,
    eilat_price: 7225,
    sale_price: 9500,
    currency: "ILS",
  },
  specs: {
    sounds: "310",
    pads: "Mesh heads",
    connectivity: "USB, MIDI, Bluetooth",
  },
  features: [
    "Full mesh heads for realistic feel",
    "TD-17 sound module with 310 sounds",
    "USB audio/MIDI connectivity",
    "Bluetooth audio streaming",
  ],
  availability: "in-stock",
  verified: true,
  verification_confidence: 0.95,
  match_quality: "excellent",
};

export const mockProducts: Product[] = [
  mockProduct,
  {
    ...mockProduct,
    id: "roland-td-27",
    name: "TD-27 V-Drums Electronic Drum Kit",
    sku: "ROLAND-TD27-IL",
    pricing: {
      ...mockProduct.pricing,
      regular_price: 12000,
    },
  },
  {
    ...mockProduct,
    id: "roland-juno-ds",
    name: "Juno-DS Synthesizer",
    category: "Synthesizers",
    sku: "ROLAND-JUNODS-IL",
    pricing: {
      ...mockProduct.pricing,
      regular_price: 5500,
    },
  },
];

export const mockBrandCatalog: BrandCatalog = {
  brand_id: "roland",
  brand_name: "Roland Corporation",
  logo_url: "https://example.com/roland-logo.png",
  brand_website: "https://www.roland.com",
  description:
    "Roland Corporation is a leading manufacturer of music instruments",
  products: mockProducts,
  brand_identity: {
    id: "roland",
    name: "Roland Corporation",
    logo_url: "https://example.com/roland-logo.png",
    hq: "Osaka, Japan",
    website: "https://www.roland.com",
    description:
      "Roland Corporation is a leading manufacturer of music instruments",
  },
  total_products: mockProducts.length,
};

export const mockMasterIndex: MasterIndex = {
  build_timestamp: "2026-01-18T10:00:00Z",
  version: "3.7.0",
  total_products: 29,
  total_verified: 29,
  brands: [
    {
      id: "roland",
      name: "Roland",
      logo_url: "https://example.com/roland-logo.png",
      hq: "Osaka, Japan",
      website: "https://www.roland.com",
      product_count: 29,
      verified_count: 29,
      description: "Roland Corporation",
      brand_number: "001",
      data_file: "catalogs_brand/roland_catalog.json",
    },
  ],
};

// Create products with different categories for testing
export const mockProductsByCategory: Record<string, Product[]> = {
  "Electronic Drums": [
    {
      ...mockProduct,
      id: "td-1",
      name: "TD-17KVX",
      category: "Electronic Drums",
    },
    { ...mockProduct, id: "td-2", name: "TD-27", category: "Electronic Drums" },
  ],
  Synthesizers: [
    {
      ...mockProduct,
      id: "synth-1",
      name: "Juno-DS",
      category: "Synthesizers",
    },
    {
      ...mockProduct,
      id: "synth-2",
      name: "JUPITER-Xm",
      category: "Synthesizers",
    },
  ],
  "Digital Pianos": [
    {
      ...mockProduct,
      id: "piano-1",
      name: "FP-90X",
      category: "Digital Pianos",
    },
  ],
};
