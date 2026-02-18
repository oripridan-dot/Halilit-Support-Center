/**
 * Dashboard View — Mission Control
 * Spec: specs/interface/01_operator_dashboard.md
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import {
  Package,
  PhoneCall,
  RefreshCw,
  Tag,
  ArrowRight,
  CheckCircle,
  XCircle,
  Loader2,
  AlertTriangle,
} from "lucide-react";

// ── Dashboard Stats ──────────────────────────────────────────────────────────

interface DashboardStats {
  total_products: number;
  calls_for_price: number;
  top_brands_count: number;
  last_ingestion_run: {
    status: "never" | "running" | "complete" | "failed" | "unknown";
    finished_at: string | null;
    product_count: number | null;
  };
}

function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const res = await fetch("/api/dashboard/stats");
      if (!res.ok) throw new Error(`Stats error ${res.status}`);
      return res.json();
    },
    staleTime: 30_000,
    retry: 1,
  });
}

// ── Sub-components ────────────────────────────────────────────────────────────

interface MetricCardProps {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  accent?: "blue" | "amber" | "green" | "red" | "zinc";
  onClick?: () => void;
}

const ACCENT_COLOR: Record<string, string> = {
  blue: "bg-blue-500/10 border-blue-500/30 text-blue-400",
  amber: "bg-amber-500/10 border-amber-500/30 text-amber-400",
  green: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
  red: "bg-red-500/10 border-red-500/30 text-red-400",
  zinc: "bg-zinc-800 border-zinc-700 text-zinc-400",
};

const MetricCard: React.FC<MetricCardProps> = ({
  icon: Icon,
  label,
  value,
  sub,
  accent = "zinc",
  onClick,
}) => {
  const accentCls = ACCENT_COLOR[accent];
  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className="flex flex-col gap-3 p-6 bg-zinc-900 border border-zinc-800 rounded-xl text-left transition-all cursor-pointer hover:border-blue-500/40 hover:bg-zinc-800/70 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950 group"
      >
        <div className={`self-start p-2.5 rounded-lg border ${accentCls}`}>
          <Icon size={20} aria-hidden />
        </div>
        <div>
          <div className="text-2xl font-bold text-white leading-tight">
            {value}
          </div>
          <div className="text-sm text-zinc-400 mt-0.5">{label}</div>
          {sub && <div className="text-xs text-zinc-600 mt-1">{sub}</div>}
        </div>
        <ArrowRight
          size={14}
          className="text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity mt-auto"
          aria-hidden
        />
      </button>
    );
  }
  return (
    <div className="flex flex-col gap-3 p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
      <div className={`self-start p-2.5 rounded-lg border ${accentCls}`}>
        <Icon size={20} aria-hidden />
      </div>
      <div>
        <div className="text-2xl font-bold text-white leading-tight">
          {value}
        </div>
        <div className="text-sm text-zinc-400 mt-0.5">{label}</div>
        {sub && <div className="text-xs text-zinc-600 mt-1">{sub}</div>}
      </div>
    </div>
  );
};

// ── Last Run Status ───────────────────────────────────────────────────────────

function LastRunStatus({ run }: { run: DashboardStats["last_ingestion_run"] }) {
  if (run.status === "never")
    return <span className="text-zinc-500 text-lg font-bold">—</span>;
  if (run.status === "running")
    return (
      <span className="flex items-center gap-1.5 text-blue-400 text-base font-semibold">
        <Loader2 size={13} className="animate-spin" aria-hidden /> Running…
      </span>
    );
  if (run.status === "complete" || run.status === "unknown") {
    const date = run.finished_at
      ? new Date(run.finished_at).toLocaleString("en-IL", {
          dateStyle: "short",
          timeStyle: "short",
        })
      : "—";
    return (
      <span className="flex items-center gap-1.5 text-emerald-400 text-sm font-semibold">
        <CheckCircle size={13} aria-hidden /> {date}
      </span>
    );
  }
  if (run.status === "failed")
    return (
      <span className="flex items-center gap-1.5 text-red-400 text-base font-semibold">
        <XCircle size={13} aria-hidden /> Failed
      </span>
    );
  return <span className="text-zinc-500 text-lg font-bold">—</span>;
}

// ── Main View ────────────────────────────────────────────────────────────────

const DashboardView: React.FC = () => {
  const { goToInventory, goToIngestionStatus } = useNavigationStore();
  const { isLoading: catalogLoading } = useConductorCatalog();
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch,
  } = useDashboardStats();

  const loading = catalogLoading || statsLoading;
  const spin = <span className="text-zinc-600 animate-pulse">…</span>;

  if (statsError) {
    return (
      <div className="p-8 max-w-xl">
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-amber-400" aria-hidden />
            <p className="text-amber-400 font-medium">Stats unavailable</p>
          </div>
          <p className="text-sm text-zinc-400 mb-4">{String(statsError)}</p>
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
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Mission Control</h1>
        <p className="text-sm text-zinc-500">
          Operator Console · v9.6.1 Dark Factory ·{" "}
          {new Date().toLocaleDateString("en-IL", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Key Metrics */}
      <section
        aria-label="Key metrics"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10"
      >
        <MetricCard
          icon={Package}
          label="Total products in catalog"
          value={loading ? spin : (stats?.total_products ?? 0).toLocaleString()}
          sub="Active SKUs"
          accent="blue"
          onClick={goToInventory}
        />
        <MetricCard
          icon={PhoneCall}
          label="Call for price"
          value={
            loading ? spin : (stats?.calls_for_price ?? 0).toLocaleString()
          }
          sub="Missing IL price"
          accent={stats && stats.calls_for_price > 0 ? "amber" : "zinc"}
        />
        <MetricCard
          icon={Tag}
          label="Active brands"
          value={
            loading ? spin : (stats?.top_brands_count ?? 0).toLocaleString()
          }
          sub="Distinct brands in catalog"
          accent="green"
        />
        <MetricCard
          icon={RefreshCw}
          label="Last ingestion run"
          value={
            loading ? (
              spin
            ) : stats ? (
              <LastRunStatus run={stats.last_ingestion_run} />
            ) : (
              "—"
            )
          }
          sub={
            stats?.last_ingestion_run.product_count != null
              ? `${stats.last_ingestion_run.product_count.toLocaleString()} products synced`
              : "No run recorded"
          }
          accent={
            stats?.last_ingestion_run.status === "failed"
              ? "red"
              : stats?.last_ingestion_run.status === "running"
                ? "blue"
                : "zinc"
          }
        />
      </section>

      {/* Quick Actions */}
      <section aria-label="Quick actions">
        <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={goToInventory}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-blue-400"
          >
            <Package size={16} aria-hidden /> Open Inventory Master
          </button>
          <button
            type="button"
            onClick={goToIngestionStatus}
            className="flex items-center gap-2 px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-medium rounded-lg transition-colors border border-zinc-700 focus-visible:ring-2 focus-visible:ring-blue-400"
          >
            <RefreshCw size={16} aria-hidden /> Data Pipeline
          </button>
        </div>
      </section>
    </div>
  );
};

export default DashboardView;
export { DashboardView };
