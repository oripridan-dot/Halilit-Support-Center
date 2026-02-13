/**
 * Spectrum Store v2 — Zustand state for the redesigned Spectrum view.
 * 
 * Manages:
 * - Semantic zoom level (galaxy → constellation → cluster → star)
 * - Instrument family navigation
 * - Sub-category and body type filtering
 * - Brand filtering
 * - Model expansion (subtrack)
 */
import { create } from 'zustand';
import type { ZoomLevel } from '../types/spectrum';
import { ZOOM_ORDER } from '../types/spectrum';

export interface SpectrumV2State {
    // Current zoom level
    zoom: ZoomLevel;
    // Selected instrument family (e.g., "guitars")
    activeFamily: string | null;
    // Selected sub-category within family (e.g., "electric")
    activeSubCategory: string | null;
    // Selected body type within sub-category (e.g., "lp_type")
    activeBodyType: string | null;
    // Selected brand filter
    activeBrand: string | null;
    // Expanded model key (showing variations in subtrack)
    expandedModel: string | null;
    // Tier filter
    activeTier: string | null;
    // Search query within spectrum
    searchQuery: string;

    // Actions
    setZoom: (zoom: ZoomLevel) => void;
    zoomIn: () => void;
    zoomOut: () => void;
    setFamily: (family: string | null) => void;
    setSubCategory: (sub: string | null) => void;
    setBodyType: (bodyType: string | null) => void;
    setBrand: (brand: string | null) => void;
    setTier: (tier: string | null) => void;
    setSearchQuery: (query: string) => void;
    toggleModel: (modelKey: string) => void;
    reset: () => void;
}

export const useSpectrumV2Store = create<SpectrumV2State>((set, get) => ({
    zoom: 'cluster',
    activeFamily: null,
    activeSubCategory: null,
    activeBodyType: null,
    activeBrand: null,
    expandedModel: null,
    activeTier: null,
    searchQuery: '',

    setZoom: (zoom) => set({ zoom }),

    zoomIn: () => {
        const idx = ZOOM_ORDER.indexOf(get().zoom);
        if (idx < ZOOM_ORDER.length - 1) {
            set({ zoom: ZOOM_ORDER[idx + 1] });
        }
    },

    zoomOut: () => {
        const idx = ZOOM_ORDER.indexOf(get().zoom);
        if (idx > 0) {
            set({ zoom: ZOOM_ORDER[idx - 1], expandedModel: null });
        }
    },

    setFamily: (family) => set({
        activeFamily: family,
        activeSubCategory: null,
        activeBodyType: null,
        activeBrand: null,
        expandedModel: null,
        activeTier: null,
        // Auto-zoom: selecting a family goes to constellation
        zoom: family ? 'constellation' : 'galaxy',
    }),

    setSubCategory: (sub) => set({
        activeSubCategory: sub,
        activeBodyType: null,
        expandedModel: null,
        // Auto-zoom: sub-category goes to cluster
        zoom: 'cluster',
    }),

    setBodyType: (bodyType) => set({
        activeBodyType: bodyType,
        expandedModel: null,
    }),

    setBrand: (brand) => set((state) => ({
        activeBrand: brand,
        expandedModel: null,
        // If picking a brand from constellation, zoom into cluster
        zoom: state.zoom === 'constellation' ? 'cluster' : state.zoom,
    })),

    setTier: (tier) => set({ activeTier: tier }),

    setSearchQuery: (query) => set({ searchQuery: query }),

    toggleModel: (modelKey) => set((state) => ({
        expandedModel: state.expandedModel === modelKey ? null : modelKey,
        zoom: state.expandedModel === modelKey ? 'cluster' : 'star',
    })),

    reset: () => set({
        zoom: 'cluster',
        activeFamily: null,
        activeSubCategory: null,
        activeBodyType: null,
        activeBrand: null,
        expandedModel: null,
        activeTier: null,
        searchQuery: '',
    }),
}));
