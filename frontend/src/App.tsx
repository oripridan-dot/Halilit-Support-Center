import React, { Suspense } from "react";
import { LayoutDashboard, PackageSearch, Server } from "lucide-react";
import { useNavigationStore } from "./store/navigationStore";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { GlobalSearch } from "./components/GlobalSearch";

// --- Factory Imports (Lazy) ---
const DashboardView = React.lazy(() => import("./components/views/DashboardView"));
const InventoryView = React.lazy(() => import("./components/views/InventoryView"));
const ProductDetailView = React.lazy(() => import("./components/views/ProductDetailView"));

// --- Components ---
const SidebarItem = ({ icon: Icon, label, isActive, onClick }: any) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? "bg-blue-600/10 text-blue-400 border border-blue-600/20"
        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
    }`}
  >
    <Icon size={18} />
    {label}
  </button>
);

function App() {
  const { currentView, goToDashboard, goToInventory } = useNavigationStore();

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen bg-black text-zinc-100 font-sans overflow-hidden">
        {/* SIDEBAR */}
        <aside className="w-64 flex-shrink-0 border-r border-zinc-800 bg-zinc-950 flex flex-col">
          <div className="h-16 flex items-center px-6 border-b border-zinc-800 gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white">H</div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white">Halilit SC</span>
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest">Operator Console</span>
            </div>
          </div>
          <nav className="flex-1 p-4 space-y-1">
            <SidebarItem icon={LayoutDashboard} label="Overview" isActive={currentView === 'DASHBOARD'} onClick={goToDashboard} />
            <SidebarItem icon={PackageSearch} label="Inventory" isActive={currentView === 'INVENTORY' || currentView === 'PRODUCT_DETAIL'} onClick={goToInventory} />
            <div className="mt-8 px-2 py-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest">System</div>
            <SidebarItem icon={Server} label="Data Pipeline" isActive={false} onClick={() => {}} />
          </nav>
        </aside>

        {/* MAIN CONTENT */}
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-16 border-b border-zinc-800 bg-zinc-950 flex items-center justify-between px-8">
            <div className="text-sm text-zinc-500">
              Console / <span className="text-zinc-200">{currentView}</span>
            </div>
            <div className="w-96"><GlobalSearch /></div>
          </header>
          <main className="flex-1 overflow-hidden bg-black relative">
            <Suspense fallback={<div className="p-8 text-zinc-600">Loading Module...</div>}>
              {currentView === 'DASHBOARD' && <DashboardView />}
              {currentView === 'INVENTORY' && <InventoryView />}
              {currentView === 'PRODUCT_DETAIL' && <ProductDetailView />}
            </Suspense>
          </main>
        </div>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
