// frontend/src/store/navigationStore.ts
/**
 * Navigation Store v4.1 - STANDARDIZED COMMUNICATION PROTOCOL
 * The Central State Machine for the 3-Step User Journey.
 * 
 * Follows unified action patterns and error handling
 */
import { create } from 'zustand';

// The Distinct States
export type AppView = 'GALAXY' | 'SPECTRUM' | 'PRODUCT_POP' | 'MODEL_SHOWCASE' | 'TIER_BAR';

/**
 * Core navigation state that determines what the user sees
 */
export interface NavigationState {
  // Current view
  currentView: AppView;

  // Context Data
  activeTribeId: string | null;      // e.g., "guitars-bass"
  activeSubcategoryId: string | null; // e.g., "electric-guitars"
  activeProductId: string | null;     // e.g., "gibson-lp-std"
  activeFilters: string[];           // Layer 3 Filters (The 1176 Buttons)

  // Error handling
  lastError: Error | null;
  clearError: () => void;

  // Actions (Following standardized pattern)
  goToGalaxy: () => void;
  goToSpectrum: (tribeId: string, subcategoryId: string, filters: string[]) => void;
  openProductPop: (productId: string) => void;
  closeProductPop: () => void;
  showModelShowcase: () => void;
  showTierBar: () => void;

  // Utility actions
  updateFilters: (filters: string[]) => void;
}

/**
 * Create the navigation store with strictly typed actions
 */
export const useNavigationStore = create<NavigationState>((set) => ({
  // Initial state
  currentView: 'GALAXY',
  activeTribeId: null,
  activeSubcategoryId: null,
  activeProductId: null,
  activeFilters: [],
  lastError: null,

  // Error handling
  clearError: () => set({ lastError: null }),

  // Navigation Actions - All follow consistent patterns

  /**
   * Navigate back to Galaxy dashboard
   * Resets all selection state
   */
  goToGalaxy: () => set({
    currentView: 'GALAXY',
    activeTribeId: null,
    activeSubcategoryId: null,
    activeProductId: null,
    activeFilters: [],
    lastError: null,
  }),

  /**
   * Navigate to Spectrum (product workbench)
   * @param tribeId - Main category ID
   * @param subcategoryId - Subcategory ID
   * @param filters - Active filter tags
   */
  goToSpectrum: (tribeId: string, subcategoryId: string, filters: string[]) => {
    if (!tribeId || !subcategoryId) {
      console.warn('goToSpectrum: Invalid parameters', { tribeId, subcategoryId });
      return;
    }
    set({
      currentView: 'SPECTRUM',
      activeTribeId: tribeId,
      activeSubcategoryId: subcategoryId,
      activeFilters: filters,
      activeProductId: null,
      lastError: null,
    });
  },

  /**
   * Open product detail modal
   * @param productId - Product ID to display
   */
  openProductPop: (productId: string) => {
    if (!productId) {
      console.warn('openProductPop: Invalid product ID');
      return;
    }
    set({
      currentView: 'PRODUCT_POP',
      activeProductId: productId,
      lastError: null,
    });
  },

  /**
   * Close product detail modal
   * Returns to Spectrum view while keeping state
   */
  closeProductPop: () => set({
    currentView: 'SPECTRUM',
    activeProductId: null,
    lastError: null,
  }),

  /**
   * Navigate to 3D Model Showcase
   */
  showModelShowcase: () => set({
    currentView: 'MODEL_SHOWCASE',
    lastError: null,
  }),

  /**
   * Show the Tier Bar (Products by Brand & Price)
   */
  showTierBar: () => set({
    currentView: 'TIER_BAR',
    lastError: null,
  }),

  /**
   * Update active filters (utility action)
   * Keeps user on Spectrum view
   */
  updateFilters: (filters: string[]) => set((state) => {
    // Only update if on Spectrum view
    if (state.currentView === 'SPECTRUM') {
      return { activeFilters: filters, lastError: null };
    }
    return state;
  }),
}));