/**
 * Ingestion Status View — Pipeline status, refresh, and run instructions.
 * Enables operators to monitor catalog build and run the full data pipeline.
 */
import React, { useState, useEffect, useCallback } from "react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import {
  Server,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Terminal,
  Copy,
} from "lucide-react";

interface RefreshStatus {
  status: "idle" | "running" | "complete" | "failed";
  product_count?: number;
  brands?: number;
  error?: string;
  started_at?: string;
  finished_at?: string;
}

const PIPELINE_COMMANDS = `# Full pipeline (from project root, with venv activated)
PYTHONPATH=. python backend/conductor_main.py skeleton-sync          # Fast inventory (~30s)
PYTHONPATH=. python backend/conductor_main.py ingest-all             # Full: commercial → enrich → sync → graph
PYTHONPATH=. python backend/conductor_main.py rebuild-catalog        # Rebuild catalog + graph
PYTHONPATH=. python backend/scripts/prebuild_catalog_cache.py        # Prebuild cache for fast first load`;

const IngestionStatusView: React.FC = () => {
  const { totalProducts, brands, isLoading, error, refetch } = useConductorCatalog();
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchRefreshStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/conductor/refresh/status");
      const data = await res.json();
      setRefreshStatus(data);
    } catch {
      setRefreshStatus(null);
    }
  }, []);

  useEffect(() => {
    fetchRefreshStatus();
    const interval = setInterval(fetchRefreshStatus, 2000);
    return () => clearInterval(interval);
  }, [fetchRefreshStatus]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await fetch("/api/conductor/refresh?block=true");
      const data = await res.json();
      setRefreshStatus({
        status: data.error ? "failed" : "complete",
        product_count: data.product_count,
        brands: data.brands,
        error: data.error,
      });
      refetch();
    } catch (e) {
      setRefreshStatus({
        status: "failed",
        error: e instanceof Error ? e.message : "Refresh failed",
      });
    } finally {
      setRefreshing(false);
    }
  };

  const handleCopyCommands = () => {
    navigator.clipboard.writeText(PIPELINE_COMMANDS);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isRefreshRunning =
    refreshStatus?.status === "running" || refreshing;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Ingestion Status</h1>
        <p className="text-zinc-400">
          Catalog build status, refresh trigger, and pipeline run instructions.
        </p>
      </div>

      {/* Catalog Status Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Server size={18} className="text-blue-400" aria-hidden />
          Catalog Status
        </h2>
        {isLoading ? (
          <div className="flex items-center gap-3 text-zinc-400">
            <Loader2 size={20} className="animate-spin" aria-hidden />
            <span>Loading catalog…</span>
          </div>
        ) : error ? (
          <div className="flex items-start gap-3 text-amber-400">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" aria-hidden />
            <div>
              <p className="font-medium">{error}</p>
              <p className="text-sm text-zinc-500 mt-1">
                Run the pipeline or trigger Refresh below. First build can take 2–5 minutes.
              </p>
              <button
                type="button"
                onClick={() => refetch()}
                className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                Retry
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={20} className="text-emerald-500" aria-hidden />
              <span className="text-zinc-300">
                <strong className="text-white">{totalProducts.toLocaleString()}</strong> products
              </span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={20} className="text-emerald-500" aria-hidden />
              <span className="text-zinc-300">
                <strong className="text-white">{brands.length}</strong> brands
              </span>
            </div>
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-zinc-800 flex items-center gap-4">
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshRunning}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-700 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors"
          >
            {isRefreshRunning ? (
              <>
                <Loader2 size={18} className="animate-spin" aria-hidden />
                Refreshing…
              </>
            ) : (
              <>
                <RefreshCw size={18} aria-hidden />
                Refresh Catalog
              </>
            )}
          </button>
          {refreshStatus?.status === "complete" && refreshStatus.product_count != null && (
            <span className="text-sm text-zinc-500">
              Last refresh: {refreshStatus.product_count} products
            </span>
          )}
          {refreshStatus?.status === "failed" && refreshStatus.error && (
            <span className="text-sm text-amber-400">{refreshStatus.error}</span>
          )}
        </div>
      </div>

      {/* Pipeline Commands */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Terminal size={18} className="text-blue-400" aria-hidden />
          Run Full Pipeline
        </h2>
        <p className="text-sm text-zinc-400 mb-4">
          From project root. Full ingest fetches from Halilit.com and builds relationships.
          Rebuild-catalog uses existing JSONs; prebuild speeds up first browser load.
        </p>
        <pre className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 text-xs text-zinc-300 font-mono overflow-x-auto whitespace-pre-wrap">
          {PIPELINE_COMMANDS}
        </pre>
        <div className="mt-4 flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyCommands}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-medium rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors"
          >
            {copied ? (
              <>
                <CheckCircle2 size={16} aria-hidden />
                Copied
              </>
            ) : (
              <>
                <Copy size={16} aria-hidden />
                Copy Commands
              </>
            )}
          </button>
          <span className="text-sm text-zinc-500">
            See README.md for full pipeline docs
          </span>
        </div>
      </div>
    </div>
  );
};

export default IngestionStatusView;
export { IngestionStatusView };
