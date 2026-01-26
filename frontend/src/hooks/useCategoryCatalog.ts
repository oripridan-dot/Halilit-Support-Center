import { useEffect, useState } from "react";
import { consolidateCategory } from "../lib/categoryConsolidator";
import type { Product } from "../types";

/**
 * useCategoryCatalog - Category Consolidation-Aware Product Loading
 *
 * This hook loads products and filters them using the CONSOLIDATED category system.
 * Brand categories are translated to universal UI categories for filtering.
 *
 * Flow:
 * 1. User selects consolidated category (e.g., "keys")
 * 2. Hook loads all brand catalogs (discovered via index.json)
 * 3. For each product, consolidate its brand category to UI category
 * 4. Filter products where consolidated category matches selection
 */

interface CatalogIndex {
  brands: Array<{ slug: string }>;
}

export const useCategoryCatalog = (
  category: string | null,
  brandId?: string | null,
) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      let aggregated: Product[] = [];

      try {
        let brandsToFetch: string[] = [];

        if (brandId) {
          brandsToFetch = [brandId];
        } else {
          try {
            const indexRes = await fetch("/data/index.json");
            if (indexRes.ok) {
              const indexData = (await indexRes.json()) as CatalogIndex;
              brandsToFetch = indexData.brands.map((b) => b.slug);
            }
          } catch {
            // ignore
          }
        }

        if (brandsToFetch.length === 0) {
          setLoading(false);
          return;
        }

        // Parallel fetch of all Master Files
        const promises = brandsToFetch.map((brand) =>
          fetch(`/data/${brand}.json`)
            .then((res) => {
              const contentType = res.headers.get("content-type");
              if (
                !res.ok ||
                (contentType && !contentType.includes("application/json"))
              ) {
                return null;
              }
              return res.json();
            })
            .then((data) => {
              if (!data) return [];
              return (data as { products: Product[] }).products || [];
            })
            .catch((_err) => {
              return [] as Product[];
            }),
        );

        const results = await Promise.all(promises);
        aggregated = results.flat();

        // Filter by CONSOLIDATED category
        const filtered = aggregated.filter((p) => {
          if (!category || category === "All") return true;

          const productBrand = (p.brand || "").toLowerCase();
          const productCategory = p.main_category || p.category || "";

          const consolidatedId = consolidateCategory(
            productBrand,
            productCategory,
          );

          return consolidatedId === category.toLowerCase();
        });

        setProducts(filtered);
      } catch {
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [category, brandId]);

  return { products, loading };
};
