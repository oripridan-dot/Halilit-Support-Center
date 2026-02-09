/**
 * Image Resolver: Ensures every product has a valid image URL
 * Phase 7.7b: Enhanced Fallback Chain with Source Traceability
 * 
 * Fallback Order (Priority):
 * 1. Official Manufacturer Image
 * 2. Halilit.com Commercial Image (Verified)
 * 3. Gallery/Additional Images
 * 4. Placeholder (Generated or Transparent)
 */

import type { Product } from "../types";

export const PLACEHOLDER_COLORS = {
  primary: "#1a1a1a",
  accent: "#ff9900",
};

// Track failed images for analytics
interface ImageResolutionTrace {
  product_id: string;
  attempted_sources: Array<{
    source_type: "official" | "halilit" | "gallery" | "placeholder";
    url: string;
    valid: boolean;
    timestamp: string;
  }>;
  final_image: string;
  resolution_time_ms: number;
}

// In-memory trace buffer (can be extended to send to backend)
const imageResolutionTraces: ImageResolutionTrace[] = [];

/**
 * Log image resolution attempt for analytics
 */
function logImageResolution(trace: ImageResolutionTrace): void {
  imageResolutionTraces.push(trace);
  
  // Keep only last 100 traces in memory
  if (imageResolutionTraces.length > 100) {
    imageResolutionTraces.shift();
  }
  
  // Log failed resolutions to console in debug mode
  if (trace.attempted_sources.some(s => !s.valid)) {
    console.debug(`[ImageResolver] ${trace.product_id}: Used fallback chain`, trace);
  }
}

/**
 * Get resolution analytics (for debugging)
 */
export function getImageResolutionAnalytics() {
  const stats = {
    total_resolutions: imageResolutionTraces.length,
    fallback_rate: 0,
    failed_sources: 0,
  };
  
  const failedAttempts = imageResolutionTraces.filter(t => 
    t.attempted_sources.some(s => !s.valid)
  );
  
  stats.fallback_rate = imageResolutionTraces.length > 0 
    ? (failedAttempts.length / imageResolutionTraces.length) * 100 
    : 0;
  
  stats.failed_sources = imageResolutionTraces.reduce((acc, t) => 
    acc + t.attempted_sources.filter(s => !s.valid).length, 0
  );
  
  return stats;
}

// Transparent pixel for "no image" state
const TRANSPARENT_PIXEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";

/**
 * Check if image URL looks valid (basic format check)
 */
function isValidImageUrl(url: string | null | undefined): boolean {
  if (!url || typeof url !== "string") return false;

  // Accept URLs with image extensions or known CDN domains
  const imageExtensions = /\.(jpg|jpeg|png|gif|svg|webp|webm)$/i;
  const cdnPattern = /(cloudfront|cdn|imgix|fastly|akamai|amazonaws|halilit\.com)/i;
  
  // Reject obviously fake URLs
  if (url.includes("brand.com") || url.includes("example.com") || url === "undefined") {
    return false;
  }

  return imageExtensions.test(url) || cdnPattern.test(url);
}

/**
 * Extract manufacturer image from official specs
 * Looks for manufacturer website URLs in the product specs
 */
function extractManufacturerImage(product: Product): string | null {
  // Check official specs for manufacturer site reference
  if (product.official_specs && typeof product.official_specs === "object") {
    // Common patterns for manufacturer image fields
    const specs = product.official_specs as Record<string, any>;
    
    if (specs.manufacturer_image && isValidImageUrl(specs.manufacturer_image)) {
      return specs.manufacturer_image;
    }
    
    if (specs.hero_image && isValidImageUrl(specs.hero_image)) {
      return specs.hero_image;
    }
  }

  // Check external_data for manufacturer links
  if (product.external_data && typeof product.external_data === "object") {
    const external = product.external_data as Record<string, any>;
    
    if (external.manufacturer_image && isValidImageUrl(external.manufacturer_image)) {
      return external.manufacturer_image;
    }
    
    if (external.featured_image && isValidImageUrl(external.featured_image)) {
      return external.featured_image;
    }
  }

  return null;
}

/**
 * Resolve a valid image URL with comprehensive fallback chain
 * 
 * Fallback Order:
 * 1. Official Manufacturer Image (highest priority)
 * 2. Halilit.com Commercial Image  
 * 3. Display/Gallery Images
 * 4. Legacy image_hero/image_thumbnail
 * 5. Placeholder (transparent or generated)
 */
