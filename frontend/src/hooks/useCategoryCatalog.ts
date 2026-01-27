import { useEffect, useState } from "react";
import type { Product, CategoryPayload } from "../types";

export const useCategoryCatalog = (category: string | null) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [availableFilters, setAvailableFilters] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategory = async () => {
      setLoading(true);
      if (!category) {
        setProducts([]);
        setLoading(false);
        return;
      }

      try {
        const catId = category.toLowerCase();
        const res = await fetch(`/data/${catId}.json`);
        
        if (res.ok) {
          const data: CategoryPayload = await res.json();
          setProducts(data.products || []);
          // Dynamically set the 1176 buttons based on actual content
          setAvailableFilters(data.metadata?.available_filters || []);
        } else {
          setProducts([]);
          setAvailableFilters([]);
        }
      } catch (err) {
        console.error("Catalog load failed", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategory();
  }, [category]);

  return { products, availableFilters, loading };
};
