/**
 * Navigation Store — Operator Console v10
 * Simple 3-state workflow: Dashboard → Inventory → Product Detail
 * No Galaxy/Spectrum modes; strict hierarchy.
 */
import { create } from 'zustand';

export type ViewType = 'DASHBOARD' | 'INVENTORY' | 'PRODUCT_DETAIL' | 'INGESTION_STATUS';

interface NavigationState {
  currentView: ViewType;
  activeProductId: string | null;
  searchQuery: string | null;
  /** When set, InventoryView will open with Call-for-Price filter pre-applied */
  initialCfpFilter: boolean | null;

  goToDashboard: () => void;
  goToInventory: (searchQuery?: string) => void;
  /** Navigate to inventory pre-filtered to Call-for-Price products */
  goToInventoryCfp: () => void;
  goToProduct: (productId: string) => void;
  goToIngestionStatus: () => void;
  goBack: () => void;
  setSearchQuery: (query: string | null) => void;
}

export const useNavigationStore = create<NavigationState>((set, get) => ({
  currentView: 'DASHBOARD',
  activeProductId: null,
  searchQuery: null,
  initialCfpFilter: null,

  goToDashboard: () => set({ currentView: 'DASHBOARD', activeProductId: null, searchQuery: null, initialCfpFilter: null }),
  goToInventory: (searchQuery?: string) => set({
    currentView: 'INVENTORY',
    activeProductId: null,
    searchQuery: searchQuery ?? null,
    initialCfpFilter: null,
  }),
  goToInventoryCfp: () => set({
    currentView: 'INVENTORY',
    activeProductId: null,
    searchQuery: null,
    initialCfpFilter: true,
  }),

  goToProduct: (productId) =>
    set({
      currentView: 'PRODUCT_DETAIL',
      activeProductId: productId,
      initialCfpFilter: null,
    }),

  goToIngestionStatus: () =>
    set({ currentView: 'INGESTION_STATUS', activeProductId: null, initialCfpFilter: null }),

  goBack: () => {
    const { currentView } = get();
    if (currentView === 'PRODUCT_DETAIL') {
      set({ currentView: 'INVENTORY', activeProductId: null, searchQuery: null, initialCfpFilter: null });
    } else if (currentView === 'INGESTION_STATUS') {
      set({ currentView: 'DASHBOARD', activeProductId: null, searchQuery: null, initialCfpFilter: null });
    } else {
      set({ currentView: 'DASHBOARD', activeProductId: null, searchQuery: null, initialCfpFilter: null });
    }
  },
  setSearchQuery: (query: string | null) => set({ searchQuery: query }),
}));
