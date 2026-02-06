import React, { useState, useEffect } from "react";
import {
  ChevronRight,
  ChevronLeft,
  DollarSign,
  Music,
  ArrowLeft,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { catalogLoader } from "../../lib/catalogLoader";
import { getPrice, getPriceValue } from "../../lib/priceFormatter";
import type { Product as CatalogProduct } from "../../types";

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;
  image: string;
  in_stock: boolean;
  sku: string;
}

interface BrandTrack {
  name: string;
  count: number;
  products: Product[];
}

interface TierBarProps {
  title?: string;
  onProductSelect?: (product: Product) => void;
}

export const TierBar: React.FC<TierBarProps> = ({
  title = "Products by Brand & Price",
  onProductSelect,
}) => {
  const [brandTracks, setBrandTracks] = useState<BrandTrack[]>([]);
  const [scrollPositions, setScrollPositions] = useState<
    Record<string, number>
  >({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { openProductPage } = useNavigationStore();

  useEffect(() => {
    fetchBrandsWithProducts();
  }, []);

  const fetchBrandsWithProducts = async () => {
    try {
      setLoading(true);

      // Load all products from catalog
      const allProducts = await catalogLoader.loadAllProducts();

      // Group by brand and sort by price
      const brandMap = new Map<string, CatalogProduct[]>();

      allProducts.forEach((product) => {
        const brand = product.brand || "Unknown";
        if (!brandMap.has(brand)) {
          brandMap.set(brand, []);
        }
        brandMap.get(brand)!.push(product);
      });

      // Transform to BrandTrack format and sort products by price
      const tracks: BrandTrack[] = Array.from(brandMap.entries())
        .map(([brandName, products]) => {
          const sorted = products.sort((a, b) => {
            const priceA = getPriceValue(a);
            const priceB = getPriceValue(b);
            return priceA - priceB;
          });

          return {
            name: brandName,
            count: sorted.length,
            products: sorted.map((p: any): Product => {
              // Robust Image Resolution Strategy (v6.0 Compatible)
              let resolvedImage = "";

              // 1. Try v6.0 Nested Object structure
              if (
                p.images &&
                typeof p.images === "object" &&
                !Array.isArray(p.images)
              ) {
                resolvedImage = p.images.main || p.images.thumbnail || "";
              }

              // 2. Try v5.0 Flat Properties
              if (!resolvedImage) {
                resolvedImage =
                  p.image_hero || p.image_thumbnail || p.image_url || "";
              }

              // 3. Last Resort: Try direct 'image' property
              if (!resolvedImage && p.image) {
                resolvedImage = p.image;
              }

              return {
                id: p.id || "",
                name: p.name || "Unnamed",
                brand: p.brand || "Unknown",
                price: getPriceValue(p),
                currency: "ILS",
                image: resolvedImage,
                in_stock: p.in_stock !== false,
                sku: String(p.sku || p.id || ""),
              };
            }),
          };
        })
        .sort((a, b) => a.name.localeCompare(b.name));

      setBrandTracks(tracks);
      setError(null);
    } catch (err) {
      console.error("Error fetching brands:", err);
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleScroll = (brandName: string, direction: "left" | "right") => {
    const trackElement = document.getElementById(`track-${brandName}`);
    if (!trackElement) return;

    const scrollAmount = 400;
    const newPosition =
      (scrollPositions[brandName] || 0) +
      (direction === "right" ? scrollAmount : -scrollAmount);

    trackElement.scrollTo({
      left: newPosition,
      behavior: "smooth",
    });

    setScrollPositions((prev) => ({
      ...prev,
      [brandName]: newPosition,
    }));
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("he-IL", {
      style: "currency",
      currency: "ILS",
    }).format(price);
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <p className="text-zinc-400 text-sm">
            Loading brands and products...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg p-6">
        <div className="text-center">
          <Music className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <p className="text-red-400 font-medium">{error}</p>
          <button
            onClick={fetchBrandsWithProducts}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (brandTracks.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg">
        <p className="text-zinc-400">No products found</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col bg-slate-950 rounded-lg p-6 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">{title}</h1>
        <p className="text-zinc-400 text-sm">
          {brandTracks.length} brands •{" "}
          {brandTracks.reduce((sum, b) => sum + b.count, 0)} total products
        </p>
      </div>

      {/* Brand Tracks Container */}
      <div className="flex-1 flex flex-col gap-6 overflow-auto pb-4">
        {brandTracks.map((brand) => (
          <div key={brand.name} className="flex flex-col gap-2">
            {/* Brand Header */}
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2">
                <Music className="w-4 h-4 text-blue-500" />
                <h2 className="text-lg font-semibold text-white">
                  {brand.name}
                </h2>
                <span className="text-xs text-zinc-500 bg-slate-900 px-2 py-1 rounded">
                  {brand.count} items
                </span>
              </div>
            </div>

            {/* Horizontal Track with Scroll Controls */}
            <div className="flex items-center gap-3">
              {/* Left Arrow */}
              <button
                onClick={() => handleScroll(brand.name, "left")}
                className="flex-shrink-0 p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-zinc-400 hover:text-blue-400 transition"
                aria-label="Scroll left"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              {/* Product Track (Horizontal Scroll) */}
              <div
                id={`track-${brand.name}`}
                className="flex-1 overflow-x-auto overflow-y-hidden flex gap-4 pb-2"
                style={{ scrollBehavior: "smooth" }}
              >
                {brand.products.map((product) => (
                  <div
                    key={product.id}
                    onClick={() => {
                      onProductSelect?.(product);
                      openProductPage(product.id);
                    }}
                    className="flex-shrink-0 w-48 bg-slate-900 rounded-lg overflow-hidden border border-slate-800 hover:border-blue-500 cursor-pointer transition group"
                  >
                    {/* Product Image */}
                    <div className="relative w-full h-32 bg-black overflow-hidden">
                      {product.image ? (
                        <img
                          src={product.image}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-110 transition duration-300"
                          onError={(e) => {
                            e.currentTarget.src =
                              "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%23333' width='400' height='300'/%3E%3C/svg%3E";
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-slate-800">
                          <Music className="w-8 h-8 text-zinc-600" />
                        </div>
                      )}

                      {/* In Stock Badge */}
                      <div className="absolute top-2 right-2">
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            product.in_stock
                              ? "bg-green-600 text-white"
                              : "bg-red-600 text-white"
                          }`}
                        >
                          {product.in_stock ? "In Stock" : "Out of Stock"}
                        </span>
                      </div>
                    </div>

                    {/* Product Info */}
                    <div className="p-3 flex flex-col gap-2">
                      <h3 className="font-semibold text-white text-sm truncate group-hover:text-blue-400 transition">
                        {product.name}
                      </h3>

                      {/* SKU */}
                      <p className="text-xs text-zinc-500">{product.sku}</p>

                      {/* Price */}
                      <div className="flex items-center gap-1 text-base font-bold text-blue-400">
                        <DollarSign className="w-4 h-4" />
                        {formatPrice(product.price)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Right Arrow */}
              <button
                onClick={() => handleScroll(brand.name, "right")}
                className="flex-shrink-0 p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-zinc-400 hover:text-blue-400 transition"
                aria-label="Scroll right"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="mt-6 pt-4 border-t border-slate-800">
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <p className="text-zinc-500">Total Brands</p>
            <p className="text-2xl font-bold text-blue-400">
              {brandTracks.length}
            </p>
          </div>
          <div>
            <p className="text-zinc-500">Total Products</p>
            <p className="text-2xl font-bold text-blue-400">
              {brandTracks.reduce((sum, b) => sum + b.count, 0)}
            </p>
          </div>
          <div>
            <p className="text-zinc-500">Price Range</p>
            <p className="text-2xl font-bold text-blue-400">
              {brandTracks.length > 0
                ? formatPrice(
                    Math.min(
                      ...brandTracks.flatMap((b) =>
                        b.products.map((p) => p.price),
                      ),
                    ),
                  )
                : "N/A"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
