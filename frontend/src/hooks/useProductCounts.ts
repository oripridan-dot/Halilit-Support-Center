import { useState, useEffect } from "react";
import { catalogLoader } from "../lib/catalogLoader";
import { getConsolidatedProductCategory } from "../lib/categoryConsolidator";

export function useProductCounts() {
    const [counts, setCounts] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        const calculateCounts = async () => {
            try {
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
            } finally {
                if (mounted) setLoading(false);
            }
        };

        calculateCounts();

        return () => {
            mounted = false;
        };
    }, []);

    return { counts, loading };
}
