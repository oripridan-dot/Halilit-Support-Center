/**
 * Dashboard View — Operator Console
 * Professional start screen with quick navigation cards.
 */
import React from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { Search, Package, Activity, ArrowRight } from "lucide-react";

interface DashboardCardProps {
  title: string;
  value: string;
  label: string;
  icon: React.ComponentType<{ size?: number }>;
  onClick: () => void;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  label,
  icon: Icon,
  onClick,
}) => (
  <button
    type="button"
    onClick={onClick}
    className="flex flex-col p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-blue-500/50 hover:bg-zinc-800/80 transition-all text-left group focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
  >
    <div className="flex items-center justify-between w-full mb-4">
      <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-400 group-hover:text-blue-400 group-hover:border-blue-500/30 transition-colors">
        <Icon size={24} aria-hidden />
      </div>
      <ArrowRight
        size={16}
        className="text-zinc-600 group-hover:text-zinc-300 opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0"
        aria-hidden
      />
    </div>
    <span className="text-2xl font-bold text-white mb-1">{value}</span>
    <span className="text-sm font-medium text-zinc-400">{title}</span>
    <span className="text-xs text-zinc-600 mt-2">{label}</span>
  </button>
);

const DashboardView: React.FC = () => {
  const { goToInventory, goToIngestionStatus } = useNavigationStore();
  const { totalProducts, isLoading, error, refetch } = useConductorCatalog();

  const productCount = isLoading ? "…" : totalProducts.toLocaleString();

  if (error) {
    return (
      <div className="p-8 max-w-xl">
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-6">
          <p className="text-amber-400 font-medium mb-2">Catalog unavailable</p>
          <p className="text-sm text-zinc-400 mb-4">{error}</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg"
            >
              Retry
            </button>
            <button
              type="button"
              onClick={goToIngestionStatus}
              className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-zinc-200 text-sm font-medium rounded-lg"
            >
              Ingestion Status
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Welcome back, Operator</h1>
        <p className="text-zinc-400">
          System status is nominal. {productCount} products active in catalog.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DashboardCard
          title="Inventory Master"
          value="Catalog"
          label="Browse all products & prices"
          icon={Package}
          onClick={goToInventory}
        />
        <DashboardCard
          title="Active Issues"
          value="0"
          label="No urgent alerts"
          icon={Activity}
          onClick={() => {}}
        />
        <DashboardCard
          title="Quick Lookup"
          value="Search"
          label="Press CMD+K to search"
          icon={Search}
          onClick={() => {}}
        />
      </div>
    </div>
  );
};

export default DashboardView;
export { DashboardView };
