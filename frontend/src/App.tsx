/**
 * HALILIT SUPPORT CENTER — Operator Console v10
 *
 * Professional shell layout:
 * - Persistent sidebar (Overview, Inventory Master, System)
 * - Header with breadcrumbs and global search (Command-K)
 * - Views: Dashboard, Inventory, Product Detail
 */
import React, { Suspense } from "react";
import {
  LayoutDashboard,
  PackageSearch,
  Settings,
  Server,
  LifeBuoy,
} from "lucide-react";
import { useNavigationStore } from "./store/navigationStore";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { GlobalSearch } from "./components/GlobalSearch";

const DashboardView = React.lazy(() =>
  import("./components/views/DashboardView").then((m) => ({ default: m.DashboardView }))
);
const InventoryView = React.lazy(() =>
  import("./components/views/InventoryView").then((m) => ({ default: m.InventoryView }))
);
const ProductDetailView = React.lazy(() =>
  import("./components/views/ProductDetailView").then((m) => ({ default: m.ProductDetailView }))
);
const IngestionStatusView = React.lazy(() =>
  import("./components/views/IngestionStatusView").then((m) => ({ default: m.IngestionStatusView }))
);

const SidebarItem = ({
  icon: Icon,
  label,
  isActive,
  onClick,
}: {
  icon: React.ElementType;
  label: string;
  isActive: boolean;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-black ${
      isActive
        ? "bg-blue-600/10 text-blue-400 border border-blue-600/20"
        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
    }`}
  >
    <Icon size={18} aria-hidden />
    {label}
  </button>
);

const LoadingScreen = () => (
  <div className="h-full w-full flex items-center justify-center bg-zinc-950">
    <div className="flex flex-col items-center gap-3">
      <div
        className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
        aria-hidden
      />
      <span className="text-xs text-zinc-500 font-mono uppercase tracking-widest">
        Loading System
      </span>
    </div>
  </div>
);

function App() {
  const { currentView, goToDashboard, goToInventory, goToIngestionStatus } = useNavigationStore();

  const breadcrumbLabel =
    currentView === "DASHBOARD"
      ? "Overview"
      : currentView === "INVENTORY"
        ? "Inventory Master"
        : currentView === "INGESTION_STATUS"
          ? "Ingestion Status"
          : "Product Intelligence";

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen bg-zinc-950 text-zinc-100 font-sans overflow-hidden selection:bg-blue-500/30">
        <aside
          className="w-64 flex-shrink-0 border-r border-zinc-800 bg-black flex flex-col"
          aria-label="Main navigation"
        >
          <div className="h-14 flex items-center px-4 border-b border-zinc-800 gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white shadow-lg shadow-blue-900/20">
              H
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold tracking-tight text-white">Halilit SC</span>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">
                Operator Console
              </span>
            </div>
          </div>

          <nav className="flex-1 p-3 space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
              Modules
            </div>
            <SidebarItem
              icon={LayoutDashboard}
              label="Overview"
              isActive={currentView === "DASHBOARD"}
              onClick={goToDashboard}
            />
            <SidebarItem
              icon={PackageSearch}
              label="Inventory Master"
              isActive={currentView === "INVENTORY" || currentView === "PRODUCT_DETAIL"}
              onClick={goToInventory}
            />

            <div className="mt-6 px-3 py-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
              System
            </div>
            <SidebarItem
              icon={Server}
              label="Ingestion Status"
              isActive={currentView === "INGESTION_STATUS"}
              onClick={goToIngestionStatus}
            />
            <SidebarItem icon={Settings} label="Settings" isActive={false} onClick={() => {}} />
          </nav>

          <div className="p-4 border-t border-zinc-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                <LifeBuoy size={14} className="text-zinc-400" aria-hidden />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-zinc-200">Support Agent</span>
                <span className="text-[10px] text-zinc-500">Online</span>
              </div>
            </div>
          </div>
        </aside>

        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 border-b border-zinc-800 bg-zinc-950/50 backdrop-blur flex items-center justify-between px-6">
            <div className="text-sm text-zinc-400">
              <span className="text-zinc-600">Console</span>
              <span className="mx-2" aria-hidden>
                /
              </span>
              <span className="text-zinc-200 font-medium">{breadcrumbLabel}</span>
            </div>

            <div className="w-96">
              <GlobalSearch className="w-full max-w-none" />
            </div>
          </header>

          <main className="flex-1 overflow-hidden bg-zinc-950 relative">
            <Suspense fallback={<LoadingScreen />}>
              {currentView === "DASHBOARD" && <DashboardView />}
              {currentView === "INVENTORY" && <InventoryView />}
              {currentView === "PRODUCT_DETAIL" && <ProductDetailView />}
              {currentView === "INGESTION_STATUS" && <IngestionStatusView />}
            </Suspense>
          </main>
        </div>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
