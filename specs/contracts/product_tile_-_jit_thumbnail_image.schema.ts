// Contract: Product Tile - JIT Thumbnail Image

export const PRODUCT_TILE_JIT_THUMBNAIL_ENDPOINT = ''; // No API endpoint

export interface ConductorProduct {
  image_url?: string;
  name: string; // Example, add other necessary properties
}

export type JITState =
  | { status: 'loading' }
  | { status: 'complete'; thumbnail: string }
  | { status: 'error'; error: string }
  | { status: 'empty' };

export interface JITIntelligence {
  status: JITState['status'];
  thumbnail?: string;
  error?: string;
}

export interface ProductTileProps {
  conductorProduct: ConductorProduct;
  jit: JITIntelligence | null;
  productId: string;
}

export type ProductTileResponse = void; // No API response