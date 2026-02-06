import { useState, useEffect } from "react";
import { catalogLoader } from "../lib/catalogLoader";
import { getConsolidatedProductCategory } from "../lib/categoryConsolidator";

export function useProductCounts() {
    const [counts, setCounts] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let mounted = true;

        const calculateCounts = async () => {
            try {
                setError(null);
                // Ensure index is loaded
                await catalogLoader.loadIndex();

                // Use the public method `loadAllProducts` which handles loading internal brands logic
                // and respects the badge gate we implemented.
                const allProducts = await catalogLoader.loadAllProducts();

                if (!mounted) return;

                const newCounts: Record<string, number> = {};

                allProducts.forEach(p => {
                    const { spectrumId } = getConsolidatedProductCategory(p);
                    newCounts[spectrumId] = (newCounts[spectrumId] || 0) + 1;
                });

                // Debug log to ensure we are seeing data
                console.log("[useProductCounts] Calculated:", newCounts);

                setCounts(newCounts);
            } catch (err) {
                console.error("[useProductCounts] Error:", err);
                if (mounted) {
                    setError((err as Error).message || "Failed to load product counts");
                    // Keep previous counts as fallback
                    setCounts(prev => prev || {});
                }
            } finally {
                if (mounted) setLoading(false);
            }
        };

        calculateCounts();

        return () => {
            mounted = false;
        };
    }, []);

    return { counts, loading, error };
}
