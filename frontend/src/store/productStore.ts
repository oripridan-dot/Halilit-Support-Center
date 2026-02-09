/**
 * Product Store v1.0 - Phase 1F Integration
 * Manages ingested and synced products from the backend pipeline
 * 
 * Integrates with:
 * - CopilotKit pipeline results (Phase 1D)
 * - Auto-sync updates (Phase 1E)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface ProductItem {
    id: string;
    name: string;
    brand: string;
    category: string;
    price_il: number;
    status: 'APPROVED' | 'REJECTED' | 'PENDING';
    risk_score: number;
    verified: boolean;
    pricing_tier?: string;
    synced_at: string;
    source: 'pipeline' | 'import';
    metadata?: Record<string, any>;
}

export interface BatchOperation {
    id: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    total_products: number;
    processed: number;
    approved: number;
    rejected: number;
    started_at: string;
    completed_at?: string;
    progress_percent: number;
}


export interface LearningInsight {
    brand: string;
    insight: string;
    timestamp: string;
    productId?: string;
}

interface ProductStoreState {
    // Products
    products: ProductItem[];
    allProductsLoaded: boolean;
    learningInsights: LearningInsight[];

    // Batch tracking
    activeBatches: Map<string, BatchOperation>;
    batchHistory: BatchOperation[];

    // Stats
    totalProducts: number;
    approvedCount: number;
    rejectedCount: number;
    pendingCount: number;

    // Filters
    activeFilters: {
        status?: 'APPROVED' | 'REJECTED' | 'PENDING';
        brand?: string;
        category?: string;
        minPrice?: number;
        maxPrice?: number;
    };

    // Actions
    addProduct: (product: ProductItem) => void;
    addProducts: (products: ProductItem[]) => void;
    updateProduct: (id: string, updates: Partial<ProductItem>) => void;
    removeProduct: (id: string) => void;
    addInsight: (insight: LearningInsight) => void;

    // Batch operations
    startBatch: (batchId: string, totalProducts: number) => void;
    updateBatchProgress: (batchId: string, processed: number, approved: number, rejected: number) => void;
    completeBatch: (batchId: string) => void;
    failBatch: (batchId: string) => void;

    // Filtering
    setFilters: (filters: ProductStoreState['activeFilters']) => void;
    clearFilters: () => void;
    getFilteredProducts: () => ProductItem[];

    // Queries
    getProduct: (id: string) => ProductItem | undefined;
    getProductsByBrand: (brand: string) => ProductItem[];
    getProductsByCategory: (category: string) => ProductItem[];
    getProductsByStatus: (status: ProductItem['status']) => ProductItem[];

    // Statistics
    getStats: () => {
        total: number;
        approved: number;
        rejected: number;
        pending: number;
        approvalRate: number;
    };

    // Storage
    clear: () => void;
}

export const useProductStore = create<ProductStoreState>()(
    devtools(
        persist(
            (set, get) => ({
                // Initial state
                products: [],
                allProductsLoaded: false,
                learningInsights: [],
                activeBatches: new Map(),
                batchHistory: [],
                totalProducts: 0,
                approvedCount: 0,
                rejectedCount: 0,
                pendingCount: 0,
                activeFilters: {},

                // Actions

                addInsight: (newInsight) => set((state) => ({
                    learningInsights: [newInsight, ...state.learningInsights].slice(0, 10)
                })),

                addProduct: (product: ProductItem) => {
                    set((state) => {
                        const exists = state.products.find((p) => p.id === product.id);
                        if (exists) return state;

                        const newProducts = [...state.products, product];
                        return {
                            products: newProducts,
                            totalProducts: newProducts.length,
                            approvedCount:
                                state.approvedCount + (product.status === 'APPROVED' ? 1 : 0),
                            rejectedCount:
                                state.rejectedCount + (product.status === 'REJECTED' ? 1 : 0),
                            pendingCount:
                                state.pendingCount + (product.status === 'PENDING' ? 1 : 0),
                        };
                    });
                },

                // Add multiple products
                addProducts: (products: ProductItem[]) => {
                    set((state) => {
                        const existingIds = new Set(state.products.map((p) => p.id));
                        const newProducts = products.filter(
                            (p) => !existingIds.has(p.id)
                        );

                        const allProducts = [...state.products, ...newProducts];
                        const approved = allProducts.filter(
                            (p) => p.status === 'APPROVED'
                        ).length;
                        const rejected = allProducts.filter(
                            (p) => p.status === 'REJECTED'
                        ).length;
                        const pending = allProducts.filter(
                            (p) => p.status === 'PENDING'
                        ).length;

                        return {
                            products: allProducts,
                            totalProducts: allProducts.length,
                            approvedCount: approved,
                            rejectedCount: rejected,
                            pendingCount: pending,
                        };
                    });
                },

                // Update product
                updateProduct: (id: string, updates: Partial<ProductItem>) => {
                    set((state) => {
                        const oldProduct = state.products.find((p) => p.id === id);
                        if (!oldProduct) return state;

                        const newProducts = state.products.map((p) =>
                            p.id === id ? { ...p, ...updates } : p
                        );

                        let approvedDelta = 0;
                        let rejectedDelta = 0;
                        let pendingDelta = 0;

                        // Calculate deltas for status changes
                        if (updates.status && oldProduct.status !== updates.status) {
                            if (oldProduct.status === 'APPROVED') approvedDelta -= 1;
                            if (oldProduct.status === 'REJECTED') rejectedDelta -= 1;
                            if (oldProduct.status === 'PENDING') pendingDelta -= 1;

                            if (updates.status === 'APPROVED') approvedDelta += 1;
                            if (updates.status === 'REJECTED') rejectedDelta += 1;
                            if (updates.status === 'PENDING') pendingDelta += 1;
                        }

                        return {
                            products: newProducts,
                            approvedCount: state.approvedCount + approvedDelta,
                            rejectedCount: state.rejectedCount + rejectedDelta,
                            pendingCount: state.pendingCount + pendingDelta,
                        };
                    });
                },

                addInsight: (newInsight) => set((state) => ({
                    // Keep the last 10 insights for the live feed
                    learningInsights: [newInsight, ...state.learningInsights].slice(0, 10)
                })),

                // Remove product
                removeProduct: (id: string) => {
                    set((state) => {
                        const product = state.products.find((p) => p.id === id);
                        if (!product) return state;

                        const newProducts = state.products.filter((p) => p.id !== id);
                        return {
                            products: newProducts,
                            totalProducts: newProducts.length,
                            approvedCount:
                                state.approvedCount -
                                (product.status === 'APPROVED' ? 1 : 0),
                            rejectedCount:
                                state.rejectedCount -
                                (product.status === 'REJECTED' ? 1 : 0),
                            pendingCount:
                                state.pendingCount - (product.status === 'PENDING' ? 1 : 0),
                        };
                    });
                },

                // Start batch operation
                startBatch: (batchId: string, totalProducts: number) => {
                    set((state) => {
                        const batch: BatchOperation = {
                            id: batchId,
                            status: 'in_progress',
                            total_products: totalProducts,
                            processed: 0,
                            approved: 0,
                            rejected: 0,
                            started_at: new Date().toISOString(),
                            progress_percent: 0,
                        };

                        const newBatches = new Map(state.activeBatches);
                        newBatches.set(batchId, batch);

                        return {
                            activeBatches: newBatches,
                        };
                    });
                },

                // Update batch progress
                updateBatchProgress: (
                    batchId: string,
                    processed: number,
                    approved: number,
                    rejected: number
                ) => {
                    set((state) => {
                        const batch = state.activeBatches.get(batchId);
                        if (!batch) return state;

                        const newBatch = {
                            ...batch,
                            processed,
                            approved,
                            rejected,
                            progress_percent:
                                batch.total_products > 0
                                    ? (processed / batch.total_products) * 100
                                    : 0,
                        };

                        const newBatches = new Map(state.activeBatches);
                        newBatches.set(batchId, newBatch);

                        return {
                            activeBatches: newBatches,
                        };
                    });
                },

                // Complete batch
                completeBatch: (batchId: string) => {
                    set((state) => {
                        const batch = state.activeBatches.get(batchId);
                        if (!batch) return state;

                        const completedBatch = {
                            ...batch,
                            status: 'completed' as const,
                            completed_at: new Date().toISOString(),
                            progress_percent: 100,
                        };

                        const newBatches = new Map(state.activeBatches);
                        newBatches.delete(batchId);

                        return {
                            activeBatches: newBatches,
                            batchHistory: [completedBatch, ...state.batchHistory],
                        };
                    });
                },

                // Fail batch
                failBatch: (batchId: string) => {
                    set((state) => {
                        const batch = state.activeBatches.get(batchId);
                        if (!batch) return state;

                        const failedBatch = {
                            ...batch,
                            status: 'failed' as const,
                            completed_at: new Date().toISOString(),
                        };

                        const newBatches = new Map(state.activeBatches);
                        newBatches.delete(batchId);

                        return {
                            activeBatches: newBatches,
                            batchHistory: [failedBatch, ...state.batchHistory],
                        };
                    });
                },

                // Set filters
                setFilters: (filters: ProductStoreState['activeFilters']) => {
                    set((state) => ({
                        activeFilters: { ...state.activeFilters, ...filters },
                    }));
                },

                // Clear filters
                clearFilters: () => {
                    set({ activeFilters: {} });
                },

                // Get filtered products
                getFilteredProducts: () => {
                    const state = get();
                    return state.products.filter((product) => {
                        if (
                            state.activeFilters.status &&
                            product.status !== state.activeFilters.status
                        )
                            return false;
                        if (
                            state.activeFilters.brand &&
                            product.brand !== state.activeFilters.brand
                        )
                            return false;
                        if (
                            state.activeFilters.category &&
                            product.category !== state.activeFilters.category
                        )
                            return false;
                        if (
                            state.activeFilters.minPrice &&
                            product.price_il < state.activeFilters.minPrice
                        )
                            return false;
                        if (
                            state.activeFilters.maxPrice &&
                            product.price_il > state.activeFilters.maxPrice
                        )
                            return false;
                        return true;
                    });
                },

                // Get product by ID
                getProduct: (id: string) => {
                    return get().products.find((p) => p.id === id);
                },

                // Get products by brand
                getProductsByBrand: (brand: string) => {
                    return get().products.filter((p) => p.brand === brand);
                },

                // Get products by category
                getProductsByCategory: (category: string) => {
                    return get().products.filter((p) => p.category === category);
                },

                // Get products by status
                getProductsByStatus: (status: ProductItem['status']) => {
                    return get().products.filter((p) => p.status === status);
                },

                // Get statistics
                getStats: () => {
                    const state = get();
                    return {
                        total: state.totalProducts,
                        approved: state.approvedCount,
                        rejected: state.rejectedCount,
                        pending: state.pendingCount,
                        approvalRate:
                            state.totalProducts > 0
                                ? (state.approvedCount / state.totalProducts) * 100
                                : 0,
                    };
                },

                // Clear all
                clear: () => {
                    set({
                        products: [],
                        allProductsLoaded: false,
                        activeBatches: new Map(),
                        batchHistory: [],
                        totalProducts: 0,
                        approvedCount: 0,
                        rejectedCount: 0,
                        pendingCount: 0,
                        activeFilters: {},
                    });
                },
            }),
            {
                name: 'product-store',
                version: 1,
                storage: {
                    getItem: (name) => {
                        const str = localStorage.getItem(name);
                        if (!str) return null;
                        const parsed = JSON.parse(str);
                        // Restore Map from plain object
                        if (parsed?.state?.activeBatches && !(parsed.state.activeBatches instanceof Map)) {
                            parsed.state.activeBatches = new Map(Object.entries(parsed.state.activeBatches));
                        }
                        return parsed;
                    },
                    setItem: (name, value) => {
                        // Serialize Map to plain object
                        const toStore = { ...value };
                        if (toStore.state?.activeBatches instanceof Map) {
                            toStore.state = {
                                ...toStore.state,
                                activeBatches: Object.fromEntries(toStore.state.activeBatches),
                            };
                        }
                        localStorage.setItem(name, JSON.stringify(toStore));
                    },
                    removeItem: (name) => localStorage.removeItem(name),
                },
            }
        )
    )
);