export function resolveProductImage(
  product: Product | null | undefined,
): string {
  const startTime = performance.now();
  const traces: ImageResolutionTrace["attempted_sources"] = [];
  
  if (!product) {
    return TRANSPARENT_PIXEL;
  }

  const productId = (product as any).id || (product as any).halilit_id || "unknown";

  // === PRIORITY 1: Official Manufacturer Image ===
  const manufacturerImage = extractManufacturerImage(product);
  if (manufacturerImage) {
    traces.push({
      source_type: "official",
      url: manufacturerImage,
      valid: true,
      timestamp: new Date().toISOString(),
    });
    
    logImageResolution({
      product_id: productId,
      attempted_sources: traces,
      final_image: manufacturerImage,
      resolution_time_ms: performance.now() - startTime,
    });
    
    return manufacturerImage;
  }

  // === PRIORITY 2: Halilit.com Commercial Image ===
  
  // 2a. Top-level image_url (preferred structure)
  if ((product as any).image_url && isValidImageUrl((product as any).image_url)) {
    traces.push({
      source_type: "halilit",
      url: (product as any).image_url,
      valid: true,
      timestamp: new Date().toISOString(),
    });
    
    logImageResolution({
      product_id: productId,
      attempted_sources: traces,
      final_image: (product as any).image_url,
      resolution_time_ms: performance.now() - startTime,
    });
    
    return (product as any).image_url;
  }

  // 2b. Display object structure (v6.0+)
  if ((product as any).display?.hero_image?.url) {
    const heroUrl = (product as any).display.hero_image.url;
    if (isValidImageUrl(heroUrl)) {
      traces.push({
        source_type: "halilit",
        url: heroUrl,
        valid: true,
        timestamp: new Date().toISOString(),
      });
      
      logImageResolution({
        product_id: productId,
        attempted_sources: traces,
        final_image: heroUrl,
        resolution_time_ms: performance.now() - startTime,
      });
      
      return heroUrl;
    }
  }

  // 2c. Commercial image fallback
  if ((product as any).commercial_image && isValidImageUrl((product as any).commercial_image)) {
    traces.push({
      source_type: "halilit",
      url: (product as any).commercial_image,
      valid: true,
      timestamp: new Date().toISOString(),
    });
    
    logImageResolution({
      product_id: productId,
      attempted_sources: traces,
      final_image: (product as any).commercial_image,
      resolution_time_ms: performance.now() - startTime,
    });
    
    return (product as any).commercial_image;
  }

  // === PRIORITY 3: Gallery/Additional Images ===
  
  // 3a. Gallery from official_images
  if ((product as any).official_images && Array.isArray((product as any).official_images)) {
    for (const image of (product as any).official_images) {
      const imageUrl = image?.url || image;
      if (imageUrl && isValidImageUrl(imageUrl)) {
        traces.push({
          source_type: "gallery",
          url: imageUrl,
          valid: true,
          timestamp: new Date().toISOString(),
        });
        
        logImageResolution({
          product_id: productId,
          attempted_sources: traces,
          final_image: imageUrl,
          resolution_time_ms: performance.now() - startTime,
        });
        
        return imageUrl;
      }
    }
  }

  // 3b. Legacy image_gallery structure
  if ((product as any).image_gallery && Array.isArray((product as any).image_gallery)) {
    for (const image of (product as any).image_gallery) {
      const imageUrl = image?.url || image;
      if (imageUrl && isValidImageUrl(imageUrl)) {
        traces.push({
          source_type: "gallery",
          url: imageUrl,
          valid: true,
          timestamp: new Date().toISOString(),
        });
        
        logImageResolution({
          product_id: productId,
          attempted_sources: traces,
          final_image: imageUrl,
          resolution_time_ms: performance.now() - startTime,
        });
        
        return imageUrl;
      }
    }
  }

  // 3c. Thumbnail as fallback
  if ((product as any).image_thumbnail?.url && isValidImageUrl((product as any).image_thumbnail.url)) {
    traces.push({
      source_type: "gallery",
      url: (product as any).image_thumbnail.url,
      valid: true,
      timestamp: new Date().toISOString(),
    });
    
    logImageResolution({
      product_id: productId,
      attempted_sources: traces,
      final_image: (product as any).image_thumbnail.url,
      resolution_time_ms: performance.now() - startTime,
    });
    
    return (product as any).image_thumbnail.url;
  }

  // === PRIORITY 4: Legacy image_hero (v5.0 compatibility) ===
  if ((product as any).image_hero?.url && isValidImageUrl((product as any).image_hero.url)) {
    traces.push({
      source_type: "gallery",
      url: (product as any).image_hero.url,
      valid: true,
      timestamp: new Date().toISOString(),
    });
    
    logImageResolution({
      product_id: productId,
      attempted_sources: traces,
      final_image: (product as any).image_hero.url,
      resolution_time_ms: performance.now() - startTime,
    });
    
    return (product as any).image_hero.url;
  }

  // === FALLBACK: Transparent Pixel ===
  // Log that all sources failed
  traces.forEach(t => { t.valid = false; });
  
  logImageResolution({
    product_id: productId,
    attempted_sources: traces,
    final_image: TRANSPARENT_PIXEL,
    resolution_time_ms: performance.now() - startTime,
  });

  return TRANSPARENT_PIXEL;
}

/**
 * Generate a data URL placeholder image
 * Used as a secondary fallback
 */
export function generatePlaceholderImage(productName: string): string {
  const svg = `<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${PLACEHOLDER_COLORS.primary};stop-opacity:1" />
        <stop offset="100%" style="stop-color:#0a0a0a;stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="300" height="300" fill="url(#grad)"/>
    <circle cx="150" cy="120" r="50" fill="${PLACEHOLDER_COLORS.accent}" opacity="0.2"/>
    <rect x="40" y="190" width="220" height="80" fill="${PLACEHOLDER_COLORS.accent}" opacity="0.15" rx="4"/>
    <text x="150" y="275" font-family="monospace" font-size="11" font-weight="bold" fill="${PLACEHOLDER_COLORS.accent}" text-anchor="middle" opacity="0.6">
      ${productName.substring(0, 15).toUpperCase()}
    </text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/**
 * Batch resolve images for multiple products
 */
export function resolveProductImages(
  products: Product[],
): Array<Product & { resolved_image_url: string }> {
  return products.map((product) => ({
    ...product,
    resolved_image_url: resolveProductImage(product),
  }));
}
