import React, { useCallback, useState } from "react";
import {
  LayoutGrid,
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
  Database,
  Layers,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";
import { CategorySlot } from "./galaxy/CategorySlot";
import { getContextBackground } from "../../lib/slotBackgrounds";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";

// Icon mapping for sectors
const ICON_MAP: Record<string, React.ElementType> = {
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
};

// Map Universal Categories to "Galaxy" shape
const galaxy = UNIVERSAL_CATEGORIES.map((cat) => ({
  id: cat.id,
  name: cat.label,
  icon: cat.iconName,
  iconComponent: ICON_MAP[cat.iconName] || HelpCircle,
  color: cat.color,
  children: cat.spectrum.map((sub) => {
    const bgConfig = getContextBackground(sub.id);
    return {
      id: sub.id,
      name: sub.label,
      image: bgConfig.imageUrl,
      fallbackGradient: bgConfig.fallbackGradient,
    };
  }),
}));

const BACKEND_HEALTH_TIMEOUT_MS = 6000;

export const GalaxyDashboard = () => {
  const { goToSpectrum, goToCuration } = useNavigationStore();
  const [dismissedHint, setDismissedHint] = useState(false);
  const [slowLoadShown, setSlowLoadShown] = useState(false);
  const [backendReachable, setBackendReachable] = useState<boolean | null>(null);

  // Check backend connectivity first so we don't hang on catalog fetch
  React.useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), BACKEND_HEALTH_TIMEOUT_MS);
    fetch("/api/health", { signal: controller.signal })
      .then((r) => (r.ok ? true : Promise.reject(new Error(`${r.status}`))))
      .then(() => {
        if (!cancelled) setBackendReachable(true);
      })
      .catch(() => {
        if (!cancelled) setBackendReachable(false);
      })
      .finally(() => clearTimeout(t));
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, []);

  const {
    isLoading,
    error,
    refetch,
    galaxyCounts,
    spectrumCounts,
    metadata,
  } = useConductorCatalog();

  // Show "taking a while" message after 12s so user knows first load can be slow
  React.useEffect(() => {
    if (!isLoading) {
      setSlowLoadShown(false);
      return;
    }
    const t = setTimeout(() => setSlowLoadShown(true), 12_000);
    return () => clearTimeout(t);
  }, [isLoading]);

  // Must be called unconditionally (Rules of Hooks) — before any early return
  const onSlotClick = useCallback(
    (mainId: string, subId: string) => goToSpectrum(mainId, subId, []),
    [goToSpectrum],
  );

  const isSampleOnly =
    !isLoading &&
    metadata?.brands?.length === 1 &&
    metadata.brands[0]?.toLowerCase() === "sample";

  // Full-screen when backend is unreachable
  if (backendReachable === false) {
    return (
      <div className="flex h-full bg-[#050505] text-white flex-col items-center justify-center p-8 text-center">
        <div className="max-w-md space-y-4">
          <h2 className="text-xl font-semibold text-red-400">Cannot reach server</h2>
          <p className="text-zinc-400 text-sm">
            The app could not connect to the backend. Start both servers from the project root:
          </p>
          <pre className="bg-zinc-900 border border-zinc-700 rounded-lg p-4 text-left text-sm text-zinc-300 overflow-x-auto">
            ./start.sh
          </pre>
          <p className="text-zinc-500 text-xs">
            Or run the backend on port 8000 and the frontend (e.g. npm run dev) on 5173.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded text-sm font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Brief "Connecting..." while health check is in progress
  if (backendReachable === null) {
    return (
      <div className="flex h-full bg-[#050505] text-white flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 rounded-full border-2 border-zinc-700 border-t-blue-500 animate-spin" />
        <p className="text-zinc-500 text-sm">Connecting to server…</p>
      </div>
    );
  }

  return (
    <div className="flex h-full bg-[#050505] text-white overflow-hidden relative flex-col">
      {/* Sample-only hint */}
      {isSampleOnly && !dismissedHint && (
        <div className="shrink-0 bg-blue-950/80 border-b border-blue-600/40 px-6 py-2.5 flex items-center justify-between gap-4">
          <p className="text-blue-200 text-sm">
            Showing <strong>sample data</strong>. Run{" "}
            <code className="bg-black/30 px-1 rounded font-mono text-xs">
              skeleton-sync
            </code>{" "}
            to load real products from Halilit.com.
          </p>
          <button
            type="button"
            onClick={() => setDismissedHint(true)}
            className="shrink-0 text-blue-400 hover:text-blue-300 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Error banner */}
      {error && !isLoading && (
        <div className="shrink-0 bg-amber-950/90 border-b border-amber-600/40 px-6 py-3 flex items-center justify-between gap-4">
          <p className="text-amber-200 text-sm">
            {error}
            <span className="block mt-1 text-amber-200/80 text-xs">
              Ensure backend is running: <code className="bg-black/30 px-1 rounded font-mono">./start.sh</code> or port 8000.
            </span>
          </p>
          <button
            type="button"
            onClick={() => refetch()}
            className="shrink-0 px-3 py-1.5 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-500/40 rounded text-amber-200 text-xs font-medium"
          >
            Retry
          </button>
        </div>
      )}

      {/* Header */}
      <header className="h-14 flex items-center justify-between px-6 bg-zinc-950/80 backdrop-blur-md z-10 border-b border-zinc-800/50 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
            <LayoutGrid className="w-4 h-4 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-zinc-100 font-bold tracking-wide text-lg">
            Galaxies
          </h1>
          {metadata?.total_products !== undefined && (
            <span className="text-[10px] text-zinc-500 font-medium ml-1">
              {metadata.total_products} products
            </span>
          )}
          {metadata?.graph_stats && metadata.graph_stats.total_families > 0 && (
            <span className="flex items-center gap-1 text-[10px] text-blue-400/70 font-medium ml-2 bg-blue-500/10 border border-blue-500/15 rounded-full px-2 py-0.5">
              <Layers size={10} />
              {metadata.graph_stats.total_families} families
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Catalog Health */}
          {metadata?.health_score !== undefined && (
            <div className="flex items-center gap-2 bg-zinc-900/60 border border-zinc-800/50 rounded-lg px-3 py-1.5">
              <Database className="w-3 h-3 text-zinc-500" />
              <div className="flex items-center gap-1.5">
                <div
                  className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                    metadata.health_status === "COMPLETE"
                      ? "bg-emerald-400"
                      : metadata.health_status === "GOOD"
                        ? "bg-green-400"
                        : metadata.health_status === "PARTIAL"
                          ? "bg-amber-400"
                          : "bg-red-400"
                  }`}
                />
                <span
                  className={`text-xs font-bold tabular-nums ${
                    metadata.health_status === "COMPLETE"
                      ? "text-emerald-400"
                      : metadata.health_status === "GOOD"
                        ? "text-green-400"
                        : metadata.health_status === "PARTIAL"
                          ? "text-amber-400"
                          : "text-red-400"
                  }`}
                >
                  {metadata.health_score}%
                </span>
              </div>
            </div>
          )}

          <button
            onClick={goToCuration}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-600/15 hover:bg-violet-600/30 border border-violet-500/20 rounded-lg text-violet-400 text-xs font-semibold transition-all"
            title="Product Graph Curation"
          >
            <Layers size={12} />
            Curation
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="flex-1 p-5 min-h-0 w-full h-full text-[10px] flex flex-col">
        {isLoading ? (
          <>
            <div className="grid grid-cols-3 grid-rows-2 gap-5 h-full w-full mx-auto animate-pulse">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="bg-zinc-900/50 rounded-xl border border-zinc-800/40 overflow-hidden flex flex-col"
                >
                  <div className="h-11 border-b border-zinc-800/30 bg-zinc-900/30 flex items-center gap-3 px-4">
                    <div className="w-6 h-6 rounded-lg bg-zinc-800/60" />
                    <div className="h-3 w-24 bg-zinc-800/60 rounded" />
                  </div>
                  <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start">
                    {Array.from({ length: 4 }).map((_, j) => (
                      <div
                        key={j}
                        className="aspect-square rounded-xl bg-zinc-800/30"
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
            {slowLoadShown && (
              <div className="mt-4 p-4 bg-amber-950/40 border border-amber-600/30 rounded-lg text-center shrink-0">
                <p className="text-amber-200 text-sm mb-2">
                  First load is building the catalog (7,000+ products). This can take 1–2 minutes.
                </p>
                <p className="text-amber-200/80 text-xs mb-3">
                  Ensure the backend is running: <code className="bg-black/30 px-1 rounded">./start.sh</code> or backend on port 8000.
                </p>
                <button
                  type="button"
                  onClick={() => refetch()}
                  className="px-4 py-2 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-500/40 rounded text-amber-200 text-sm font-medium"
                >
                  Retry
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="grid grid-cols-3 grid-rows-2 gap-5 h-full w-full mx-auto">
            {galaxy.map((sector, sectorIdx) => (
              <div
                key={sector.id}
                className="bg-zinc-950 rounded-xl border border-zinc-800/50 overflow-hidden flex flex-col shadow-lg hover:border-zinc-700/60 transition-colors duration-300 min-h-0"
                style={{ animationDelay: `${sectorIdx * 50}ms` }}
              >
                {/* Sector Header */}
                <div className="px-4 py-2.5 border-b border-zinc-800/40 bg-zinc-900/40 flex items-center gap-3 shrink-0 h-11">
                  <div
                    className="w-6 h-6 rounded-lg flex items-center justify-center shadow-md shrink-0"
                    style={{
                      backgroundColor: `${sector.color}20`,
                      border: `1px solid ${sector.color}40`,
                    }}
                  >
                    {React.createElement(sector.iconComponent, {
                      className: "w-3.5 h-3.5",
                      color: sector.color,
                    })}
                  </div>
                  <h2 className="font-semibold uppercase tracking-wider text-zinc-200 text-xs truncate">
                    {sector.name}
                  </h2>
                  {galaxyCounts[sector.id] !== undefined && (
                    <span className="ml-auto text-[9px] text-zinc-600 font-medium tabular-nums shrink-0">
                      {galaxyCounts[sector.id]}
                    </span>
                  )}
                </div>

                {/* Subcategory Slots */}
                <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start overflow-hidden">
                  {sector.children.map((sub) => (
                    <CategorySlot
                      key={sub.id}
                      id={sub.id}
                      name={sub.name}
                      image={sub.image}
                      fallbackGradient={sub.fallbackGradient}
                      icon={sector.iconComponent}
                      mainColor={sector.color}
                      count={
                        isLoading
                          ? undefined
                          : (spectrumCounts[sub.id] ?? 0)
                      }
                      onClick={() => onSlotClick(sector.id, sub.id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
