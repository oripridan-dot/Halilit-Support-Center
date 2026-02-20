import React, { Suspense, useState } from "react";
import {
  LayoutDashboard,
  PackageSearch,
  Server,
  ChevronLeft,
  ChevronRight,
  Activity,
  Zap,
} from "lucide-react";
import { useNavigationStore } from "./store/navigationStore";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { GlobalSearch } from "./components/GlobalSearch";

// Strict Lazy Loading
const DashboardView = React.lazy(
  () => import("./components/views/DashboardView"),
);
const InventoryView = React.lazy(
  () => import("./components/views/InventoryView"),
);
const ProductDetailView = React.lazy(
  () => import("./components/views/ProductDetailView"),
);
const IngestionStatusView = React.lazy(
  () => import("./components/views/IngestionStatusView"),
);

const VIEW_LABELS: Record<string, string> = {
  DASHBOARD: "Mission Control",
  INVENTORY: "Inventory Master",
  PRODUCT_DETAIL: "Product Intelligence",
  INGESTION_STATUS: "Data Pipeline",
};

const NAV_ITEMS = [
  { view: "DASHBOARD" as const, icon: LayoutDashboard, label: "Overview" },
  { view: "INVENTORY" as const, icon: PackageSearch, label: "Inventory" },
];

function App() {
  const { currentView, goToDashboard, goToInventory } = useNavigationStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const viewLabel = VIEW_LABELS[currentView] ?? currentView;

  const navHandlers: Record<string, () => void> = {
    DASHBOARD: () => goToDashboard(),
    INVENTORY: () => goToInventory(),
  };

  const isInventoryActive =
    currentView === "INVENTORY" || currentView === "PRODUCT_DETAIL";

  return (
    <GlobalErrorBoundary>
      <div
        className="flex h-screen w-screen bg-black text-zinc-100 overflow-hidden"
        style={{ fontFamily: "Inter, system-ui, sans-serif" }}
      >
        {/* ── SIDEBAR ── */}
        <aside
          className="relative flex flex-col bg-[#0a0a0a] border-r border-zinc-900 transition-all duration-200"
          style={{ width: sidebarOpen ? 220 : 56 }}
        >
          {/* Logo */}
          <div
            className="h-12 flex items-center border-b border-zinc-900 shrink-0 overflow-hidden"
            style={{ padding: sidebarOpen ? "0 16px" : "0 14px" }}
          >
            <div className="w-7 h-7 bg-blue-600 rounded-md flex items-center justify-center font-black text-white text-sm shrink-0">
              H
            </div>
            {sidebarOpen && (
              <div className="ml-3 flex flex-col leading-tight">
                <span className="text-[13px] font-semibold tracking-tight text-zinc-100">
                  Halilit SC
                </span>
                <span className="text-[9px] text-zinc-600 tracking-[0.12em] uppercase">
                  Operator Console
                </span>
              </div>
            )}
          </div>

          {/* Nav Items */}
          <nav className="flex-1 py-3 space-y-0.5 px-2">
            {NAV_ITEMS.map(({ view, icon: Icon, label }) => {
              const active =
                view === "DASHBOARD"
                  ? currentView === "DASHBOARD"
                  : isInventoryActive;
              return (
                <button
                  key={view}
                  onClick={navHandlers[view]}
                  title={!sidebarOpen ? label : undefined}
                  className={`
                    w-full flex items-center gap-2.5 rounded-md text-[13px] font-medium transition-all
                    ${sidebarOpen ? "px-3 py-2" : "px-0 py-2 justify-center"}
                    ${
                      active
                        ? "bg-blue-600/10 text-blue-400"
                        : "text-zinc-500 hover:text-zinc-200 hover:bg-zinc-900"
                    }
                  `}
                >
                  <Icon size={15} className="shrink-0" />
                  {sidebarOpen && <span>{label}</span>}
                </button>
              );
            })}
          </nav>

          {/* Factory Status */}
          <div className="pb-3 px-2 border-t border-zinc-900 pt-3">
            <div
              title={!sidebarOpen ? "Factory Online" : undefined}
              className={`flex items-center gap-2 rounded-md py-1.5 ${sidebarOpen ? "px-3" : "justify-center"}`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0 animate-pulse" />
              {sidebarOpen && (
                <span className="text-[11px] text-zinc-600">
                  Factory <span className="text-emerald-500">Online</span>
                </span>
              )}
            </div>
          </div>

          {/* Collapse Toggle */}
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="absolute -right-3 top-8 w-6 h-6 rounded-full bg-zinc-900 border border-zinc-800
              flex items-center justify-center text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors z-10"
          >
            {sidebarOpen ? (
              <ChevronLeft size={12} />
            ) : (
              <ChevronRight size={12} />
            )}
          </button>
        </aside>

        {/* ── MAIN STAGE ── */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="h-12 border-b border-zinc-900 bg-[#0a0a0a] flex items-center justify-between px-5 shrink-0">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-zinc-600">System</span>
              <span className="text-zinc-700">/</span>
              <span className="text-zinc-300 font-medium">{viewLabel}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-72">
                <GlobalSearch />
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800">
                <Zap size={11} className="text-blue-400" />
                <span className="text-[11px] text-zinc-500">v9.7.1</span>
              </div>
            </div>
          </header>

          {/* Content */}
          <main className="flex-1 overflow-auto bg-black">
            <Suspense
              fallback={
                <div className="flex items-center gap-3 p-8 text-zinc-600">
                  <Activity size={14} className="animate-pulse" />
                  <span className="text-sm">Loading module…</span>
                </div>
              }
            >
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
