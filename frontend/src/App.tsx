// frontend/src/App.tsx
/**
 * UNIFIED DATA PIPELINE v8.3
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

// Loading placeholder
const LoadingPlaceholder = () => (
  <div className="flex items-center justify-center w-full h-full text-zinc-500">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-600" />
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
        {/* Global Header */}
        <header className="h-12 bg-black border-b border-zinc-900 flex items-center justify-between px-6 z-50 relative">
          <div className="flex items-center gap-2.5 shrink-0">
            <img
              src="/assets/logos/halilit_logo.svg"
              alt="Halilit"
              className="h-6 w-auto"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
            <span className="text-zinc-600 text-xs font-mono tracking-widest">
              SC
            </span>
          </div>
          <div className="flex-1 max-w-2xl px-8 flex justify-center">
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

          {/* Screen 3: Product Page (Full Analysis View) */}
          {currentView === "PRODUCT_PAGE" && activeProductId && (
            <div className="absolute inset-0 z-50 bg-black/90 backdrop-blur-sm animate-fade-in flex items-center justify-center p-4">
              <Suspense fallback={<LoadingPlaceholder />}>
                <ProductPage productId={activeProductId} />
              </Suspense>
            </div>
          )}
        </main>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
