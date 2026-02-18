/**
 * Product Page v.0 - Perfect Cockpit
 * 
 * Single source of truth for one product:
 * - Identity, hierarchy, media, verification, reviews, compatibility, actions
 * 
 * Layout: Clean, scannable, no clutter. Clear sections with clear headings.
 */

import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  X,
  ArrowLeft,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  BookOpen,
  Settings,
  ShoppingCart,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog, useProductVariants, useProductRelationships } from "../../hooks/useConductorCatalog";
import { HierarchyBreadcrumb, type HierarchyPath } from "../hierarchy/HierarchyBreadcrumb";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import { ProductRelationsManager } from "./ProductRelationsManager";

interface ProductPageV0Props {
  productId: string;
}

export const ProductPageV0: React.FC<ProductPageV0Props> = ({ productId }) => {
  const { closeProductPage, goToSpectrum, openProductPage } = useNavigationStore();
  const { products, metadata, isLoading: catalogLoading } = useConductorCatalog();
  const { variants } = useProductVariants(productId);
  const { accessories, compatible, alternatives, all: allRelations } = useProductRelationships(productId);
  
  const product = useMemo(
    () => products.find((p) => p.id === productId),
    [products, productId]
  );
  
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  
  // Extract hierarchy from product
  const hierarchy = useMemo<HierarchyPath | null>(() => {
    if (!product) return null;
    
    const taxonomy = product.taxonomy || {};
    return {
      category: taxonomy.canonical_category || "Uncategorized",
      subCategory: taxonomy.canonical_subcategory || "",
      productType: taxonomy.product_type || "",
      brand: product.brand || "",
      family: product.family_name || "",
      model: product.model_name || "",
    };
  }, [product]);
  
  // Images
  const images = useMemo(() => {
    if (!product) return [];
    if (product.image_gallery && product.image_gallery.length > 0) {
      return product.image_gallery;
    }
    return product.image_url ? [product.image_url] : [];
  }, [product]);
  
  // Price and stock
  const price = product?.price || product?.price_il || null;
  const priceDisplay = price ? `₪${price.toLocaleString()}` : "Price on request";
  const inStock = product?.in_stock !== false; // Default to true if not specified
  
  // Verification status
  const specsVerified = product?.specs_verified || false;
  const relationsVerified = product?.relations_verified || false;
  
  if (!product) {
    return (
      <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-zinc-900 rounded-xl p-8 max-w-md text-center">
          <h2 className="text-xl font-semibold text-white mb-2">Product not found</h2>
          <p className="text-zinc-400 mb-6">This product may have been removed.</p>
          <button
            onClick={closeProductPage}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }
  
  const brandLogo = product.brand ? getBrandLogoUrl(product.brand) : null;
  
  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm overflow-y-auto">
      <div className="min-h-full bg-zinc-950">
        {/* 1. Sticky Header - Compact */}
        <header className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur-md border-b border-zinc-800">
          <div className="w-full px-4 sm:px-6 lg:px-8 max-w-[1600px] mx-auto">
            {/* Hierarchy Breadcrumb */}
            {hierarchy && (
              <div className="pt-4 pb-2">
                <HierarchyBreadcrumb hierarchy={hierarchy} className="text-xs" />
              </div>
            )}
            
            {/* Header Content */}
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center gap-4 min-w-0 flex-1">
                <button
                  onClick={closeProductPage}
                  className="touch-target flex items-center justify-center rounded-lg hover:bg-zinc-800 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
                  aria-label="Back"
                >
                  <ArrowLeft className="w-5 h-5 text-zinc-400" />
                </button>
                
                {brandLogo && (
                  <img
                    src={brandLogo}
                    alt={product.brand}
                    className="w-10 h-10 rounded-lg object-contain"
                  />
                )}
                
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h1 className="text-xl font-semibold text-white truncate">
                      {product.name || product.product_name}
                    </h1>
                    {product.verified && (
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-medium rounded">
                        Verified
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-4 ml-4">
                <div className="text-right">
                  <div className="text-lg font-semibold text-white">{priceDisplay}</div>
                  {inStock && (
                    <div className="text-xs text-green-400 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      In Stock
                    </div>
                  )}
                </div>
                
                <button
                  onClick={closeProductPage}
                  className="touch-target flex items-center justify-center rounded-lg hover:bg-zinc-800 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
                  aria-label="Close"
                >
                  <X className="w-5 h-5 text-zinc-400" />
                </button>
              </div>
            </div>
          </div>
        </header>
        
        {/* Main Content - Optimized layout: Variants Left | Image Center | Related Right */}
        <main className="w-full px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 max-w-[1600px] mx-auto">
            {/* Left Column: Variants (Vertical) */}
            {variants && variants.length > 0 && (
              <div className="lg:col-span-2 order-2 lg:order-1">
                <section aria-label="Product variants">
                  <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden sticky top-24">
                    <div className="px-2.5 py-1.5 border-b border-zinc-800">
                      <h2 className="text-[9px] font-semibold text-zinc-400 uppercase tracking-wider text-center">
                        Variants ({variants.length})
                      </h2>
                    </div>
                    <div className="p-2">
                      <div className="flex flex-col gap-1.5">
                        {variants.map((variant) => (
                          <button
                            key={variant.id}
                            onClick={() => openProductPage(variant.id)}
                            className="relative w-full aspect-square rounded overflow-hidden border-2 border-zinc-800 hover:border-blue-500/50 transition-all hover:scale-105 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none group"
                            aria-label={`View variant: ${variant.name}`}
                            title={variant.name}
                          >
                            {variant.image_url ? (
                              <img
                                src={variant.image_url}
                                alt={variant.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full bg-zinc-800 flex items-center justify-center">
                                <div className="text-zinc-600 text-[7px] text-center px-1 leading-tight">{variant.name}</div>
                              </div>
                            )}
                            {/* Overlay on hover */}
                            <div className="absolute inset-0 bg-black/85 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-1">
                              <div className="text-[8px] font-medium text-white text-center line-clamp-2 leading-tight">
                                {variant.name}
                              </div>
                              {variant.price && (
                                <div className="text-[7px] text-zinc-300 mt-0.5">₪{variant.price.toLocaleString()}</div>
                              )}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            )}
            
            {/* Center Column: Main Image */}
            <div className={`${variants && variants.length > 0 ? 'lg:col-span-5' : 'lg:col-span-7'} order-1 lg:order-2`}>
              {/* 2. Hero & Media - Compact with integrated thumbnails */}
              <section aria-label="Product images">
                <div className="bg-zinc-900 rounded-xl overflow-hidden">
                  {images.length > 0 ? (
                    <div className="relative">
                      {/* Main Image */}
                      <div className="aspect-[4/3] bg-zinc-800 flex items-center justify-center relative">
                        <img
                          src={images[activeImageIndex]}
                          alt={product.name}
                          className="w-full h-full object-contain p-4"
                        />
                        
                        {/* Thumbnails integrated into bottom of main image - smaller and perfectly aligned */}
                        {images.length > 1 && (
                          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-zinc-900/95 via-zinc-900/85 to-transparent p-2">
                            <div className="flex items-center justify-center gap-1">
                              {images.map((img, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => setActiveImageIndex(idx)}
                                  className={`flex-shrink-0 w-9 h-9 rounded overflow-hidden border-2 transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                                    idx === activeImageIndex
                                      ? "border-blue-500 ring-1 ring-blue-500/50 scale-105"
                                      : "border-zinc-700/60 hover:border-zinc-600 hover:scale-105"
                                  }`}
                                  aria-label={`View image ${idx + 1} of ${images.length}`}
                                  aria-current={idx === activeImageIndex ? "true" : undefined}
                                >
                                  <img
                                    src={img}
                                    alt={`${product.name} view ${idx + 1}`}
                                    className="w-full h-full object-cover"
                                  />
                                </button>
                              ))}
                            </div>
                            <div className="text-[8px] text-zinc-500 text-center mt-1 font-medium">
                              {activeImageIndex + 1} / {images.length}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="aspect-[4/3] bg-zinc-800 flex items-center justify-center">
                      <div className="text-zinc-600 text-sm">No image available</div>
                    </div>
                  )}
                </div>
              </section>
            </div>
            
            {/* Right Column: Related Products (Vertical) + Info Panels Below */}
            <div className={`${variants && variants.length > 0 ? 'lg:col-span-5' : 'lg:col-span-5'} order-3 space-y-4`}>
              {/* Related Products - Vertical Layout */}
              {(accessories.length > 0 || compatible.length > 0 || alternatives.length > 0) && (
                <section aria-label="Related products">
                  <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
                    <div className="px-2.5 py-1.5 border-b border-zinc-800">
                      <h2 className="text-[9px] font-semibold text-zinc-400 uppercase tracking-wider text-center">
                        Related Products
                      </h2>
                    </div>
                    <div className="p-2 space-y-3 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-zinc-900">
                      {accessories.length > 0 && (
                        <div>
                          <h3 className="text-[8px] font-medium text-zinc-500 uppercase tracking-wider mb-1.5">Accessories</h3>
                          <div className="flex flex-col gap-1.5">
                            {accessories.map((acc) => {
                              const accProduct = products.find((p) => p.id === acc.id);
                              if (!accProduct) return null;
                              return (
                                <button
                                  key={acc.id}
                                  onClick={() => openProductPage(acc.id)}
                                  className="flex items-center gap-2 p-1.5 bg-zinc-800/50 rounded border border-zinc-800 hover:border-blue-500/50 transition-all hover:bg-zinc-800 text-left group"
                                >
                                  {accProduct.image_url && (
                                    <img
                                      src={accProduct.image_url}
                                      alt={accProduct.name}
                                      className="w-10 h-10 rounded object-cover flex-shrink-0"
                                    />
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <div className="text-[9px] font-medium text-white line-clamp-1 group-hover:text-blue-400 transition-colors">
                                      {accProduct.name}
                                    </div>
                                    {accProduct.price && (
                                      <div className="text-[7px] text-zinc-400 mt-0.5">₪{accProduct.price.toLocaleString()}</div>
                                    )}
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      
                      {compatible.length > 0 && (
                        <div>
                          <h3 className="text-[8px] font-medium text-zinc-500 uppercase tracking-wider mb-1.5">Compatible</h3>
                          <div className="flex flex-col gap-1.5">
                            {compatible.map((comp) => {
                              const compProduct = products.find((p) => p.id === comp.id);
                              if (!compProduct) return null;
                              return (
                                <button
                                  key={comp.id}
                                  onClick={() => openProductPage(comp.id)}
                                  className="flex items-center gap-2 p-1.5 bg-zinc-800/50 rounded border border-zinc-800 hover:border-green-500/50 transition-all hover:bg-zinc-800 text-left group"
                                >
                                  {compProduct.image_url && (
                                    <img
                                      src={compProduct.image_url}
                                      alt={compProduct.name}
                                      className="w-10 h-10 rounded object-cover flex-shrink-0"
                                    />
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <div className="text-[9px] font-medium text-white line-clamp-1 group-hover:text-green-400 transition-colors">
                                      {compProduct.name}
                                    </div>
                                    {compProduct.price && (
                                      <div className="text-[7px] text-zinc-400 mt-0.5">₪{compProduct.price.toLocaleString()}</div>
                                    )}
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      
                      {alternatives.length > 0 && (
                        <div>
                          <h3 className="text-[8px] font-medium text-zinc-500 uppercase tracking-wider mb-1.5">Alternatives</h3>
                          <div className="flex flex-col gap-1.5">
                            {alternatives.map((alt) => {
                              const altProduct = products.find((p) => p.id === alt.id);
                              if (!altProduct) return null;
                              return (
                                <button
                                  key={alt.id}
                                  onClick={() => openProductPage(alt.id)}
                                  className="flex items-center gap-2 p-1.5 bg-zinc-800/50 rounded border border-zinc-800 hover:border-orange-500/50 transition-all hover:bg-zinc-800 text-left group"
                                >
                                  {altProduct.image_url && (
                                    <img
                                      src={altProduct.image_url}
                                      alt={altProduct.name}
                                      className="w-10 h-10 rounded object-cover flex-shrink-0"
                                    />
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <div className="text-[9px] font-medium text-white line-clamp-1 group-hover:text-orange-400 transition-colors">
                                      {altProduct.name}
                                    </div>
                                    {altProduct.price && (
                                      <div className="text-[7px] text-zinc-400 mt-0.5">₪{altProduct.price.toLocaleString()}</div>
                                    )}
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </section>
              )}
              
              {/* Info Panels Below Related Products */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 4. Categorization - Compact */}
                {hierarchy && (
                  <section aria-label="Categorization">
                    <div className="bg-zinc-900 rounded-lg p-3 border border-zinc-800">
                      <div className="space-y-1.5">
                        <div>
                          <div className="text-[10px] text-zinc-500 mb-0.5">Category</div>
                          <div className="text-xs font-medium text-white">{hierarchy.category}</div>
                        </div>
                        {hierarchy.subCategory && (
                          <div>
                            <div className="text-[10px] text-zinc-500 mb-0.5">Subcategory</div>
                            <div className="text-xs font-medium text-white">{hierarchy.subCategory}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  </section>
                )}
                
                {/* 5. Truth Matrix / Verification - Compact */}
                <section aria-label="Verification status">
                  <div className="bg-zinc-900 rounded-lg p-3 border border-zinc-800 space-y-2">
                    {/* Catalog data loaded — confirms new data is showing */}
                    {!catalogLoading && metadata?.total_products != null && (
                      <div className="flex items-center justify-between pb-2 mb-2 border-b border-zinc-800">
                        <span className="text-xs text-zinc-500">Catalog</span>
                        <div className="flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5 text-green-400" aria-hidden />
                          <span className="text-xs font-medium text-green-400">
                            {metadata.total_products.toLocaleString()} products loaded
                          </span>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">Price</span>
                      <span className="text-xs font-medium text-white">
                        {price ? "Set" : "Not set"}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">Specs</span>
                      <div className="flex items-center gap-1.5">
                        {specsVerified ? (
                          <>
                            <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                            <span className="text-xs font-medium text-green-400">Verified</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-3.5 h-3.5 text-yellow-400" />
                            <span className="text-xs font-medium text-yellow-400">Unverified</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">Relations</span>
                      <div className="flex items-center gap-1.5">
                        {relationsVerified ? (
                          <>
                            <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                            <span className="text-xs font-medium text-green-400">Verified</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-3.5 h-3.5 text-yellow-400" />
                            <span className="text-xs font-medium text-yellow-400">Check needed</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </section>
              </div>
              
              {/* Interactive Relations Manager - Always visible */}
              <ProductRelationsManager
                productId={productId}
                relations={(allRelations || []).map((rel) => {
                  const targetId = rel.source_id === productId ? rel.target_id : rel.source_id;
                  const targetProduct = products.find((p) => p.id === targetId);
                  return {
                    id: `${rel.source_id}-${rel.target_id}-${rel.relationship_type}`,
                    type: rel.relationship_type as any,
                    targetId: targetId,
                    targetName: targetProduct?.name || targetId,
                    targetImage: targetProduct?.image_url,
                    verified: (rel.sources_verified && rel.sources_verified.length > 0) || false,
                    confidence: rel.confidence,
                  };
                })}
                onRelationAdd={(targetId, type) => {
                  console.log("Add relation:", { productId, targetId, type });
                  // TODO: Implement API call to add relation
                }}
                onRelationRemove={(relationId) => {
                  console.log("Remove relation:", relationId);
                  // TODO: Implement API call to remove relation
                }}
                onRelationVerify={(relationId) => {
                  console.log("Verify relation:", relationId);
                  // TODO: Implement API call to verify relation
                }}
              />
              
              {/* 6. Trusted Reviews - Compact */}
              <section aria-label="Trusted reviews">
                <h2 className="text-base font-semibold text-white mb-3">Reviews</h2>
                <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
                  <p className="text-xs text-zinc-400">Reviews will be displayed here</p>
                </div>
              </section>
            </div>
          </div>
        </main>
        
        {/* 8. Actions Footer - Compact */}
        <footer className="sticky bottom-0 bg-zinc-950/95 backdrop-blur-md border-t border-zinc-800 mt-6">
          <div className="w-full px-4 sm:px-6 lg:px-8 py-3 max-w-[1600px] mx-auto">
            <div className="flex flex-wrap items-center gap-2 justify-between">
              <div className="flex flex-wrap gap-2">
                <button
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-xs font-medium flex items-center gap-1.5"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  Deep Dive
                </button>
                <button
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors text-xs font-medium flex items-center gap-1.5"
                >
                  <Settings className="w-3.5 h-3.5" />
                  Compatibility
                </button>
                <button
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors text-xs font-medium flex items-center gap-1.5"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  Setup Guide
                </button>
                <button
                  onClick={goToSpectrum}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors text-xs font-medium"
                >
                  Back to Spectrum
                </button>
              </div>
              {product.halilit_url && (
                <a
                  href={product.halilit_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors text-xs font-medium flex items-center gap-1.5"
                >
                  <ShoppingCart className="w-3.5 h-3.5" />
                  View on Halilit
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};
