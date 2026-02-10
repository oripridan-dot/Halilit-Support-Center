// frontend/src/store/navigationStore.ts
/**
 * Navigation Store v8.2 - UNIFIED DATA PIPELINE
 * The Central State Machine for the 3-Screen User Journey.
 * 
 * Screens:
 * 1. GALAXY - Category dashboard
 * 2. SPECTRUM - Product spectrum by brand & price
 * 3. PRODUCT_PAGE - Full product analysis (renamed from PRODUCT_POP)
 * 
 * Follows unified action patterns and error handling
 */
import { create } from 'zustand';

// The Distinct States
export type AppView = 'GALAXY' | 'SPECTRUM' | 'PRODUCT_PAGE';

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
  openProductPage: (productId: string) => void;
  closeProductPage: () => void;

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
   * Navigate to Spectrum (product workbench with TierBar)
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
   * Open product analysis page
   * Renamed from openProductPop to openProductPage
   * @param productId - Product ID to analyze
   */
  openProductPage: (productId: string) => {
    if (!productId) {
      console.warn('openProductPage: Invalid product ID');
      return;
    }
    set({
      currentView: 'PRODUCT_PAGE',
      activeProductId: productId,
      lastError: null,
    });
  },

  /**
   * Close product analysis page
   * Returns to Spectrum view while keeping state
   * Renamed from closeProductPop to closeProductPage
   */
  closeProductPage: () => set({
    currentView: 'SPECTRUM',
    activeProductId: null,
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