import React from 'react';
import { AlertTriangle, CheckCircle, Loader2, XCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useNavigationStore } from '../../store/navigationStore';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';

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

interface MetricCardProps {
  icon: React.ComponentType;
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  accent: "blue" | "amber" | "green" | "red" | "zinc";
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon: Icon, label, value, sub, accent, onClick }) => {
  const accentColors: Record<string, string> = {
    blue: 'bg-blue-100/10 text-blue-500',
    amber: 'bg-amber-100/10 text-amber-500',
    green: 'bg-green-100/10 text-green-500',
    red: 'bg-red-100/10 text-red-500',
    zinc: 'bg-zinc-100/10 text-zinc-500',
  };
  const accentClasses = accentColors[accent] || '';

  return (
    <div className="flex flex-col gap-2 p-4 rounded-xl bg-bg-elevated hover:bg-zinc-800 transition-colors touch-target" onClick={onClick} style={onClick ? { cursor: 'pointer' } : {}}>
      <div className="flex items-center justify-between">
        <div className={`p-2 rounded-md ${accentClasses}`}>
          <Icon size={20} />
        </div>
      </div>
      <div className="text-sm text-text-secondary">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
      {sub && <div className="text-xs text-text-muted">{sub}</div>}
    </div>
  );
};

const LastRunStatus: React.FC<{ run: DashboardStats['last_ingestion_run'] }> = ({ run }) => {
  if (run.status === 'never') {
    return <span className="text-zinc-500">—</span>;
  }
  if (run.status === 'running') {
    return (
      <>
        <Loader2 size={16} className="inline mr-1 animate-spin text-blue-400" />
        <span className="text-blue-400">Running...</span>
      </>
    );
  }
  if (run.status === 'complete' || run.status === 'unknown') {
    return (
      <>
        <CheckCircle size={16} className="inline mr-1 text-emerald-400" />
        {new Date(run.finished_at!).toLocaleString("en-IL", { dateStyle: "short", timeStyle: "short" })}
      </>
    );
  }
  if (run.status === 'failed') {
    return (
      <>
        <XCircle size={16} className="inline mr-1 text-red-400" />
        <span className="text-red-400">Failed</span>
      </>
    );
  }
  return <span className="text-zinc-500">—</span>;
};


const useDashboardStats = () => {
    const query = useQuery({
        queryKey: ['dashboardStats'],
        queryFn: async () => {
            const res = await fetch('/api/dashboard/stats');
            const text = await res.text();
            if (text.startsWith('<')) {
                throw new Error('Backend is unavailable');
            }
            if (!res.ok) {
                const json = await res.json();
                throw new Error(json.error || 'Failed to fetch dashboard stats');
            }
            return JSON.parse(text) as DashboardStats;
        },
        staleTime: 30_000,
        retry: 0,
    });

    return {
        ...query,
        stats: query.data,
        errorMsg: query.error?.message,
    };
};

const DashboardView: React.FC = () => {
  const { goToInventory, goToInventoryCfp, goToIngestionStatus } = useNavigationStore();
  const { stats, errorMsg, isLoading, refetch } = useDashboardStats();
  const { isLoading: isCatalogLoading } = useConductorCatalog();
  const hasStats = !!stats && !errorMsg;

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  return (
    <div className="p-6">
      <header className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-semibold">Mission Control</h1>
        <p className="text-sm text-text-muted">{today}</p>
      </header>

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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-4 mb-8">
        <MetricCard
          icon={React.lazy(() => import('lucide-react').then(mod => ({ default: mod.Package }))) as React.ComponentType}
          label="Total products"
          value={hasStats ? stats.total_products.toLocaleString() : <span className="text-zinc-600 animate-pulse">…</span>}
          sub="Active SKUs"
          accent="blue"
          onClick={() => goToInventory()}
        />
        <MetricCard
          icon={React.lazy(() => import('lucide-react').then(mod => ({ default: mod.Phone }))) as React.ComponentType}
          label="Call for price"
          value={hasStats ? stats.calls_for_price.toLocaleString() : <span className="text-zinc-600 animate-pulse">…</span>}
          sub="Missing IL price"
          accent={hasStats && stats.calls_for_price > 0 ? 'amber' : 'zinc'}
          onClick={() => goToInventoryCfp()}
        />
        <MetricCard
          icon={React.lazy(() => import('lucide-react').then(mod => ({ default: mod.Briefcase }))) as React.ComponentType}
          label="Active brands"
          value={hasStats ? stats.top_brands_count.toLocaleString() : <span className="text-zinc-600 animate-pulse">…</span>}
          sub="Distinct brands in catalog"
          accent="green"
        />
        <MetricCard
          icon={React.lazy(() => import('lucide-react').then(mod => ({ default: mod.Clock }))) as React.ComponentType}
          label="Last ingestion run"
          value={hasStats ? <LastRunStatus run={stats.last_ingestion_run} /> : <span className="text-zinc-600 animate-pulse">…</span>}
          sub={
              hasStats && stats.last_ingestion_run.status !== 'never'
              ? `${stats.last_ingestion_run.product_count?.toLocaleString() || 0} products synced`
              : "No run recorded"
          }
          accent={
              hasStats
                ? stats.last_ingestion_run.status === 'failed'
                  ? 'red'
                  : stats.last_ingestion_run.status === 'running'
                  ? 'blue'
                  : 'zinc'
                : 'zinc'
            }
        />
      </div>

      <div className="flex gap-4">
        <button className="px-4 py-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-text-primary transition-colors" onClick={() => goToInventory()}>Open Inventory Master</button>
        <button className="px-4 py-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-text-primary transition-colors" onClick={() => goToIngestionStatus()}>Data Pipeline</button>
      </div>
    </div>
  );
};

export default DashboardView;