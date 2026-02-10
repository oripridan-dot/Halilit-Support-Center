/**
 * Product Store v8.1 — Learning Insights Feed
 *
 * Lean store for SSE learning insights from the backend.
 * Product data comes from conductor API via React Query (useConductorCatalog).
 */

import { create } from 'zustand';

export interface LearningInsight {
    brand: string;
    insight: string;
    timestamp: string;
    productId?: string;
}

interface ProductStoreState {
    learningInsights: LearningInsight[];
    addInsight: (insight: LearningInsight) => void;
    clearInsights: () => void;
}

export const useProductStore = create<ProductStoreState>()((set) => ({
    learningInsights: [],

    addInsight: (newInsight) => set((state) => ({
        learningInsights: [newInsight, ...state.learningInsights].slice(0, 20)
    })),

    clearInsights: () => set({ learningInsights: [] }),
}));
