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
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";

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
        {new Date(run.finished_at).toLocaleString("en-IL", {
          dateStyle: "short",
          timeStyle: "short",
        })}
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

const ACCENT_MAP: Record<
  string,
  { icon: string; number: string; border: string; hover: string }
> = {
  blue: {
    icon: "text-blue-400 bg-blue-500/10",
    number: "text-blue-50",
    border: "border-zinc-800 hover:border-blue-800/50",
    hover: "hover:bg-blue-950/10",
  },
  amber: {
    icon: "text-amber-400 bg-amber-500/10",
    number: "text-amber-50",
    border: "border-zinc-800 hover:border-amber-800/50",
    hover: "hover:bg-amber-950/10",
  },
  green: {
    icon: "text-emerald-400 bg-emerald-500/10",
    number: "text-emerald-50",
    border: "border-zinc-800 hover:border-emerald-800/50",
    hover: "hover:bg-emerald-950/10",
  },
  red: {
    icon: "text-red-400 bg-red-500/10",
    number: "text-red-50",
    border: "border-zinc-800 hover:border-red-800/50",
    hover: "hover:bg-red-950/10",
  },
  zinc: {
    icon: "text-zinc-400 bg-zinc-800",
    number: "text-zinc-100",
    border: "border-zinc-800",
    hover: "",
  },
};

const MetricCard: React.FC<MetricCardProps> = ({
  icon: Icon,
  label,
  value,
  sub,
  accent,
  onClick,
}) => {
  const a = ACCENT_MAP[accent] ?? ACCENT_MAP.zinc;
  const Tag = onClick ? "button" : "div";
  return (
    <Tag
      onClick={onClick}
      className={`
        relative flex flex-col gap-4 p-5 rounded-xl bg-[#0a0a0a] border transition-all
        ${a.border} ${onClick ? `cursor-pointer ${a.hover}` : ""}
      `}
    >
      <div className="flex items-start justify-between">
        <div className={`p-2 rounded-lg ${a.icon}`}>
          <Icon size={16} />
        </div>
        {onClick && <ArrowRight size={13} className="text-zinc-700 mt-0.5" />}
      </div>
      <div>
        <div
          className={`text-[28px] font-bold leading-none tracking-tight mb-1 ${a.number}`}
        >
          {value}
        </div>
        <div className="text-xs text-zinc-500">{label}</div>
        {sub && <div className="text-[11px] text-zinc-700 mt-1">{sub}</div>}
      </div>
    </Tag>
  );
};

// ── SkeletonCard ───────────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div className="flex flex-col gap-4 p-5 rounded-xl bg-[#0a0a0a] border border-zinc-900">
    <div className="w-8 h-8 rounded-lg bg-zinc-900 animate-pulse" />
    <div className="space-y-1.5">
      <div className="h-7 w-20 rounded bg-zinc-900 animate-pulse" />
      <div className="h-3 w-28 rounded bg-zinc-900 animate-pulse" />
    </div>
  </div>
);

// ── DashboardView ──────────────────────────────────────────────────────────────
const DashboardView: React.FC = () => {
  const { stats, errorMsg, refetch, isLoading } = useDashboardStats();
  const { goToInventory, goToInventoryCfp, goToIngestionStatus } =
    useNavigationStore();

  const hasStats = !!stats && !errorMsg;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-zinc-100 mb-0.5">
          Mission Control
        </h1>
        <p className="text-sm text-zinc-600">
          Real-time catalog and pipeline status
        </p>
      </div>

      {/* Error banner */}
      {errorMsg && (
        <div className="flex items-center gap-3 mb-6 px-4 py-3 rounded-xl bg-amber-950/20 border border-amber-900/40 text-sm">
          <AlertTriangle size={13} className="text-amber-400 shrink-0" />
          <span className="text-amber-300 font-medium">
            Stats unavailable —
          </span>
          <span className="text-zinc-500 truncate flex-1">{errorMsg}</span>
          <button
            onClick={() => refetch()}
            className="ml-auto shrink-0 px-3 py-1 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Metrics grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <MetricCard
              icon={Package}
              label="Total Products"
              value={hasStats ? stats.total_products.toLocaleString() : "—"}
              sub="Active SKUs"
              accent="blue"
              onClick={() => goToInventory()}
            />
            <MetricCard
              icon={PhoneCall}
              label="Call for Price"
              value={hasStats ? stats.calls_for_price.toLocaleString() : "—"}
              sub="Missing IL price"
              accent={hasStats && stats.calls_for_price > 0 ? "amber" : "zinc"}
              onClick={() => goToInventoryCfp()}
            />
            <MetricCard
              icon={Tag}
              label="Active Brands"
              value={hasStats ? stats.top_brands_count.toLocaleString() : "—"}
              sub="Distinct brands in catalog"
              accent="green"
            />
            <MetricCard
              icon={RefreshCcw}
              label="Last Ingestion"
              value={
                <LastRunStatus
                  run={
                    hasStats
                      ? stats.last_ingestion_run
                      : {
                          status: "never",
                          finished_at: null,
                          product_count: null,
                        }
                  }
                />
              }
              sub={
                hasStats && stats.last_ingestion_run.product_count
                  ? `${stats.last_ingestion_run.product_count.toLocaleString()} products synced`
                  : "No run recorded"
              }
              accent={
                hasStats && stats.last_ingestion_run.status === "failed"
                  ? "red"
                  : hasStats && stats.last_ingestion_run.status === "running"
                    ? "blue"
                    : "zinc"
              }
            />
          </>
        )}
      </div>

      {/* Quick Actions */}
      <div>
        <p className="text-[11px] text-zinc-700 uppercase tracking-widest mb-3 font-medium">
          Quick Actions
        </p>
        <div className="flex gap-3">
          <button
            onClick={() => goToInventory()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-900 hover:bg-zinc-800
              border border-zinc-800 hover:border-zinc-700 text-zinc-300 text-sm font-medium transition-all"
          >
            <Package size={14} />
            Open Inventory Master
          </button>
          <button
            onClick={() => goToIngestionStatus()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-zinc-900 hover:bg-zinc-800
              border border-zinc-800 hover:border-zinc-700 text-zinc-300 text-sm font-medium transition-all"
          >
            <Database size={14} />
            Data Pipeline
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardView;
