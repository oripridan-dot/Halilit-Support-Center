import { useState, useEffect } from "react";
import { GalaxyCatalog, GalaxyProduct } from "../types/galaxy-schema";

export const useGalaxyData = () => {
  const [data, setData] = useState<GalaxyCatalog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load the single source of truth
    fetch("/data/galaxy_db.json")
      .then(res => {
        if (!res.ok) throw new Error("Failed to load Galaxy DB");
        return res.json();
      })
      .then((catalog: GalaxyCatalog) => {
        setData(catalog);
        setLoading(false);
      })
      .catch(err => {
        console.error("CRITICAL DATA FAILURE:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  /**
   * Helper: Semantic-ish search using the pre-computed tokens
   */
  const search = (query: string): GalaxyProduct[] => {
    if (!data) return [];
    const lowerQ = query.toLowerCase();
    return data.products.filter(p => p.searchTokens.includes(lowerQ));
  };

  return { 
    catalog: data, 
    products: data?.products || [],
    categories: data?.categories || {},
    loading, 
    error,
    search 
  };
};
