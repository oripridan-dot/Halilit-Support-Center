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

  goToDashboard: () => void;
  goToInventory: () => void;
  goToProduct: (productId: string) => void;
  goToIngestionStatus: () => void;
  goBack: () => void;
}

export const useNavigationStore = create<NavigationState>((set, get) => ({
  currentView: 'DASHBOARD',
  activeProductId: null,

  goToDashboard: () => set({ currentView: 'DASHBOARD', activeProductId: null }),
  goToInventory: () => set({ currentView: 'INVENTORY', activeProductId: null }),

  goToProduct: (productId) =>
    set({
      currentView: 'PRODUCT_DETAIL',
      activeProductId: productId,
    }),

  goToIngestionStatus: () =>
    set({ currentView: 'INGESTION_STATUS', activeProductId: null }),

  goBack: () => {
    const { currentView } = get();
    if (currentView === 'PRODUCT_DETAIL') {
      set({ currentView: 'INVENTORY', activeProductId: null });
    } else if (currentView === 'INGESTION_STATUS') {
      set({ currentView: 'DASHBOARD', activeProductId: null });
    } else {
      set({ currentView: 'DASHBOARD', activeProductId: null });
    }
  },
}));
