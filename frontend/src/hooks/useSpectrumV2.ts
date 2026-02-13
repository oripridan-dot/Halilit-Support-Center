/**
 * useSpectrumV2 — Data hooks for the redesigned Spectrum view.
 * 
 * Fetches model-grouped data from /api/spectrum/ endpoints,
 * reacting to zoom level and filter changes from spectrumV2Store.
 */
import { useQuery } from '@tanstack/react-query';
import { useSpectrumV2Store } from '../store/spectrumV2Store';
import type {
    SpectrumResponse,
    FamiliesResponse,
} from '../types/spectrum';

/**
 * Fetch the instrument family tree for sidebar navigation.
 * Rarely changes — long cache time.
 */
export function useInstrumentFamilies() {
    return useQuery<FamiliesResponse>({
        queryKey: ['spectrum-v2', 'families'],
        queryFn: async () => {
            const res = await fetch('/api/spectrum/families');
            if (!res.ok) throw new Error('Failed to fetch instrument families');
            return res.json();
        },
        staleTime: 10 * 60 * 1000, // 10 minutes
        gcTime: 30 * 60 * 1000,
    });
}

/**
 * Fetch model groups shaped by current zoom level and filters.
 * Reacts to spectrumV2Store state changes via query key.
 */
export function useSpectrumModels() {
    const {
        zoom,
        activeFamily,
        activeSubCategory,
        activeBodyType,
        activeBrand,
        activeTier,
        searchQuery,
    } = useSpectrumV2Store();

    return useQuery<SpectrumResponse>({
        queryKey: [
            'spectrum-v2', 'models',
            zoom, activeFamily, activeSubCategory, activeBodyType,
            activeBrand, activeTier, searchQuery,
        ],
        queryFn: async () => {
            const params = new URLSearchParams({ zoom });
            if (activeFamily) params.set('family', activeFamily);
            if (activeSubCategory) params.set('sub_category', activeSubCategory);
            if (activeBodyType) params.set('body_type', activeBodyType);
            if (activeBrand) params.set('brand', activeBrand);
            if (activeTier) params.set('tier', activeTier);
            if (searchQuery.trim()) params.set('search', searchQuery.trim());

            const res = await fetch(`/api/spectrum/models?${params}`);
            if (!res.ok) throw new Error('Failed to fetch spectrum data');
            return res.json();
        },
        staleTime: 2 * 60 * 1000, // 2 minutes
        gcTime: 5 * 60 * 1000,
    });
}
