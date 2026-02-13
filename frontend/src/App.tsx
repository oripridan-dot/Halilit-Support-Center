// frontend/src/App.tsx
/**
 * UNIFIED DATA PIPELINE v8.5
 *
 * Three screens that share the same data source:
 * 1. GalaxyDashboard - Category browser
 * 2. SpectrumModule - Product spectrum (TierBar is integrated)
 * 3. ProductPage - Full product analysis
 *
 * All screens consume data from: useConductorCatalog (React Query)
 */
import React, { lazy, Suspense } from "react";
import { GlobalSearch } from "./components/GlobalSearch";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { Breadcrumbs } from "./components/ui/Breadcrumbs";
import { useNavigationStore } from "./store/navigationStore";
import { LearningFeed } from "./components/LearningFeed";
import { useLearningStream } from "./hooks/useLearningStream";

// Lazy load heavy views for code-splitting
const GalaxyDashboard = lazy(() =>
  import("./components/views/GalaxyDashboard").then((m) => ({
    default: m.GalaxyDashboard,
  })),
);
const SpectrumModule = lazy(() =>
  import("./components/views/SpectrumModule").then((m) => ({
    default: m.SpectrumModule,
  })),
);
const ProductPage = lazy(() =>
  import("./components/views/ProductPage").then((m) => ({
    default: m.ProductPage,
  })),
);
const CurationDashboard = lazy(() =>
  import("./components/views/CurationDashboard").then((m) => ({
    default: m.CurationDashboard,
  })),
);
const SpectrumV2 = lazy(() =>
  import("./components/spectrum/SpectrumV2").then((m) => ({
    default: m.SpectrumV2,
  })),
);

// Loading placeholder with skeleton animation
const LoadingPlaceholder = () => (
  <div className="flex items-center justify-center w-full h-full bg-black/50">
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-2 border-zinc-800" />
        <div className="absolute inset-0 rounded-full border-2 border-t-blue-500 animate-spin" />
      </div>
      <p className="text-xs text-zinc-600 font-mono tracking-widest uppercase animate-pulse">
        Loading
      </p>
    </div>
  </div>
);

function App() {
  // Extract strictly what we need
  const { currentView, activeProductId } = useNavigationStore();

  // Initialize Learning Stream listener
  useLearningStream();

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen flex-col bg-black text-white font-sans overflow-hidden">
        {/* Global Header — refined with breadcrumbs */}
        <header className="h-14 bg-black/95 backdrop-blur-md border-b border-zinc-800/60 flex items-center justify-between px-6 z-50 relative shadow-lg shadow-black/50">
          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => useNavigationStore.getState().goToGalaxy()}
              className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
              title="Go to Dashboard"
            >
              <img
                src="/assets/logos/halilit_logo.svg"
                alt="Halilit"
                className="h-6 w-auto"
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }}
              />
              <span className="text-zinc-600 text-[10px] font-mono tracking-[0.15em] uppercase">
                Support Center
              </span>
            </button>
            <div className="h-5 w-px bg-zinc-800 mx-1" />
            <Breadcrumbs />
          </div>
          <div className="flex-1 max-w-xl px-6 flex justify-end">
            <GlobalSearch />
          </div>
        </header>

        {/* Main Stage */}
        <main className="flex-1 relative overflow-hidden">
          {/* Real-time Learning Feed Overlay */}
          <LearningFeed />

          {/* Screen 1: Galaxy Dashboard */}
          {currentView === "GALAXY" && (
            <div className="absolute inset-0 animate-fade-in">
              <Suspense fallback={<LoadingPlaceholder />}>
                <GalaxyDashboard />
              </Suspense>
            </div>
          )}

          {/* Screen 2: Spectrum Module (includes TierBar/product spectrum) */}
          {currentView === "SPECTRUM" && (
            <div className="absolute inset-0 animate-slide-up">
              <Suspense fallback={<LoadingPlaceholder />}>
                <SpectrumModule />
              </Suspense>
            </div>
          )}

          {/* Screen 2b: Spectrum V2 (Redesigned with Model Grouping & Zoom) */}
          {currentView === "SPECTRUM_V2" && (
            <div className="absolute inset-0 animate-slide-up">
              <Suspense fallback={<LoadingPlaceholder />}>
                <SpectrumV2 />
              </Suspense>
            </div>
          )}

          {/* Screen 3: Product Page (Full Analysis View) */}
          {currentView === "PRODUCT_PAGE" && activeProductId && (
            <div className="absolute inset-0 z-50 bg-black/90 backdrop-blur-sm animate-fade-in flex items-center justify-center p-4">
              <Suspense fallback={<LoadingPlaceholder />}>
                <ProductPage productId={activeProductId} />
              </Suspense>
            </div>
          )}

          {/* Screen 4: Curation Dashboard (Admin) */}
          {currentView === "CURATION" && (
            <div className="absolute inset-0 animate-slide-up">
              <Suspense fallback={<LoadingPlaceholder />}>
                <CurationDashboard />
              </Suspense>
            </div>
          )}
        </main>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
