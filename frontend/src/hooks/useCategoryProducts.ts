import { useEffect, useState } from "react";
import { catalogLoader } from "../lib/catalogLoader";
import { getConsolidatedProductCategory } from "../lib/categoryConsolidator";
import type { Product } from "../types";

export const useCategoryProducts = (subcategoryId: string | null) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      // If we don't have a subcategory, we can't filter
      // But we might want to loadAllProducts anyway for the cache?
      // No, let's keep it specific.
      if (!subcategoryId) {
        setProducts([]);
        setLoading(false);
        return;
      }

      setLoading(true);

      try {
        // 1. Efficiently load ALL products (leveraging catalogLoader cache)
        const allProducts = await catalogLoader.loadAllProducts();

        // 2. Filter using the Single Source of Truth Logic
        // This ensures what you see in the "Galaxy" view matches search/filtering elsewhere
        const filtered = allProducts.filter((p) => {
          const { spectrumId } = getConsolidatedProductCategory(p);
          return spectrumId === subcategoryId;
        });

        setProducts(filtered);
      } catch {
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [subcategoryId]);

  return { products, loading };
};
