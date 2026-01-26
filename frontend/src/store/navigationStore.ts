// frontend/src/store/navigationStore.ts
/**
 * Navigation Store v4.0 [LOCKED]
 * The Central State Machine for the 3-Step User Journey.
 */
import { create } from 'zustand';

// The 3 Distinct States
type AppView = 'GALAXY' | 'SPECTRUM' | 'PRODUCT_POP';

interface NavigationState {
  currentView: AppView;
  
  // Context Data
  activeTribeId: string | null;      // e.g., "guitars-bass"
  activeSubcategoryId: string | null; // e.g., "electric-guitars"
  activeProductId: string | null;     // e.g., "gibson-lp-std"
  activeFilters: string[];           // Layer 3 Filters (The 1176 Buttons)

  // Actions
  goToGalaxy: () => void;
  goToSpectrum: (tribeId: string, subcategoryId: string, filters: string[]) => void;
  openProductPop: (productId: string) => void;
  closeProductPop: () => void;
}

export const useNavigationStore = create<NavigationState>((set) => ({
  currentView: 'GALAXY',
  activeTribeId: null,
  activeSubcategoryId: null,
  activeProductId: null,
  activeFilters: [],

  goToGalaxy: () => set({ 
    currentView: 'GALAXY',
    activeTribeId: null,
    activeSubcategoryId: null,
    activeProductId: null,
    activeFilters: []
  }),

  goToSpectrum: (tribeId, subcategoryId, filters) => set({ 
    currentView: 'SPECTRUM',
    activeTribeId: tribeId,
    activeSubcategoryId: subcategoryId,
    activeFilters: filters,
    activeProductId: null
  }),

  openProductPop: (productId) => set({ 
    currentView: 'PRODUCT_POP', 
    activeProductId: productId 
  }),

  closeProductPop: () => set({ 
    currentView: 'SPECTRUM', // Return to Workbench, keeping state alive
    activeProductId: null 
  }),
}));
