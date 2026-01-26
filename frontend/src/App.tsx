// frontend/src/App.tsx
import { lazy, Suspense } from "react";
import { GlobalSearch } from "./components/GlobalSearch";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { useNavigationStore } from "./store/navigationStore";

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
const ProductPopInterface = lazy(() =>
  import("./components/views/ProductPopInterface").then((m) => ({
    default: m.ProductPopInterface,
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

  return (
    <GlobalErrorBoundary>
      <div className="flex h-screen w-screen flex-col bg-black text-white font-sans overflow-hidden">
        {/* Global Header (Optional) */}
        <header className="h-12 bg-black border-b border-zinc-900 flex items-center justify-between px-6 z-50 relative">
          <span className="font-black italic text-lg tracking-tight shrink-0">
            Halilit<span className="text-zinc-600">SC</span>
          </span>
          <div className="flex-1 max-w-2xl px-8 flex justify-center">
            <GlobalSearch />
          </div>
          <div className="w-[80px]" /> {/* Spacer for visual balance */}
        </header>

        {/* Main Stage */}
        <main className="flex-1 relative overflow-hidden">
          {/* Layer 1: Galaxy */}
          {currentView === "GALAXY" && (
            <div className="absolute inset-0 animate-fade-in">
              <Suspense fallback={<LoadingPlaceholder />}>
                <GalaxyDashboard />
              </Suspense>
            </div>
          )}

          {/* Layer 2: Spectrum */}
          {currentView === "SPECTRUM" && (
            <div className="absolute inset-0 animate-slide-up">
              <Suspense fallback={<LoadingPlaceholder />}>
                <SpectrumModule />
              </Suspense>
            </div>
          )}

          {/* Layer 3: Product Pop (Overlay) */}
          {currentView === "PRODUCT_POP" && activeProductId && (
            <div className="absolute inset-0 z-50 bg-black/90 backdrop-blur-sm animate-fade-in flex items-center justify-center p-4">
              <Suspense fallback={<LoadingPlaceholder />}>
                <ProductPopInterface productId={activeProductId} />
              </Suspense>
            </div>
          )}
        </main>
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
