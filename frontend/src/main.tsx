import React from "react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { initSovereignNerve } from "./telemetry.ts";
import App from "./App.tsx";
import "./index.css";

// ── Sovereign Nerve: self-hosted crash/error telemetry ─────────────────────
initSovereignNerve();

// Initialize React Query client with sensible defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale-While-Revalidate: Cache is valid for 5 minutes
      staleTime: 5 * 60 * 1000,
      // Keep unused data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests once
      retry: 1,
      // Refetch on window focus (e.g., user tabs back to app)
      refetchOnWindowFocus: true,
      // Refetch on network reconnection
      refetchOnReconnect: true,
    },
  },
});

const rootElement = document.getElementById("root");

if (rootElement) {
  try {
    createRoot(rootElement).render(
      <StrictMode>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </StrictMode>,
    );
  } catch (error) {
    console.error("Failed to mount React application:", error);
    rootElement.innerHTML = `
      <div style="padding: 40px; font-family: system-ui; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #ef4444;">Failed to Load Application</h1>
        <p style="color: #64748b;">Check browser console for details</p>
        <pre style="background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 8px; overflow: auto;">${error}</pre>
      </div>
    `;
  }
} else {
  console.error("Root element #root not found");
}
