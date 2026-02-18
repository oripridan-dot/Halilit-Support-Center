/**
 * HALILIT SUPPORT CENTER — Operator Console (Factory Shell)
 * Strict router: Mission Control, Inventory Master, Product Intelligence.
 * No Galaxy/Spectrum imports. Spec-driven: see OPERATOR_CONSOLE_SPEC.md and specs/
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

// Strict Lazy Loading — No Galaxy imports allowed
const DashboardView = React.lazy(() => import("./components/views/DashboardView"));
const InventoryView = React.lazy(() => import("./components/views/InventoryView"));
const ProductDetailView = React.lazy(() =>
  import("./components/views/ProductDetailView")
);

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

const SidebarItem = ({ icon: Icon, label, isActive, onClick }: SidebarItemProps) => (
  <button
    type="button"
    onClick={onClick}
    aria-current={isActive ? "page" : undefined}
    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-black ${
      isActive
        ? "bg-blue-600/10 text-blue-400 border border-blue-600/20 shadow-sm"
        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
    }`}
  >
    <Icon size={18} aria-hidden />
    {label}
  </button>
);

function App() {
  const { currentView, goToDashboard, goToInventory } = useNavigationStore();

  const breadcrumbLabel =
    currentView === "DASHBOARD"
      ? "Mission Control"
      : currentView === "INVENTORY"
        ? "Inventory Master"
        : "Product Intelligence";

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen bg-black text-zinc-100 font-sans overflow-hidden">
        {/* OPERATOR SIDEBAR */}
        <aside
          className="w-64 flex-shrink-0 border-r border-zinc-800 bg-zinc-950 flex flex-col"
          aria-label="Main navigation"
        >
          <div className="h-16 flex items-center px-6 border-b border-zinc-800 gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white">
              H
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white">Halilit SC</span>
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest">
                Operator Console
              </span>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            <div className="px-2 py-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-2">
              Workflows
            </div>
            <SidebarItem
              icon={LayoutDashboard}
              label="Mission Control"
              isActive={currentView === "DASHBOARD"}
              onClick={goToDashboard}
            />
            <SidebarItem
              icon={PackageSearch}
              label="Inventory Master"
              isActive={
                currentView === "INVENTORY" || currentView === "PRODUCT_DETAIL"
              }
              onClick={goToInventory}
            />

            <div className="mt-8 px-2 py-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-2">
              System
            </div>
            <SidebarItem
              icon={Server}
              label="Data Pipeline"
              isActive={false}
              onClick={() => {}}
            />
            <SidebarItem
              icon={Settings}
              label="Configuration"
              isActive={false}
              onClick={() => {}}
            />
          </nav>

          <div className="p-4 border-t border-zinc-800 bg-zinc-900/30">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                <LifeBuoy size={14} className="text-zinc-400" aria-hidden />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-zinc-300">
                  System Active
                </span>
                <span className="text-[10px] text-emerald-500">
                  Connected to Factory
                </span>
              </div>
            </div>
          </div>
        </aside>

        {/* FACTORY VIEWPORT */}
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-16 border-b border-zinc-800 bg-zinc-950 flex items-center justify-between px-8">
            <div className="text-sm breadcrumbs text-zinc-500">
              <span>Console</span>
              <span className="mx-2" aria-hidden>
                /
              </span>
              <span className="text-zinc-200 font-medium">
                {breadcrumbLabel}
              </span>
            </div>
            <div className="w-96">
              <GlobalSearch />
            </div>
          </header>

          <main className="flex-1 overflow-hidden bg-black relative">
            <Suspense
              fallback={
                <div className="h-full w-full flex items-center justify-center">
                  <span className="text-zinc-500 animate-pulse font-mono text-xs">
                    LOADING FACTORY MODULE...
                  </span>
                </div>
              }
            >
              {currentView === "DASHBOARD" && <DashboardView />}
              {currentView === "INVENTORY" && <InventoryView />}
              {currentView === "PRODUCT_DETAIL" && <ProductDetailView />}
              {currentView === "INGESTION_STATUS" && (
                <div className="h-full flex items-center justify-center text-zinc-500 text-sm">
                  Data Pipeline — see specs/interface and factory_reset.sh
                </div>
              )}
            </Suspense>
          </main>
        </div>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
