import React, { Suspense } from "react";
import { LayoutDashboard, PackageSearch, Server } from "lucide-react";
import { useNavigationStore } from "./store/navigationStore";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { GlobalSearch } from "./components/GlobalSearch";

// Strict Lazy Loading (Only professional views)
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

function App() {
  const { currentView, goToDashboard, goToInventory } = useNavigationStore();

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen bg-black text-zinc-100 font-sans overflow-hidden">
        {/* SIDEBAR */}
        <aside className="w-64 border-r border-zinc-800 bg-zinc-950 flex flex-col">
          <div className="h-16 flex items-center px-6 border-b border-zinc-800 gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white">
              H
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold">Halilit SC</span>
              <span className="text-[10px] text-zinc-500 tracking-widest">
                OPERATOR CONSOLE
              </span>
            </div>
          </div>
          <nav className="p-4 space-y-2">
            <button
              onClick={goToDashboard}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded text-sm transition-colors ${currentView === "DASHBOARD" ? "bg-zinc-900 text-blue-400" : "text-zinc-400 hover:text-white"}`}
            >
              <LayoutDashboard size={18} /> Overview
            </button>
            <button
              onClick={goToInventory}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded text-sm transition-colors ${currentView === "INVENTORY" || currentView === "PRODUCT_DETAIL" ? "bg-zinc-900 text-blue-400" : "text-zinc-400 hover:text-white"}`}
            >
              <PackageSearch size={18} /> Inventory
            </button>
            <div className="pt-4 mt-4 border-t border-zinc-800">
              <div className="flex items-center gap-3 px-3 text-zinc-500">
                <Server size={16} />
                <span className="text-xs">
                  Factory Status:{" "}
                  <span className="text-emerald-500">Online</span>
                </span>
              </div>
            </div>
          </nav>
        </aside>

        {/* MAIN STAGE */}
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-16 border-b border-zinc-800 bg-zinc-950 flex items-center justify-between px-8">
            <div className="text-sm text-zinc-500">
              System <span className="text-zinc-300">/ {currentView}</span>
            </div>
            <div className="w-96">
              <GlobalSearch />
            </div>
          </header>
          <main className="flex-1 overflow-auto bg-black relative">
            <Suspense
              fallback={
                <div className="p-10 text-zinc-500 animate-pulse">
                  Loading Factory Module...
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
