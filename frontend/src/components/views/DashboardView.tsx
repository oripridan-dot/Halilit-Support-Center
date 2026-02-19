import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle,
  Loader2,
  Package,
  PhoneMissed,
  RefreshCcw,
  XCircle,
} from "lucide-react";

import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";

interface DashboardStats {
  total_products: number;
  calls_for_price: number;
  top_brands_count: number;
  last_ingestion_run: {
    status: "never" | "running" | "ok" | "failed";
    finished_at?: string | null;
    product_count?: number | null;
  } | null;
}

interface MetricCardProps {
  icon: React.ComponentType;
  label: string;
  value: React.ReactNode; // large number or JSX status
  sub?: React.ReactNode; // small hint line below label
  accent: "blue" | "amber" | "green" | "red" | "zinc";
  onClick?: () => void; // if present → render as <button>
}

const MetricCard: React.FC<MetricCardProps> = ({
  icon: Icon,
  label,
  value,
  sub,
  accent,
  onClick,
}) => {
  const textColor = `text-${accent}-400`;
  const bgClass = `bg-zinc-800 hover:bg-zinc-700`; // hover only if onClick is defined
  const cursorClass = onClick ? "cursor-pointer" : "";

  const cardContent = (
    <div className="flex flex-col gap-1 p-4 rounded-xl">
      <div className="flex items-center gap-2">
        <Icon className={textColor} size={20} />
        <h3 className="text-lg font-semibold text-zinc-100">{label}</h3>
      </div>
      <div className="text-3xl font-bold text-zinc-50 mt-2">{value}</div>
      {sub && <div className="text-sm text-zinc-400">{sub}</div>}
    </div>
  );

  return onClick ? (
    <button
      onClick={onClick}
      className={`${bgClass} ${cursorClass} w-full rounded-xl`}
    >
      {cardContent}
    </button>
  ) : (
    <div className={`${bgClass} ${cursorClass} w-full rounded-xl`}>
      {cardContent}
    </div>
  );
};

interface LastRunStatusProps {
  run: DashboardStats["last_ingestion_run"];
}

const LastRunStatus: React.FC<LastRunStatusProps> = ({ run }) => {
  if (!run) return <span className="text-zinc-500">—</span>;

  if (run.status === "never") {
    return <span className="text-zinc-500">—</span>;
  }

  if (run.status === "running") {
    return (
      <div className="flex items-center gap-1 text-blue-400">
        <Loader2 className="animate-spin" size={16} />
        Running…
      </div>
    );
  }

  let colorClass = "text-emerald-400";
  let icon = <CheckCircle size={16} />;
  let text = "";

  if (run.status === "failed") {
    colorClass = "text-red-400";
    icon = <XCircle size={16} />;
    text = "Failed";
  } else {
    if (run.finished_at) {
      text = new Date(run.finished_at).toLocaleString("en-IL", {
        dateStyle: "short",
        timeStyle: "short",
      });
    } else {
      text = "Unknown";
    }
  }

  return (
    <div className={`flex items-center gap-1 ${colorClass}`}>
      {icon}
      {text}
    </div>
  );
};

const DashboardView: React.FC = () => {
  const { goToInventory, goToInventoryCfp, goToIngestionStatus } =
    useNavigationStore();
  const { isLoading: isCatalogLoading } = useConductorCatalog();
  const {
    data: stats,
    error: statsError,
    refetch,
  } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const res = await fetch("/api/dashboard/stats");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json() as Promise<DashboardStats>;
    },
    staleTime: 30_000,
    retry: 0,
  });

  const hasStats = !!stats && !statsError && !isCatalogLoading;
  const errorMsg = statsError?.message;

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-zinc-100">Mission Control</h1>
        <span className="text-sm text-zinc-400">
          Operator Console · {new Date().toLocaleDateString()}
        </span>
      </div>

      {errorMsg && (
        <div
          className="flex items-center gap-2 mb-6 px-4 py-3
                  bg-amber-900/20 border border-amber-500/30 rounded-xl text-sm"
        >
          <AlertTriangle size={14} className="text-amber-400 shrink-0" />
          <span className="text-amber-300 font-medium">
            Stats unavailable —
          </span>
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={Package}
          label="Total products"
          value={
            hasStats ? (
              stats.total_products.toLocaleString()
            ) : (
              <span className="text-zinc-600 animate-pulse">…</span>
            )
          }
          sub="Active SKUs"
          accent="blue"
          onClick={() => goToInventory()}
        />
        <MetricCard
          icon={PhoneMissed}
          label="Call for price"
          value={
            hasStats ? (
              stats.calls_for_price.toLocaleString()
            ) : (
              <span className="text-zinc-600 animate-pulse">…</span>
            )
          }
          sub="Missing IL price"
          accent={hasStats && stats.calls_for_price > 0 ? "amber" : "zinc"}
          onClick={() => goToInventoryCfp()}
        />
        <MetricCard
          icon={RefreshCcw}
          label="Active brands"
          value={
            hasStats ? (
              stats.top_brands_count.toLocaleString()
            ) : (
              <span className="text-zinc-600 animate-pulse">…</span>
            )
          }
          sub="Distinct brands in catalog"
          accent="green"
        />
        <MetricCard
          icon={RefreshCcw}
          label="Last ingestion run"
          value={
            hasStats ? (
              <LastRunStatus run={stats.last_ingestion_run} />
            ) : (
              <span className="text-zinc-600 animate-pulse">…</span>
            )
          }
          sub={
            hasStats &&
            stats.last_ingestion_run &&
            stats.last_ingestion_run.product_count !== null
              ? `${stats.last_ingestion_run.product_count} products synced`
              : "No run recorded"
          }
          accent={
            hasStats && stats.last_ingestion_run?.status === "failed"
              ? "red"
              : hasStats && stats.last_ingestion_run?.status === "running"
                ? "blue"
                : "zinc"
          }
        />
      </div>

      <div className="flex gap-4 mt-6">
        <button
          onClick={() => goToInventory()}
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg px-4 py-2"
        >
          Open Inventory Master
        </button>
        <button
          onClick={() => goToIngestionStatus()}
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg px-4 py-2"
        >
          Data Pipeline
        </button>
      </div>
    </div>
  );
};

export default DashboardView;
