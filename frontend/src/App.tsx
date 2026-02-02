// frontend/src/App.tsx
import { lazy, Suspense } from "react";
import { GlobalSearch } from "./components/GlobalSearch";
import { GlobalErrorBoundary } from "./components/ui/GlobalErrorBoundary";
import { DevAgentMonitor } from "./components/DevAgentMonitor";
import { useNavigationStore } from "./store/navigationStore";
import { useCopilotReadable, useCopilotAction } from "@copilotkit/react-core";

// Lazy load heavy views for code-splitting
const GalaxyDashboard = lazy(() =>
  import("./components/views/GalaxyDashboard").then((m) => ({
    default: m.GalaxyDashboard,
  })),
);

const SpectrumModule = lazy(() =>
  import("./components/views/SpectrumModule").then((m) => ({
    default: m.default,
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
  const { currentView, activeTribeId, activeProductId } = useNavigationStore();

  // --- UI AGENT INTEGRATION ---
  useCopilotReadable({
    description: "The current state of the Halilit Support Center Dashboard",
    value: {
      currentView,
      activeTribeId,
      appVersion: "5.1",
      status: "Online",
    },
  });

  useCopilotAction({
    name: "requestAudit",
    description: "Request a full compliance audit for a specific brand",
    parameters: [
      {
        name: "brand",
        type: "string",
        description: "The brand name to audit (e.g., 'Nord', 'Roland')",
        required: true,
      },
    ],
    handler: async ({ brand }) => {
      // In a real app, this triggers the backend job
      console.log(`[UI Agent] Requesting audit for ${brand}...`);
      return `Audit requested for ${brand}. Check the logs.`;
    },
  });
  // ---------------------------

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
        </header>

        {/* Main Stage */}
        <main className="flex-1 relative overflow-hidden">
          {/* Conditional View Rendering Based on Navigation State */}
          <Suspense fallback={<LoadingPlaceholder />}>
            {currentView === "GALAXY" && (
              <div className="absolute inset-0 animate-fade-in">
                <GalaxyDashboard />
              </div>
            )}

            {currentView === "SPECTRUM" && (
              <div className="absolute inset-0 animate-fade-in">
                <SpectrumModule />
              </div>
            )}

            {currentView === "PRODUCT_POP" && activeProductId && (
              <div className="absolute inset-0 animate-fade-in">
                <ProductPopInterface productId={activeProductId} />
              </div>
            )}
          </Suspense>
        </main>

        {/* Development Agent Monitor - Only visible in dev mode */}
        <DevAgentMonitor />
      </div>
    </GlobalErrorBoundary>
  );
}

export default App;
