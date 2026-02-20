/**
 * DashboardView — Mission Control  (Spec 01 v2.0 · Stitch redesign)
 * Dense, data-forward dark console. Vercel/Linear aesthetic.
 */
import React from "react";
import {
  AlertTriangle,
  CheckCircle,
  Loader2,
  XCircle,
  Package,
  PhoneCall,
  Tag,
  RefreshCcw,
  ArrowRight,
  Database,
  Telescope,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import { format } from 'date-fns';

// ── Types ──────────────────────────────────────────────────────────────────────
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

// ── useDashboardStats ──────────────────────────────────────────────────────────
function useDashboardStats() {
  const query = useQuery<DashboardStats, Error>({
    queryKey: ["dashboardStats"],
    queryFn: async () => {
      const res = await fetch("/api/dashboard/stats");
      const text = await res.text();
      if (text.trimStart().startsWith("<")) {
        throw new Error("Backend is unreachable — check the factory server.");
      }
      if (!res.ok) {
        try {
          const j = JSON.parse(text);
          throw new Error(j.error ?? `Server error ${res.status}`);
        } catch {
          throw new Error(`Server error ${res.status}`);
        }
      }
      return JSON.parse(text) as DashboardStats;
    },
    staleTime: 30_000,
    retry: 0,
  });

  return {
    stats: query.data,
    statsError: query.error,
    errorMsg: query.error?.message,
    refetch: query.refetch,
    isLoading: query.isLoading,
  };
}

// ── LastRunStatus ──────────────────────────────────────────────────────────────
const LastRunStatus: React.FC<{
  run: DashboardStats["last_ingestion_run"];
}> = ({ run }) => {
  if (run.status === "never") return <span className="text-zinc-600">—</span>;
  if (run.status === "running")
    return (
      <span className="inline-flex items-center gap-1.5 text-blue-400">
        <Loader2 size={12} className="animate-spin" />
        Running…
      </span>
    );
  if (run.status === "failed")
    return (
      <span className="inline-flex items-center gap-1.5 text-red-400">
        <XCircle size={12} />
        Failed
      </span>
    );
  if (run.finished_at) {
    return (
      <span className="inline-flex items-center gap-1.5 text-emerald-400">
        <CheckCircle size={12} />
        {format(new Date(run.finished_at), 'dd/MM/yyyy HH:mm')}
      </span>
    );
  }
  return <span className="text-zinc-500">—</span>;
};

// ── MetricCard ─────────────────────────────────────────────────────────────────
interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  accent: "blue" | "amber" | "green" | "red" | "zinc";
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  icon,
  label,
  value,
  sub,
  accent,
  onClick,
}) => {
  const bgColor =
    accent === "blue"
      ? "bg-blue-900/20"
      : accent === "amber"
      ? "bg-amber-900/20"
      : accent === "green"
      ? "bg-green-900/20"
      : accent === "red"
      ? "bg-red-900/20"
      : "bg-zinc-900/20";

  const textColor =
    accent === "blue"
      ? "text-blue-400"
      : accent === "amber"
      ? "text-amber-400"
      : accent === "green"
      ? "text-green-400"
      : accent === "red"
      ? "text-red-400"
      : "text-zinc-400";

  const borderColor =
    accent === "blue"
      ? "border-blue-500/30"
      : accent === "amber"
      ? "border-amber-500/30"
      : accent === "green"
      ? "border-green-500/30"
      : accent === "red"
      ? "border-red-500/30"
      : "border-zinc-500/30";

  return (
    <div
      className={`flex flex-col gap-2 p-4 rounded-xl border ${borderColor} ${
        onClick ? "cursor-pointer" : ""
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className={`flex items-center gap-2 ${textColor}`}>
          <div className="shrink-0">{React.createElement(icon, { size: 20 })}</div>
          <span className="text-sm font-medium">{label}</span>
        </div>
      </div>
      <div className="text-2xl font-semibold text-zinc-100">
        {value}
      </div>
      {sub && <div className="text-xs text-zinc-500">{sub}</div>}
    </div>
  );
};

const DashboardView: React.FC = () => {
  const { stats, statsError, errorMsg, refetch, isLoading } =
    useDashboardStats();
  const { goToInventory, goToInventoryCfp, goToIngestionStatus } =
    useNavigationStore();
  const hasStats = !!stats && !statsError;

  const renderLoadingValue = () => (
    <span className="text-zinc-600 animate-pulse">…</span>
  );

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-xl font-semibold text-zinc-100">Mission Control</h2>
        <span className="text-sm text-zinc-500">
          Operator Console · {format(new Date(), 'dd/MM/yyyy')}
        </span>
      </div>

      {errorMsg && (
        <div
          className="flex items-center gap-2 mb-6 px-4 py-3
                  bg-amber-900/20 border border-amber-500/30 rounded-xl text-sm"
        >
          <AlertTriangle size={14} className="text-amber-400 shrink-0" />
          <span className="text-amber-300 font-medium">Stats unavailable —</span>
          <span className="text-zinc-400 truncate">{errorMsg}</span>
          <button
            onClick={() => refetch()}
            className="ml-auto shrink-0 px-3 py-1 bg-zinc-700 hover:bg-zinc-600
                       text-zinc-200 text-xs rounded-lg"
          >
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <MetricCard
          icon={Package}
          label="Total products"
          value={hasStats ? stats.total_products.toLocaleString() : renderLoadingValue()}
          sub="Active SKUs"
          accent="blue"
          onClick={() => goToInventory()}
        />
        <MetricCard
          icon={PhoneCall}
          label="Call for price"
          value={hasStats ? stats.calls_for_price.toLocaleString() : renderLoadingValue()}
          sub="Missing IL price"
          accent={stats?.calls_for_price && stats.calls_for_price > 0 ? "amber" : "zinc"}
          onClick={() => goToInventoryCfp()}
        />
        <MetricCard
          icon={Tag}
          label="Active brands"
          value={hasStats ? stats.top_brands_count.toLocaleString() : renderLoadingValue()}
          sub="Distinct brands in catalog"
          accent="green"
        />
        <MetricCard
          icon={RefreshCcw}
          label="Last ingestion run"
          value={<LastRunStatus run={stats?.last_ingestion_run || { status: "never", finished_at: null, product_count: null }} />}
          sub={
            hasStats
              ? stats.last_ingestion_run.product_count
                ? `${stats.last_ingestion_run.product_count?.toLocaleString()} products synced`
                : "No run recorded"
              : ""
          }
          accent={
            stats?.last_ingestion_run.status === "failed"
              ? "red"
              : stats?.last_ingestion_run.status === "running"
              ? "blue"
              : "zinc"
          }
        />
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => goToInventory()}
          className="px-4 py-2 text-sm font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-100 rounded-lg"
        >
          Open Inventory Master
        </button>
        <button
          onClick={() => goToIngestionStatus()}
          className="px-4 py-2 text-sm font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-100 rounded-lg"
        >
          Data Pipeline
        </button>
      </div>
    </div>
  );
};

export default DashboardView;